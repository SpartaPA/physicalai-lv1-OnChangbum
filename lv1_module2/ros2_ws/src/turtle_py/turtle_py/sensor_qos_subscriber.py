# 초기 기동 시 Reliable 프로파일을 강제 적용하도록 설계하여 Best-Effort 발행자와의 QoS 비호환(Incompatibility) 통신 단절 현상을 의도적으로 유도합니다. 이후 파라미터(use_best_effort) 제어를 통해 런타임에 동적으로 프로파일을 수정하여 정상 복구하도록 구성되어 있습니다.
#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from std_msgs.msg import Float32
from rcl_interfaces.msg import SetParametersResult
from rclpy.parameter import Parameter

class SensorQosSubscriber(Node):
    def __init__(self):
        super().__init__('turtle_sensor_qos_subscriber')
        
        # use_best_effort 파라미터 선언 (기본값 False -> 초기 Reliable 모드로 비호환 유도)
        self.declare_parameter('use_best_effort', False)
        self.use_best_effort = self.get_parameter('use_best_effort').get_parameter_value().bool_value
        
        self.subscription = None
        self.setup_subscriber()
        
        # 동적 파라미터 변경 콜백 등록 (복구 실험용)
        self.add_on_set_parameters_callback(self.parameter_callback)
        self.get_logger().info("Sensor QoS Subscriber Initialized. Initial Policy: RELIABLE")

    def setup_subscriber(self):
        # 기존 구독 관계가 있으면 안전하게 파괴
        if self.subscription:
            self.destroy_subscription(self.subscription)
            
        # 파라미터 상태에 따라 QoS 프로파일 동적 결정
        if self.use_best_effort:
            policy = ReliabilityPolicy.BEST_EFFORT
            policy_str = "BEST_EFFORT"
        else:
            policy = ReliabilityPolicy.RELIABLE
            policy_str = "RELIABLE"
            
        qos_profile = QoSProfile(
            reliability=policy,
            history=HistoryPolicy.KEEP_LAST,
            depth=10
        )
        
        self.subscription = self.create_subscription(
            Float32,
            '/sensor_data',
            self.listener_callback,
            qos_profile
        )
        self.get_logger().info(f"Subscriber QoS Reliability Policy applied: {policy_str}")

    def listener_callback(self, msg):
        self.get_logger().info(f"Received High-Freq Sensor Data: [{msg.data:.4f}]")

    def parameter_callback(self, params):
        for param in params:
            if param.name == 'use_best_effort' and param.type_ == Parameter.Type.BOOL:
                new_val = param.value
                if new_val != self.use_best_effort:
                    self.use_best_effort = new_val
                    self.get_logger().info(f"Parameter updated! Re-configuring subscriber QoS...")
                    self.setup_subscriber()
                    
        return SetParametersResult(successful=True)

def main(args=None):
    rclpy.init(args=args)
    node = SensorQosSubscriber()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
