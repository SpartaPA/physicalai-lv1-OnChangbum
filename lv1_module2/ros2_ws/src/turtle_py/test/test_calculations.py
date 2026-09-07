# 과제 필수 요구조건인 정상(Normal), 경계값(Boundary), 예외 처리 실패(Failure/Exception) 케이스를 모두 담은 pytest 파일입니다.
#!/usr/bin/env python3
import pytest
import math
from turtle_py.calculations import calculate_distance, calculate_exterior_angle, calculate_progress

# 1. calculate_distance 테스트 (정상, 경계)
def test_calculate_distance_normal():
    assert calculate_distance(0.0, 0.0, 3.0, 4.0) == pytest.approx(5.0)

def test_calculate_distance_boundary():
    # 제자리 이동 경계값 검증
    assert calculate_distance(5.5, 5.5, 5.5, 5.5) == 0.0

# 2. calculate_exterior_angle 테스트 (정상, 예외 실패 처리)
def test_calculate_exterior_angle_normal():
    # 정삼각형 외각 (120도 -> 약 2.0944 rad)
    assert calculate_exterior_angle(3) == pytest.approx((2.0 * math.pi) / 3.0)
    # 정사각형 외각 (90도 -> 약 1.5708 rad)
    assert calculate_exterior_angle(4) == pytest.approx(math.pi / 2.0)

def test_calculate_exterior_angle_exception():
    # 3 미만의 변 입력 시 ValueError 예외 처리 검증
    with pytest.raises(ValueError):
        calculate_exterior_angle(2)
    # 정수가 아닌 타입 유입 시 TypeError 예외 처리 검증
    with pytest.raises(TypeError):
        calculate_exterior_angle(4.5)

# 3. calculate_progress 테스트 (정상, 경계, 예외 실패 처리)
def test_calculate_progress_normal():
    assert calculate_progress(2, 5) == pytest.approx(0.4)

def test_calculate_progress_boundary():
    # 하한/상한선 임계 경계값 검증
    assert calculate_progress(0, 4) == 0.0
    assert calculate_progress(4, 4) == 1.0

def test_calculate_progress_zero_division():
    # 0으로 나눌 때 ZeroDivisionError 예외 처리 발생 검증
    with pytest.raises(ZeroDivisionError):
        calculate_progress(1, 0)
