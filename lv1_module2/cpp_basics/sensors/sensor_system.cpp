#include "sensor_system.hpp"

void demonstrate_raii() {
    std::cout << "\n--- [RAII 및 소멸 시점 관찰 스코프 시작] ---" << std::endl;
    Lidar local_lidar("Local_Stack_Lidar"); // 스택 객체
    auto unique_imu = std::make_unique<Imu>("Unique_Heap_Imu"); // 힙 객체 (스마트 포인터)
    std::cout << "--- [RAII 및 소멸 시점 관찰 스코프 끝 직전] ---" << std::endl;
}

int main() {
    std::cout << "========= 현대 C++ 센서 계층 프로그램 =========" << std::endl;

    // 1. 다형성 루프 테스트 (std::vector + std::unique_ptr)
    std::vector<std::unique_ptr<Sensor>> sensor_pool;
    sensor_pool.push_back(std::make_unique<Lidar>("Front_Lidar"));
    sensor_pool.push_back(std::make_unique<Imu>("Chassis_Imu"));

    std::cout << "\n[다형성 루프 실행]" << std::endl;
    for (const auto& sensor : sensor_pool) {
        sensor->read();
    }

    // 2. RAII 소멸 시점 관찰 함수 호출
    demonstrate_raii();

    // 3. STL 컨테이너 및 count_if 활용 (목표점까지 거리 로그)
    std::unordered_map<std::string, double> latest_measurements;
    latest_measurements["Front_Lidar"] = 0.28;
    latest_measurements["Chassis_Imu"] = 0.55;

    std::vector<double> distance_logs = {0.12, 0.45, 0.32, 0.78, 0.22, 0.35, 0.91};
    
    // 거리가 0.35 이내인 기록 개수 계산
    long count = std::count_if(distance_logs.begin(), distance_logs.end(), [](double dist) {
        return dist <= 0.35;
    });
    std::cout << "\n[STL 연산] 0.35 이내 목표점 거리 기록 개수: " << count << "개" << std::endl;

    // 4. 함수 템플릿 clamp 적용 테스트
    double current_speed = 1850.5;
    int pixel_value = 320;
    
    std::cout << "\n[템플릿 Clamp 적용]" << std::endl;
    std::cout << "속도 제한 (1000~1500 RPM): " << clamp(current_speed, 1000.0, 1500.0) << " RPM" << std::endl;
    std::cout << "픽셀 제한 (0~255): " << clamp(pixel_value, 0, 255) << std::endl;

    // 5. 의도적인 메모리 누수 재현 (실험용 코드)
    // 주석 처리를 지우고 빌드하여 Sanitizer 혹은 valgrind 경고를 유도합니다.
    // std::cout << "\n[메모리 누수 테스트 의도적 실행]" << std::endl;
    std::cout << "\n[메모리 누수 테스트 -> 스마트 포인터로 수정 완료]" << std::endl;
    std::vector<std::unique_ptr<Sensor>> fixed_pool;
    for (int i = 0; i < 3; ++i) {
        // Sensor* leaked_sensor = new Lidar("Leaked_Lidar_" + std::to_string(i));
        // leaked_sensor->read();
        fixed_pool.push_back(std::make_unique<Lidar>("Fixed_Lidar_" + std::to_string(i)));
        fixed_pool.back()->read();
    }

    std::cout << "\n========= 프로그램 종료 =========" << std::endl;
    return 0;
}