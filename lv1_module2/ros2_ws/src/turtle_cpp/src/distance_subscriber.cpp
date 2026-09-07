#include <memory>
#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/float32.hpp"

class DistanceSubscriber : public rclcpp::Node {
public:
    DistanceSubscriber() : Node("turtle_distance_subscriber") {
        subscription_ = this->create_subscription<std_msgs::msg::Float32>(
            "/turtle_distance", 10, std::bind(&DistanceSubscriber::distance_callback, this, std::placeholders::_1));
        RCLCPP_INFO(this->get_logger(), "C++ Distance Subscriber Node Initialized.");
    }

private:
    void distance_callback(const std_msgs::msg::Float32::SharedPtr msg) const {
        RCLCPP_INFO(this->get_logger(), "Received Distance from Origin: [%.2f m]", msg->data);
    }
    rclcpp::Subscription<std_msgs::msg::Float32>::SharedPtr subscription_;
};

int main(int argc, char *argv[]) {
    rclcpp::init(argc, argv);
    auto node = std::make_shared<DistanceSubscriber>();
    try {
        rclcpp::spin(node);
    } catch (const std::exception &e) {
        (void)e;
    }
    rclcpp::shutdown();
    return 0;
}
