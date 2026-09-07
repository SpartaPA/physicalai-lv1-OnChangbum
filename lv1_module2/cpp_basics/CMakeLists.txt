cmake_minimum_required(VERSION 3.22)
project(CppBasics LANGUAGES CXX)

# C++17 표준 및 경고 메시지 활성화 설정
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -Wextra")

# -----------------------------------------------------------------
# 타깃 1: 제동 거리 계산 프로그램 (단일 파일 빌드)
# -----------------------------------------------------------------
add_executable(stop_distance stop_distance.cpp)

# -----------------------------------------------------------------
# 타깃 2: 모터 제어 프로그램 (다중 파일 빌드 - 컴파일 및 링크 분리 관찰용)
# -----------------------------------------------------------------
# 헤더 파일 폴더 지정 (현재 폴더의 motor.hpp를 참조하도록 설정)
include_directories(${CMAKE_CURRENT_SOURCE_DIR})

# main.cpp와 motor.cpp를 묶어서 motor_app 실행 파일 생성
add_executable(motor_app main.cpp motor.cpp)
