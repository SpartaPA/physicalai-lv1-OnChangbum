#include "motor.hpp"
#include <iostream>

Motor::Motor() : speed_(0.0) {}

void Motor::setSpeed(double speed) {
    speed_ = speed;
    std::cout << "[Motor] 속도가 " << speed_ << " RPM으로 설정되었습니다." << std::endl;
}

double Motor::getSpeed() const {
    return speed_;
}

void Motor::brake() {
    speed_ = 0.0;
    std::cout << "[Motor] 급제동! 속도가 0 RPM이 되었습니다." << std::endl;
}

// 빌드 테스트