# 시뮬레이터 몸체, 거리 발행자(YAML 반영), 경고 구독자(YAML 반영)를 일괄 가동하며, 네임스페이스 격리가 적용된 두 번째 거북이(turtle2) 노드까지 한 번에 안전하게 오케스트레이션합니다.
import os
from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    # ★ 패키지 인덱스 조회를 배제하고 파일의 물리적 상대 경로를 직접 계산 (버그 원천 차단)
    current_file_dir = os.path.dirname(os.path.abspath(__file__))
    # launch 폴더의 상위 패키지 루트로 이동 후 config/params.yaml 정밀 추적
    param_file_path = os.path.join(os.path.dirname(current_file_dir), 'config', 'params.yaml')

    return LaunchDescription([
        # 1. 메인 turtlesim 시뮬레이터 노드 기동
        Node(
            package='turtlesim',
            executable='turtlesim_node',
            name='turtlesim',
            output='screen'
        ),
        
        # 2. 거리 발행자 노드 기동 (외부 YAML 파라미터 주입)
        Node(
            package='turtle_py',
            executable='distance_publisher',
            name='turtle_distance_publisher',
            output='screen',
            parameters=[param_file_path]
        ),
        
        # 3. 경고 구독자 노드 기동 (외부 YAML 파라미터 주입)
        Node(
            package='turtle_py',
            executable='distance_subscriber',
            name='turtle_distance_subscriber',
            output='screen',
            parameters=[param_file_path]
        ),
        
        # 4. 네임스페이스 격리가 적용된 다중 로봇용 두 번째 거북이 노드 기동
        Node(
            package='turtlesim',
            executable='turtlesim_node',
            namespace='turtle2',
            name='turtlesim',
            output='screen'
        )
    ])
