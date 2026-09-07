#ifndef MOTOR_HPP
#define MOTOR_HPP

class Motor {
private:
    double speed_;

public:
    Motor();
    void setSpeed(double speed);
    double getSpeed() const;
    void brake();
};

#endif