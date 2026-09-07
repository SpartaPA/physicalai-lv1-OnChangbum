# /turtle1/rotate_absolute 액션 서버로 목표 각도를 전송하고 피드백(remaining)을 실시간 수집하며, 지정한 타이밍 뒤에 cancel_goal 취소 명령을 날려 강제 차단 제어를 수행합니다.
#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.action import ActionClient
from turtlesim.action import RotateAbsolute
import argparse

class RotateActionClient(Node):
    def __init__(self, target_theta, cancel_after):
        super().__init__('rotate_action_client')
        self.target_theta = target_theta
        self.cancel_after = cancel_after
        self.goal_handle = None
        self.cancel_timer = None
        
        self.action_client = ActionClient(self, RotateAbsolute, '/turtle1/rotate_absolute')
        self.get_logger().info("Rotate Absolute Action Client Initialized.")
        
        # 1초 타이머 콜백으로 액션 서버 대기 및 실행 트리거 (데드락 방지 정석)
        self.init_timer = self.create_timer(0.5, self.check_server_and_send)

    def check_server_and_send(self):
        if not self.action_client.wait_for_server(timeout_sec=0.1):
            self.get_logger().info('Waiting for action server /turtle1/rotate_absolute...')
            return
            
        # 서버가 준비되면 기동 타이머 파괴 후 목표 송신
        self.destroy_timer(self.init_timer)
        
        goal_msg = RotateAbsolute.Goal()
        goal_msg.theta = self.target_theta

        self.get_logger().info(f'Sending Action Goal: Theta = {self.target_theta} rad')
        
        # 비동기 전송 후 콜백 핸들러 연결 (스레드 충돌 원천 차단)
        send_goal_future = self.action_client.send_goal_async(
            goal_msg, feedback_callback=self.feedback_callback)
        send_goal_future.add_done_callback(self.goal_response_callback)

    def goal_response_callback(self, future):
        self.goal_handle = future.result()
        if not self.goal_handle.accepted:
            self.get_logger().info('Goal Rejected by Server.')
            rclpy.shutdown()
            return

        self.get_logger().info('Goal Accepted by Server.')

        # 수강생님이 지정하신 타이밍 뒤에 취소 요청을 날릴 1회성 타이머 가동
        if self.cancel_after > 0.0:
            self.get_logger().info(f'Scheduling cancel request in {self.cancel_after} seconds...')
            self.cancel_timer = self.create_timer(self.cancel_after, self.cancel_goal_callback)

        # 결과 대기 퓨처 콜백 연결
        result_future = self.goal_handle.get_result_async()
        result_future.add_done_callback(self.get_result_callback)

    def feedback_callback(self, feedback_msg):
        feedback = feedback_msg.feedback
        self.get_logger().info(f'Feedback received - Remaining Orientation Angle: {feedback.remaining:.4f} rad')

    def cancel_goal_callback(self):
        # 타이머 중복 실행 방지를 위한 즉각 소멸
        if self.cancel_timer:
            self.destroy_timer(self.cancel_timer)
            self.cancel_timer = None
            
        self.get_logger().info('Sending Cancel Request to Action Server now...')
        if self.goal_handle is not None:
            self.goal_handle.cancel_goal_async()

    def get_result_callback(self, future):
        result_res = future.result()
        status = result_res.status
        
        if status == 4:  # STATUS_SUCCEEDED
            self.get_logger().info(f'Action Goal Succeeded! Result Delta Theta: {result_res.result.delta:.4f}')
        elif status == 5:  # STATUS_CANCELED
            self.get_logger().info('Action Goal Successfully CANCELED on fly.')
            
        # 프로세스 깔끔하게 종료
        rclpy.shutdown()

def main(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--theta', type=float, default=3.14)
    parser.add_argument('--cancel-after', type=float, default=0.0)
    parsed_args, unknown = parser.parse_known_args()

    rclpy.init(args=args)
    node = RotateActionClient(target_theta=parsed_args.theta, cancel_after=parsed_args.cancel_after)
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        # 노드가 정상 종료 플래그 상태일 때만 안전 반환
        if rclpy.ok():
            node.destroy_node()
            rclpy.shutdown()

if __name__ == '__main__':
    main()
