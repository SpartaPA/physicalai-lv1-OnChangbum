cmake_minimum_required(VERSION 3.22)
project(SensorSystem LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# AddressSanitizer 활성화 플래그 (메모리 누수 추적용)
# 만약 누수를 검출하고 싶다면 아래 라인의 주석을 해제하고 재빌드하세요.
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fsanitize=address")

add_executable(sensor_app sensor_system.cpp)