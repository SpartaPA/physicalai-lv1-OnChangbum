#ifndef SENSOR_SYSTEM_HPP
#define SENSOR_SYSTEM_HPP

#include <iostream>
#include <string>
#include <vector>
#include <memory>
#include <unordered_map>
#include <algorithm>

// 값 제한 함수 템플릿 (double 속도 및 int 픽셀값 양쪽 적용)
template <typename T>
T clamp(T value, T min_val, T max_val) {
    if (value < min_val) return min_val;
    if (value > max_val) return max_val;
    return value;
}

// 추상 클래스 Sensor
class Sensor {
protected:
    std::string name_;

public:
    Sensor(const std::string& name) : name_(name) {}
    
    // 주석 해제/처리를 통해 가상 소멸자 유무 실험 수행 가능
    virtual ~Sensor() {
        std::cout << "[Sensor] " << name_ << " 소멸자 호출 (부모)" << std::endl;
    }

    virtual void read() = 0; // 순수 가상 함수
    std::string getName() const { return name_; }
};

// Lidar 클래스 (Sensor 상속)
class Lidar : public Sensor {
public:
    Lidar(const std::string& name) : Sensor(name) {}
    ~Lidar() override {
        std::cout << "[Lidar] " << name_ << " 소멸자 호출 (자식)" << std::endl;
    }
    void read() override {
        std::cout << "[Lidar] " << name_ << " 레이저 스캔 데이터를 읽습니다." << std::endl;
    }
};

// Imu 클래스 (Sensor 상속)
class Imu : public Sensor {
public:
    Imu(const std::string& name) : Sensor(name) {}
    ~Imu() override {
        std::cout << "[Imu] " << name_ << " 소멸자 호출 (자식)" << std::endl;
    }
    void read() override {
        std::cout << "[Imu] " << name_ << " 가속도 및 자이로 데이터를 읽습니다." << std::endl;
    }
};

#endif