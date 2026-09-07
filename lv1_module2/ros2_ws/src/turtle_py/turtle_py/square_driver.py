#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
import math

from geometry_msgs.msg import Twist
from turtlesim.msg import Pose

class SquareDriver(Node):
    def __init__(self):
        super().__init__('turtle_square_driver')
        
        self.cmd_vel_pub = self.create_publisher(Twist, '/turtle1/cmd_vel', 10)
        self.pose_sub = self.create_subscription(Pose, '/turtle1/pose', self.pose_callback, 10)
        
        # 지터 영향을 최소화하기 위해 주기를 100Hz(0.01초)로 극대화
        self.timer = self.create_timer(0.01, self.control_loop)
        
        self.current_pose = None
        self.start_pose = None
        
        self.state = 'INIT'
        self.current_side = 0
        self.target_sides = 4
        
        # 주행 속도 안정화
        self.linear_speed = 1.0   # m/s
        self.max_angular_speed = 0.5  # 최대 회전 속도 (rad/s)
        self.side_length = 2.5    # m
        self.target_angle = math.pi / 2.0  # 정확한 90도 (1.5708 rad)
        
        self.get_logger().info("Square Driver Node Initialized. Starting precision trajectory.")

    def pose_callback(self, msg):
        self.current_pose = msg

    def control_loop(self):
        if self.current_pose is None:
            return

        twist = Twist()

        if self.state == 'INIT':
            self.start_pose = self.current_pose
            self.state = 'GO_STRAIGHT'
            self.get_logger().info(f"[Side {self.current_side + 1}] Driving Straight...")

        elif self.state == 'GO_STRAIGHT':
            moved_distance = math.hypot(
                self.current_pose.x - self.start_pose.x,
                self.current_pose.y - self.start_pose.y
            )
            
            if moved_distance < self.side_length:
                twist.linear.x = self.linear_speed
                twist.angular.z = 0.0
            else:
                twist.linear.x = 0.0
                self.start_pose = self.current_pose
                self.state = 'TURN'
                self.get_logger().info(f"[Side {self.current_side + 1}] Turning 90 Degrees...")

        elif self.state == 'TURN':
            # 상대 회전각 계산 및 -pi ~ pi 정규화
            angle_diff = self.current_pose.theta - self.start_pose.theta
            while angle_diff > math.pi: angle_diff -= 2.0 * math.pi
            while angle_diff < -math.pi: angle_diff += 2.0 * math.pi
            
            # 남은 각도 계산
            remaining_angle = self.target_angle - abs(angle_diff)
            
            # 칼같은 직각을 위한 비례 감속 제어 (남은 각도가 줄어들수록 속도를 0.05까지 부드럽게 감속)
            if remaining_angle > 0.005:  # 매우 엄격한 목표 오차 허용 경계값 (약 0.2도)
                twist.linear.x = 0.0
                # 남은 각도에 비례하여 속도 결정 (최소 속도 0.08 보장하여 멈춤 방지)
                p_speed = remaining_angle * 1.5
                twist.angular.z = max(0.08, min(self.max_angular_speed, p_speed))
            else:
                # 회전 정지 및 다음 상태 전입
                twist.angular.z = 0.0
                self.current_side += 1
                
                if self.current_side < self.target_sides:
                    self.start_pose = self.current_pose
                    self.state = 'GO_STRAIGHT'
                    self.get_logger().info(f"[Side {self.current_side + 1}] Driving Straight...")
                else:
                    self.state = 'DONE'
                    self.get_logger().info("Square trajectory completed perfectly.")

        elif self.state == 'DONE':
            twist.linear.x = 0.0
            twist.angular.z = 0.0

        self.cmd_vel_pub.publish(twist)

def main(args=None):
    rclpy.init(args=args)
    node = SquareDriver()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()
