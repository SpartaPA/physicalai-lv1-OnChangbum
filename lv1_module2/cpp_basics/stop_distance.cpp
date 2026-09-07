#include <iostream>
#include <cmath>

int main() {
    double velocity = 0.0;
    double friction_coefficient = 0.0;
    const double gravity = 9.81;

    std::cout << "========= 제동 거리 계산기 =========" << std::endl;
    std::cout << "차량의 초기 속도 (m/s) 입력: ";
    std::cin >> velocity;

    std::cout << "도로의 마찰 계수 입력: ";
    std::cin >> friction_coefficient;

    if (friction_coefficient <= 0) {
        std::cerr << "에러: 마찰 계수는 0보다 커야 합니다." << std::endl;
        return 1;
    }

    // 제동 거리 공식: d = v^2 / (2 * g * mu)
    double braking_distance = std::pow(velocity, 2) / (2 * gravity * friction_coefficient);

    std::cout << "------------------------------------" << std::endl;
    std::cout << "계산된 제동 거리: " << braking_distance << " m" << std::endl;
    std::cout << "====================================" << std::endl;

    return 0;
}