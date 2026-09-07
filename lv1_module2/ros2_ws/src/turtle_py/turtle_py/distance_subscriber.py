#!/usr/bin/env python3
import rclpy
from rclpy.node import Node

from std_msgs.msg import Float32
from rcl_interfaces.msg import SetParametersResult

class DistanceSubscriber(Node):
    def __init__(self):
        super().__init__('turtle_distance_subscriber')
        
        # warn_distance 파라미터 선언 및 초기화 (기본값: 2.5)
        self.declare_parameter('warn_distance', 2.5)
        self.warn_threshold = self.get_parameter('warn_distance').get_parameter_value().double_value
        
        # /turtle_distance 토픽 구독
        self.subscription = self.create_subscription(
            Float32,
            '/turtle_distance',
            self.distance_callback,
            10
        )
        
        # 동적 파라미터 변경 콜백 등록
        self.add_on_set_parameters_callback(self.parameter_callback)
        self.get_logger().info("Distance Subscriber Node Initialized.")

    def distance_callback(self, msg):
        current_distance = msg.data
        # 임계값을 초과하는 주행 시 rclpy 경고 로그 유도
        if current_distance > self.warn_threshold:
            self.get_logger().warn(
                f"WARN: Turtle distance ({current_distance:.2f}m) exceeded threshold ({self.warn_threshold:.2f}m)!"
            )

    def parameter_callback(self, params):
        for param in params:
            if param.name == 'warn_distance' and param.type_ == param.Type.DOUBLE:
                new_threshold = param.value
                if new_threshold < 0.0:
                    return SetParametersResult(successful=False, reason="Warning distance cannot be negative.")
                
                self.get_logger().info(f"Warning distance threshold changed: {self.warn_threshold} -> {new_threshold}")
                self.warn_threshold = new_threshold
                
        return SetParametersResult(successful=True)

def main(args=None):
    rclpy.init(args=args)
    node = DistanceSubscriber()
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