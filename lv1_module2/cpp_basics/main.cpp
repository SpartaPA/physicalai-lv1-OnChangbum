#include <iostream>
#include "motor.hpp"

int main() {
    std::cout << "========= 모터 제어 프로그램 =========" << std::endl;
    
    Motor my_motor;
    std::cout << "현재 초기 속도: " << my_motor.getSpeed() << " RPM" << std::endl;

    my_motor.setSpeed(1500.0);
    std::cout << "현재 운행 속도: " << my_motor.getSpeed() << " RPM" << std::endl;

    my_motor.brake();
    std::cout << "최종 모터 속도: " << my_motor.getSpeed() << " RPM" << std::endl;
    
    std::cout << "====================================" << std::endl;
    return 0;
}