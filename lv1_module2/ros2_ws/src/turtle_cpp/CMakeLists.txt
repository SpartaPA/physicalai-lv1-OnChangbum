cmake_minimum_required(VERSION 3.22)
project(turtle_cpp)

# C++17 표준 및 빌드 경고 메시지 활성화
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
if(NOT CMAKE_CXX_FLAGS MATCHES "-Wall")
  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -Wextra")
endif()

# 1. 필수 의존성 패키지 검색
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(turtlesim REQUIRED)
find_package(turtle_interfaces REQUIRED)

# 2. 타깃 1: C++ 거리 발행자 노드 빌드 설정
add_executable(distance_publisher src/distance_publisher.cpp)
ament_target_dependencies(distance_publisher
  rclcpp
  std_msgs
  turtlesim
)

# 3. 타깃 2: C++ 거리 구독자 노드 빌드 설정
add_executable(distance_subscriber src/distance_subscriber.cpp)
ament_target_dependencies(distance_subscriber
  rclcpp
  std_msgs
)

# 4. 바이너리 실행 파일 설치(install) 규칙 선언 (ros2 run 가능하게 링크)
install(TARGETS
  distance_publisher
  distance_subscriber
  DESTINATION lib/${PROJECT_NAME}
)

# ament 시스템 빌드 마감 선언
ament_package()
