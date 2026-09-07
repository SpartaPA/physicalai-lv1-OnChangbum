# /turtle1/set_pen(펜 변경) ➔ /spawn(거북이 추가) ➔ /turtle1/teleport_absolute(순간이동) ➔ /clear(궤적 지우기)를 call_async와 비동기 루프로 순차 호출합니다.
#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
import sys

from turtlesim.srv import TeleportAbsolute, SetPen, Spawn
from std_srvs.srv import Empty

class BuiltinServiceClient(Node):
    def __init__(self):
        super().__init__('builtin_service_client')
        self.get_logger().info("Builtin Service Client Node Initialized.")

    def run_sequence(self):
        # 1. /turtle1/set_pen 클라이언트 호출
        pen_cli = self.create_client(SetPen, '/turtle1/set_pen')
        while not pen_cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for /turtle1/set_pen service...')
        
        req_pen = SetPen.Request()
        req_pen.r, req_pen.g, req_pen.b, req_pen.width, req_pen.off = 255, 0, 0, 5, 0
        self.get_logger().info('Calling /turtle1/set_pen (Red, Width: 5)...')
        future = pen_cli.call_async(req_pen)
        rclpy.spin_until_future_complete(self, future)

        # 2. /spawn 클라이언트 호출 (turtle2 생성)
        spawn_cli = self.create_client(Spawn, '/spawn')
        while not spawn_cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for /spawn service...')
            
        req_spawn = Spawn.Request()
        req_spawn.x, req_spawn.y, req_spawn.theta, req_spawn.name = 2.0, 2.0, 0.0, 'turtle2'
        self.get_logger().info('Calling /spawn (name: turtle2 at 2.0, 2.0)...')
        future = spawn_cli.call_async(req_spawn)
        rclpy.spin_until_future_complete(self, future)
        res_spawn = future.result()
        self.get_logger().info(f'Spawned successful: {res_spawn.name}')

        # 3. /turtle1/teleport_absolute 클라이언트 호출
        teleport_cli = self.create_client(TeleportAbsolute, '/turtle1/teleport_absolute')
        while not teleport_cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for /turtle1/teleport_absolute service...')
            
        req_teleport = TeleportAbsolute.Request()
        req_teleport.x, req_teleport.y, req_teleport.theta = 8.0, 8.0, 1.57
        self.get_logger().info('Calling /turtle1/teleport_absolute (to 8.0, 8.0)...')
        future = teleport_cli.call_async(req_teleport)
        rclpy.spin_until_future_complete(self, future)

        # 4. /clear 클라이언트 호출
        clear_cli = self.create_client(Empty, '/clear')
        while not clear_cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('Waiting for /clear service...')
            
        req_clear = Empty.Request()
        self.get_logger().info('Calling /clear to wipe trajectories...')
        future = clear_cli.call_async(req_clear)
        rclpy.spin_until_future_complete(self, future)
        self.get_logger().info('All sequence completed successfully.')

def main(args=None):
    rclpy.init(args=args)
    node = BuiltinServiceClient()
    try:
        # spin 구조를 함수 내부로 양도하여 Humble 비동기 순차 호출 완료
        node.run_sequence()
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
