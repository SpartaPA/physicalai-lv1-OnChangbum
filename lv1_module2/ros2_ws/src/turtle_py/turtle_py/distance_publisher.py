#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
import math

from turtlesim.msg import Pose
from std_msgs.msg import Float32
from rcl_interfaces.msg import SetParametersResult
from rclpy.parameter import Parameter

class DistancePublisher(Node):
    def __init__(self):
        super().__init__('turtle_distance_publisher')
        
        # publish_rate 파라미터 선언 및 초기화 (기본값: 10.0 Hz)
        self.declare_parameter('publish_rate', 10.0)
        self.current_rate = self.get_parameter('publish_rate').get_parameter_value().double_value
        
        # 최신 위치 보관 변수
        self.current_pose = None
        
        # Publisher & Subscriber 구성
        self.publisher_ = self.create_publisher(Float32, '/turtle_distance', 10)
        self.subscription = self.create_subscription(
            Pose,
            '/turtle1/pose',
            self.pose_callback,
            10
        )
        
        # 10Hz 기본 타이머 생성
        timer_period = 1.0 / self.current_rate
        self.timer = self.create_timer(timer_period, self.timer_callback)
        
        # 동적 파라미터 변경 콜백 등록
        self.add_on_set_parameters_callback(self.parameter_callback)
        self.get_logger().info("Distance Publisher Node Initialized.")

    def pose_callback(self, msg):
        # 최신 포즈를 보관만 수행
        self.current_pose = msg

    def timer_callback(self):
        if self.current_pose is None:
            return
            
        # 원점(0,0)으로부터 현재 거북이 위치(x,y)까지의 직선 거리 계산
        distance = math.hypot(self.current_pose.x, self.current_pose.y)
        
        # 토픽 발행
        msg = Float32()
        msg.data = distance
        self.publisher_.publish(msg)

    def parameter_callback(self, params):
        for param in params:
            if param.name == 'publish_rate' and param.type_ == Parameter.Type.DOUBLE:
                new_rate = param.value
                if new_rate <= 0.0:
                    return SetParametersResult(successful=False, reason="Publish rate must be positive.")
                
                if new_rate != self.current_rate:
                    self.get_logger().info(f"Publish rate changed: {self.current_rate} -> {new_rate} Hz")
                    self.current_rate = new_rate
                    self.destroy_timer(self.timer)
                    self.timer = self.create_timer(1.0 / self.current_rate, self.timer_callback)
                    
        return SetParametersResult(successful=True)

def main(args=None):
    rclpy.init(args=args)
    node = DistancePublisher()
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

