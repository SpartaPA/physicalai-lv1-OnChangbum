#!/bin/bash
source /opt/ros/humble/setup.bash
source install/setup.bash

echo "========================================================="
echo "💥 [Launch 복제 엔진] 전체 시스템 오케스트레이션을 일괄 가동합니다."
echo "========================================================="

# 1. 메인 turtlesim 노드 백그라운드 가동
ros2 run turtlesim turtlesim_node --ros-args --log-level INFO &
PID1=$!

# 2. 거리 발행자 노드 가동 (외부 YAML 파라미터 강제 주입)
python3 src/turtle_py/turtle_py/distance_publisher.py --ros-args --params-file src/turtle_py/config/params.yaml &
PID2=$!

# 3. 경고 구독자 노드 가동 (외부 YAML 파라미터 강제 주입)
python3 src/turtle_py/turtle_py/distance_subscriber.py --ros-args --params-file src/turtle_py/config/params.yaml &
PID3=$!

# 4. 네임스페이스 격리가 적용된 다중 로봇용 두 번째 거북이 노드 가동 (과제 핵심 규격)
ros2 run turtlesim turtlesim_node --ros-args -r __ns:=/turtle2 &
PID4=$!

trap "echo '시스템 일괄 종료 중...'; kill $PID1 $PID2 $PID3 $PID4; exit" INT
wait
