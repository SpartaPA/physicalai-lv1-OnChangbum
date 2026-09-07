# 테스트 주도 개발(TDD) 규격을 검증하기 위해 순수 수학 계산 함수 3개(거리, 외각, 진행률)를 독립 분리했습니다.
#!/usr/bin/env python3
import math

def calculate_distance(x1, y1, x2, y2):
    """두 좌표 간의 직선 거리를 계산하는 함수"""
    return math.hypot(x2 - x1, y2 - y1)

def calculate_exterior_angle(sides):
    """정다각형 외각을 계산하는 함수 (변의 수는 3 이상 정수여야 함)"""
    if not isinstance(sides, int):
        raise TypeError("Sides must be an integer.")
    if sides < 3:
        raise ValueError("Polygon sides must be 3 or more.")
    return (2.0 * math.pi) / sides

def calculate_progress(completed, total):
    """완주 진행률을 0.0 ~ 1.0 범위로 계산하는 함수"""
    if total <= 0:
        raise ZeroDivisionError("Total sides cannot be zero or negative.")
    progress = completed / total
    return max(0.0, min(1.0, progress))
