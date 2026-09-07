"""문제 5 — 동차변환 inv_T 검증 (pytest). [학생 작성용 템플릿]

지시문이 요구하는 것은 `inv_T` 검증이지만,
점/방향 구분과 벡터화, 최소자승까지 함께 검증해 두면 이후 문제에서 안전하다.

실행: 프로젝트 루트에서  pytest -v
"""

import numpy as np
import pytest

from src.rotation import rot_x, rot_y, rot_z
from src.transform import (
    inv_T,
    least_squares_normal_equation,
    make_T,
    transform_direction,
    transform_point,
    transform_points,
)


@pytest.fixture
def T():
    """테스트에 쓸 대표 동차변환 하나."""
    R = rot_z(0.9) @ rot_y(-0.35) @ rot_x(1.3)
    return make_T(R, [0.35, -0.15, 0.55])


def test_inv_T_gives_identity(T):
    # TODO: inv_T(T) @ T 와 T @ inv_T(T) 가 모두 4x4 단위행렬인지 검사
    Ti = inv_T(T)
    I_expected = np.eye(4, dtype=float)
    
    assert np.allclose(Ti @ T, I_expected, atol=1e-12), "inv_T(T) @ T 결과가 단위행렬이 아닙니다."
    assert np.allclose(T @ Ti, I_expected, atol=1e-12), "T @ inv_T(T) 결과가 단위행렬이 아닙니다."


def test_inv_T_matches_generic_inverse(T):
    # TODO: inv_T(T) 가 np.linalg.inv(T) 와 일치하는지 검사 (np.linalg 는 검산용)
    Ti = inv_T(T)
    Ti_ref = np.linalg.inv(T) # [검산] 넘파이 내장 일반 역행렬 함수
    
    assert np.allclose(Ti, Ti_ref, atol=1e-12), "구현한 inv_T 결과가 np.linalg.inv와 일치하지 않습니다."


def test_point_and_direction_differ(T):
    # TODO: 같은 벡터를 점(w=1)/방향(w=0)으로 변환하면 결과가 다르고,
    #       그 차이가 정확히 병진 벡터 T[:3, 3] 이며,
    #       방향 변환은 길이를 보존하는지 검사
    v = np.array([1.0, 2.0, 3.0], dtype=float)
    
    p_out = transform_point(T, v)
    d_out = transform_direction(T, v)
    t_expected = T[:3, 3]
    
    assert not np.allclose(p_out, d_out), "점 변환과 방향 변환 결과가 우연히 일치합니다."
    
    assert np.allclose(p_out - d_out, t_expected, atol=1e-12), "점과 방향 변환의 차이가 병진 벡터 t와 다릅니다."
    
    assert np.isclose(np.linalg.norm(d_out), np.linalg.norm(v), atol=1e-12), "방향 변환 시 벡터의 길이가 보존되지 않습니다."


def test_transform_points_is_vectorized(T):
    # TODO: (N,3) 점군을 한 번에 변환한 결과가
    #       transform_point 를 반복문으로 돌린 결과와 같은지 검사
    rng = np.random.default_rng(42) # 난수 시드 고정
    P_cam = rng.uniform(-1.0, 1.0, size=(50, 3))
    
    # 1. 배치 처리 (반복문 없음)
    P_base_vec = transform_points(T, P_cam, w=1.0)
    
    # 2. 파이썬 반복문을 사용한 단건 처리 누적
    P_base_loop = np.array([transform_point(T, p) for p in P_cam])
    
    assert np.allclose(P_base_vec, P_base_loop, atol=1e-12), "벡터화 처리 결과가 반복문 처리 결과와 일치하지 않습니다."


def test_roundtrip_through_inverse(T):
    # TODO: T 로 보냈다가 inv_T(T) 로 되돌리면 원래 점군이 나오는지 검사
    rng = np.random.default_rng(100)
    P_orig = rng.uniform(-2.0, 2.0, size=(100, 3))
    
    # 순방향 변환 T 적용
    P_forward = transform_points(T, P_orig, w=1.0)
    
    # 역방향 변환 inv_T(T) 적용하여 복원
    Ti = inv_T(T)
    P_back = transform_points(Ti, P_forward, w=1.0)
    
    assert np.allclose(P_back, P_orig, atol=1e-12), "동차변환 왕복(Roundtrip) 후 원본 좌표가 복원되지 않았습니다."


def test_least_squares_matches_lstsq():
    # TODO: 노이즈를 섞은 과결정 문제를 만들어
    #       least_squares_normal_equation 의 해가 np.linalg.lstsq 와 일치하고
    #       잔차가 A 의 열공간에 수직(A^T r = 0)인지 검사
    rng = np.random.default_rng(123)
    
    # 방정식 개수 40개, 미지수 6개 구조의 과결정 시스템 설계
    m, n = 40, 6
    A = rng.uniform(-5.0, 5.0, size=(m, n))
    x_true = rng.uniform(-2.0, 2.0, size=n)
    
    # 측정 노이즈 추가
    noise = 0.02 * rng.standard_normal(size=m)
    b = A @ x_true + noise
    
    # 정규방정식 솔버 실행
    x_hat, residual = least_squares_normal_equation(A, b)
    
    # 1. [비교 대상] 넘파이 내장 최소자승 솔버 결과 추출
    x_ref, _, _, _ = np.linalg.lstsq(A, b, rcond=None)
    assert np.allclose(x_hat, x_ref, atol=1e-10), "정규방정식 최소자승해가 np.linalg.lstsq와 일치하지 않습니다."
    
    # 2. 잔차가 A의 열공간과 완전 수직(직교 조건 A^T @ r == 0)인지 수치 검증
    # 부동소수점 오차 및 노이즈가 주입된 조건이므로 자릿수를 고려해 허용오차(atol) 설정
    assert np.allclose(A.T @ residual, 0.0, atol=1e-9), "최소자승 오차 잔차 벡터가 설계행렬 A의 열공간에 수직하지 않습니다."
