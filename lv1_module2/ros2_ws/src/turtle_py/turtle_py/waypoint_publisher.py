# 과제 6·7번 규격 연동을 위해 WaypointList.msg 타입을 활용해 헤더와 중첩 배열 필드 데이터 4개를 채워 /waypoints 토픽으로 유일하게 발행합니다.
#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, DurabilityPolicy

from std_msgs.msg import Header
from turtle_interfaces.msg import Waypoint, WaypointList

class WaypointPublisher(Node):
    def __init__(self):
        super().__init__('turtle_waypoint_publisher')
        
        # 문제 7번 late-join 수신 검증용 고정 규격: TRANSIENT_LOCAL 설정
        qos_profile = QoSProfile(depth=1)
        qos_profile.durability = DurabilityPolicy.TRANSIENT_LOCAL
        
        self.publisher_ = self.create_publisher(WaypointList, '/waypoints', qos_profile)
        self.timer = self.create_timer(2.0, self.timer_callback)
        self.get_logger().info("Waypoint Transient Local Publisher Initialized.")

    def timer_callback(self):
        msg = WaypointList()
        
        # Header 데이터 빌드
        msg.header = Header()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'world'
        
        # 고정 경유점 4개 명세 배열 생성 연동
        w1 = Waypoint(x=2.0, y=2.0, tolerance=0.1, label='Waypoint_A')
        w2 = Waypoint(x=8.0, y=2.0, tolerance=0.1, label='Waypoint_B')
        w3 = Waypoint(x=8.0, y=8.0, tolerance=0.1, label='Waypoint_C')
        w4 = Waypoint(x=2.0, y=8.0, tolerance=0.1, label='Waypoint_D')
        
        msg.waypoints = [w1, w2, w3, w4]
        
        self.publisher_.publish(msg)
        self.get_logger().info("Published WaypointList with 4 coordinates.")

def main(args=None):
    rclpy.init(args=args)
    node = WaypointPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
