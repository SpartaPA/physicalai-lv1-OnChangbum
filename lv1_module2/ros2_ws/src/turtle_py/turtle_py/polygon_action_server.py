#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.action import ActionServer, CancelResponse, GoalResponse
from rclpy.callback_groups import ReentrantCallbackGroup
from rclpy.executors import MultiThreadedExecutor
import math
import time

from geometry_msgs.msg import Twist
from turtlesim.msg import Pose
from turtle_interfaces.action import DrawPolygon

class PolygonActionServer(Node):
    def __init__(self):
        super().__init__('turtle_polygon_action_server')
        
        self.cmd_vel_pub = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.pose_sub = self.create_subscription(Pose, '/turtle1/pose', self.pose_callback, 10)
        
        self.current_pose = None
        
        # 액션 제어 동시성 확보를 위한 멀티스레드 콜백 그룹 세팅 (★취소 인터럽트 강제 인입용)
        self.callback_group = ReentrantCallbackGroup()
        
        self.action_server = ActionServer(
            self,
            DrawPolygon,
            '/draw_polygon',
            execute_callback=self.execute_callback,
            goal_callback=self.goal_callback,
            cancel_callback=self.cancel_callback,
            callback_group=self.callback_group
        )
        self.get_logger().info("Polygon Action Server Initialized. Ready for /draw_polygon goals.")

    def pose_callback(self, msg):
        self.current_pose = msg

    def goal_callback(self, goal_request):
        self.get_logger().info(f"Received Goal Request: sides={goal_request.sides}, length={goal_request.side_length}")
        if goal_request.sides < 3:
            self.get_logger().warn("Rejected: Polygon sides must be 3 or more.")
            return GoalResponse.REJECT

        # 주행 전 중앙 복귀 수동 유도 알림
        self.get_logger().info("Goal Accepted. Please ensure turtlesim is cleared and centered to avoid wall crash.")
        return GoalResponse.ACCEPT

    def cancel_callback(self, goal_handle):
        self.get_logger().info("Received Action Cancel Request from Client.")
        return CancelResponse.ACCEPT

    def execute_callback(self, goal_handle):
        self.get_logger().info("Executing polygon drawing trajectory...")
        
        sides = goal_handle.request.sides
        side_length = goal_handle.request.side_length
        
        feedback_msg = DrawPolygon.Feedback()
        result = DrawPolygon.Result()
        
        total_distance = 0.0
        target_turn_angle = (2.0 * math.pi) / sides  # 외각 공식 계산 (90도 고정이 아님)
        
        # 제어 주기 규칙 세팅 (50Hz)
        loop_rate = self.create_rate(50)
        twist = Twist()

        for side in range(sides):
            # 실시간 취소 인입 체크 메커니즘
            if goal_handle.is_cancel_requested:
                twist.linear.x = 0.0
                twist.angular.z = 0.0
                self.cmd_vel_pub.publish(twist)
                goal_handle.canceled()
                self.get_logger().info(f"Action drawing completely CANCELED at side {side+1}.")
                result.total_distance = total_distance
                return result

            # --- 1. 직진 시퀀스 구동 ---
            while self.current_pose is None:
                time.sleep(0.01)
                
            start_pose = self.current_pose
            moved_distance = 0.0
            
            self.get_logger().info(f"[Side {side + 1}/{sides}] Driving straight...")
            while moved_distance < side_length:
                if goal_handle.is_cancel_requested:
                    break
                twist.linear.x = 1.0  # 부드러운 속도 세팅
                twist.angular.z = 0.0
                self.cmd_vel_pub.publish(twist)
                
                loop_rate.sleep()
                moved_distance = math.hypot(
                    self.current_pose.x - start_pose.x,
                    self.current_pose.y - start_pose.y
                )
            
            total_distance += moved_distance
            twist.linear.x = 0.0
            self.cmd_vel_pub.publish(twist)

            if goal_handle.is_cancel_requested:
                continue

            # --- 2. 제동 비례 감속 회전 시퀀스 구동 ---
            start_pose = self.current_pose
            rotated_angle = 0.0
            
            self.get_logger().info(f"[Side {side + 1}/{sides}] Turning precise angle...")
            while True:
                if goal_handle.is_cancel_requested:
                    break
                    
                angle_diff = self.current_pose.theta - start_pose.theta
                while angle_diff > math.pi: angle_diff -= 2.0 * math.pi
                while angle_diff < -math.pi: angle_diff += 2.0 * math.pi
                rotated_angle = abs(angle_diff)
                
                remaining_angle = target_turn_angle - rotated_angle
                if remaining_angle <= 0.02:  # 정밀 경계오차 세팅
                    break
                    
                twist.linear.x = 0.0
                # 비례 감속 제어 연동으로 오버슈트 비정형 궤적 왜곡 영구 박멸
                p_speed = remaining_angle * 1.5
                twist.angular.z = max(0.1, min(0.5, p_speed))
                self.cmd_vel_pub.publish(twist)
                loop_rate.sleep()
                
            twist.angular.z = 0.0
            self.cmd_vel_pub.publish(twist)
            
            # --- 3. 피드백 전송 시퀀스 구동 ---
            feedback_msg.completed_sides = side + 1
            feedback_msg.progress = (side + 1) / sides
            goal_handle.publish_feedback(feedback_msg)
            self.get_logger().info(f"Feedback Sent: completed={side+1}, progress={feedback_msg.progress:.2f}")

        # 모든 변 주행 완수 시 석세스 마감
        goal_handle.succeed()
        self.get_logger().info("Polygon drawing trajectory completed perfectly.")
        result.total_distance = total_distance
        return result

def main(args=None):
    rclpy.init(args=args)
    node = PolygonActionServer()
    
    # 동시 취소 멀티 콜백 처리를 위해 멀티스레드 익스큐터 장착 구동
    executor = MultiThreadedExecutor()
    executor.add_node(node)
    try:
        executor.spin()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
