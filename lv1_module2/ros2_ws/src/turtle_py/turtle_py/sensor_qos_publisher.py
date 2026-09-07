# 과제 요구 명세에 맞춰 고주파수 가상 주행 센서 데이터를 Best-Effort 신뢰성(Reliability) 프로파일 정책으로 설정하여 /sensor_data 토픽으로 발행합니다.
#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from std_msgs.msg import Float32
import random

class SensorQosPublisher(Node):
    def __init__(self):
        super().__init__('turtle_sensor_qos_publisher')
        
        # 과제 요구 고정 규격: Best-Effort 프로파일 세팅
        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=10
        )
        
        self.publisher_ = self.create_publisher(Float32, '/sensor_data', qos_profile)
        self.timer = self.create_timer(0.05, self.timer_callback)  # 고주파수 20Hz 발행
        self.get_logger().info("Sensor QoS Publisher Initialized with BEST_EFFORT policy.")

    def timer_callback(self):
        msg = Float32()
        # 0.0 ~ 1.0 사이의 가상 센서 노이즈 데이터 생성
        msg.data = random.random()
        self.publisher_.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = SensorQosPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
