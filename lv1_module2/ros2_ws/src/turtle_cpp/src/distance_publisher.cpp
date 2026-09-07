#include <chrono>
#include <functional>
#include <memory>
#include <string>
#include <cmath>
#include <vector>

#include "rclcpp/rclcpp.hpp"
#include "turtlesim/msg/pose.hpp"
#include "std_msgs/msg/float32.hpp"
#include "rcl_interfaces/msg/set_parameters_result.hpp"

using namespace std::chrono_literals;

class DistancePublisher : public rclcpp::Node {
public:
    DistancePublisher() : Node("turtle_distance_publisher"), current_rate_(10.0) {
        // 1. 파라미터 선언 및 기본값 초기화 (10.0 Hz)
        this->declare_parameter<double>("publish_rate", 10.0);
        this->get_parameter("publish_rate", current_rate_);

        // 2. Publisher 및 Subscriber 설정
        publisher_ = this->create_publisher<std_msgs::msg::Float32>("/turtle_distance", 10);
        subscription_ = this->create_subscription<turtlesim::msg::Pose>(
            "/turtle1/pose", 10, std::bind(&DistancePublisher::pose_callback, this, std::placeholders::_1));

        // 3. 타이머 생성 (10Hz)
        auto period = std::chrono::duration<double>(1.0 / current_rate_);
        timer_ = this->create_wall_timer(period, std::bind(&DistancePublisher::timer_callback, this));

        // 4. 파라미터 변경 동적 콜백 등록
        param_callback_handle_ = this->add_on_set_parameters_callback(
            std::bind(&DistancePublisher::parameter_callback, this, std::placeholders::_1));

        RCLCPP_INFO(this->get_logger(), "C++ Distance Publisher Node Initialized.");
    }

private:
    void pose_callback(const turtlesim::msg::Pose::SharedPtr msg) {
        current_pose_ = msg;
    }

    void timer_callback() {
        if (!current_pose_) {
            return;
        }

        // 원점(0,0)으로부터 직선 거리 계산 (hypot)
        double distance = std::hypot(current_pose_->x, current_pose_->y);

        auto msg = std_msgs::msg::Float32();
        msg.data = static_cast<float>(distance);
        publisher_->publish(msg);
    }

    rcl_interfaces::msg::SetParametersResult parameter_callback(const std::vector<rclcpp::Parameter> &parameters) {
        rcl_interfaces::msg::SetParametersResult result;
        result.successful = true;

        for (const auto &param : parameters) {
            if (param.get_name() == "publish_rate" && param.get_type() == rclcpp::ParameterType::PARAMETER_DOUBLE) {
                double new_rate = param.as_double();
                if (new_rate <= 0.0) {
                    result.successful = false;
                    result.reason = "Publish rate must be positive.";
                    return result;
                }

                if (new_rate != current_rate_) {
                    RCLCPP_INFO(this->get_logger(), "Publish rate changed: %.1f -> %.1f Hz", current_rate_, new_rate);
                    current_rate_ = new_rate;
                    timer_->cancel();
                    auto period = std::chrono::duration<double>(1.0 / current_rate_);
                    timer_ = this->create_wall_timer(period, std::bind(&DistancePublisher::timer_callback, this));
                }
            }
        }
        return result;
    }

    double current_rate_;
    turtlesim::msg::Pose::SharedPtr current_pose_{nullptr};
    rclcpp::Publisher<std_msgs::msg::Float32>::SharedPtr publisher_;
    rclcpp::Subscription<turtlesim::msg::Pose>::SharedPtr subscription_;
    rclcpp::TimerBase::SharedPtr timer_;
    rclcpp::node_interfaces::OnSetParametersCallbackHandle::SharedPtr param_callback_handle_;
};

int main(int argc, char *argv[]) {
    rclcpp::init(argc, argv);
    auto node = std::make_shared<DistancePublisher>();
    try {
        rclcpp::spin(node);
    } catch (const std::exception &e) {
        (void)e;
    }
    rclcpp::shutdown();
    return 0;
}
