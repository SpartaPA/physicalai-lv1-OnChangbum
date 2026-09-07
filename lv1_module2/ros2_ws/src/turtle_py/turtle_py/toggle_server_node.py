# 주행을 On/Off 시키는 std_srvs/srv/SetBool 서버와, 홈 위치 저장 및 복귀를 관장하는 std_srvs/srv/Trigger 서비스 서버를 구현하여 콜백 데드락을 방지하는 비동기 패턴으로 설계되었습니다.
#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
import math
from std_msgs.msg import Float32
from turtlesim.msg import Pose
from std_srvs.srv import SetBool, Trigger
from turtlesim.srv import TeleportAbsolute

class ToggleServerNode(Node):
    def __init__(self):
        super().__init__('turtle_toggle_server')
        
        # 상태 변수
        self.enable_driving = True
        self.home_pose = None
        self.current_pose = None
        
        # Pub/Sub 구성
        self.publisher_ = self.create_publisher(Float32, '/turtle_distance', 10)
        self.subscription = self.create_subscription(Pose, '/turtle1/pose', self.pose_callback, 10)
        self.timer = self.create_timer(0.1, self.timer_callback)
        
        # 1. /enable_driving 서비스 서버 생성 (주행 허가 제어)
        self.srv_driving = self.create_service(SetBool, '/enable_driving', self.handle_enable_driving)
        
        # 2. /save_home 서비스 서버 생성 (현재 위치 홈 세이브)
        self.srv_save_home = self.create_service(Trigger, '/save_home', self.handle_save_home)
        
        # 3. /go_home 서비스 서버 생성 (홈으로 순간이동 - 데드락 방지 비동기 트리거 방식)
        self.srv_go_home = self.create_service(Trigger, '/go_home', self.handle_go_home)
        
        # 다른 서비스용 비동기 클라이언트
        self.teleport_client = self.create_client(TeleportAbsolute, '/turtle1/teleport_absolute')
        
        self.get_logger().info("Toggle Servers Node with Distance Publisher Initialized.")

    def pose_callback(self, msg):
        self.current_pose = msg

    def timer_callback(self):
        if self.current_pose is None or not self.enable_driving:
            return
        distance = math.hypot(self.current_pose.x, self.current_pose.y)
        msg = Float32()
        msg.data = distance
        self.publisher_.publish(msg)

    def handle_enable_driving(self, request, response):
        self.enable_driving = request.data
        response.success = True
        response.message = f"Driving enable status set to: {self.enable_driving}"
        self.get_logger().info(response.message)
        return response

    def handle_save_home(self, request, response):
        if self.current_pose is None:
            response.success = False
            response.message = "Failed to save home: Pose dataset empty."
        else:
            self.home_pose = self.current_pose
            response.success = True
            response.message = f"Saved current position as Home: ({self.home_pose.x:.2f}, {self.home_pose.y:.2f})"
        self.get_logger().info(response.message)
        return response

    def handle_go_home(self, request, response):
        if self.home_pose is None:
            response.success = False
            response.message = "Failed: No saved home coordinates."
            return response
            
        # ★ 데드락 예방 패턴: 콜백 내부에서 동기 대기하지 않고 비동기(create_task)로 양도 실행
        self.create_task(self.async_go_home_call())
        response.success = True
        response.message = "Go Home teleport request triggered in non-blocking loop."
        return response

    async def async_go_home_call(self):
        while not self.teleport_client.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for /turtle1/teleport_absolute service...')
        
        req = TeleportAbsolute.Request()
        req.x = self.home_pose.x
        req.y = self.home_pose.y
        req.theta = self.home_pose.theta
        self.get_logger().info("Sending Teleport Request to Saved Home Position...")
        await self.teleport_client.call_async(req)
        self.get_logger().info("Teleportation to Home completed successfully.")

def main(args=None):
    rclpy.init(args=args)
    node = ToggleServerNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
