"""문제 3 — 쿼터니언과 SLERP 검증 (pytest). [학생 작성용 템플릿]

지시문이 요구하는 두 가지:

  1. SLERP 결과가 항상 단위 쿼터니언인가                 -> test_slerp_is_unit_norm
  2. 보간 비율 0 과 1 에서 시작·목표 자세와 같은가       -> test_slerp_endpoints

작성 요령
--------
- 쿼터니언 순서는 (x, y, z, w). q 와 -q 는 같은 회전이므로 자세 비교는
  `quaternion_to_matrix` 로 회전행렬을 만들어 비교하거나 |q . q_ref| == 1 로 한다.
- `@pytest.mark.parametrize("t", [...])` 로 여러 비율을 한 번에 검사한다.
- 비교는 `np.allclose` / `np.isclose` (기본 허용오차).

실행: 프로젝트 루트에서  pytest tests/test_quaternion.py -v
"""

import numpy as np
import pytest

from src.quaternion import lerp_quat, matrix_to_quaternion, quaternion_to_matrix, slerp
from src.rotation import rodrigues, rot_x, rot_y, rot_z

TS = [0.0, 0.1, 0.25, 0.5, 0.75, 0.9, 1.0]


@pytest.fixture
def rng():
    return np.random.default_rng(42)


@pytest.fixture
def q_pair():
    """시작·목표 자세 (노트북 3-2 와 같은 값)."""
    R_start = rot_z(np.deg2rad(-30.0)) @ rot_x(np.deg2rad(20.0))
    R_goal = rot_z(np.deg2rad(120.0)) @ rot_y(np.deg2rad(60.0)) @ rot_x(np.deg2rad(-40.0))
    return matrix_to_quaternion(R_start), matrix_to_quaternion(R_goal)


# --- 1. SLERP 결과는 항상 단위 쿼터니언 ---------------------------------------

@pytest.mark.parametrize("t", TS)
def test_slerp_is_unit_norm(q_pair, t):
    # TODO: slerp(q0, q1, t) 의 노름이 1 인지 검사
    q0, q1 = q_pair
    q_interpolated = slerp(q0, q1, t)
    
    # 생성된 보간 쿼터니언의 크기가 유클리드 노름 1로 정규화되어 유지되는지 단언
    assert np.isclose(np.linalg.norm(q_interpolated), 1.0)


# --- 2. t = 0 / 1 에서 시작·목표 자세 -----------------------------------------

def test_slerp_endpoints(q_pair):
    # TODO: slerp(q0, q1, 0) 이 q0 과, slerp(q0, q1, 1) 이 q1 과 같은 회전인지 검사
    #       (부호가 다를 수 있으므로 회전행렬로 비교하거나 |q . q_ref| == 1 로 비교)
    q0, q1 = q_pair
    
    q_at_0 = slerp(q0, q1, 0.0)
    q_at_1 = slerp(q0, q1, 1.0)
    
    # 규약에 명시된 |q . q_ref| == 1 조건을 반영하여 부호 독립적 자세 동치성 단언
    assert np.isclose(np.abs(np.dot(q_at_0, q0)), 1.0)
    assert np.isclose(np.abs(np.dot(q_at_1, q1)), 1.0)


# --- 여기부터는 추가 테스트 (권장) -------------------------------------------
#
def test_matrix_quaternion_roundtrip(rng):
#         """무작위 회전 50개: R -> q -> R 이 원래 행렬로 돌아오는가."""
    for _ in range(50):
        axis = rng.normal(size=3)
        angle = rng.uniform(0.0, np.pi)
        R_orig = rodrigues(axis, angle)
        
        q = matrix_to_quaternion(R_orig)
        R_back = quaternion_to_matrix(q)
        
        assert np.allclose(R_orig, R_back)
#
# 예) def test_slerp_matches_scipy(q_pair):
#         """scipy.spatial.transform.Slerp 와 회전행렬 기준으로 일치하는가."""
#
def test_slerp_nearly_identical_poses(q_pair):
#         """거의 같은 두 자세에서 NaN 이 나오지 않는가."""
    q0, _ = q_pair
    # 강제 미소 변위 오프셋 생성
    q_near = q0 + 1e-9
    q_near /= np.linalg.norm(q_near)
    
    q_mid = slerp(q0, q_near, 0.5)
    assert not np.any(np.isnan(q_mid))
#
# 예) def test_lerp_norm_drops_below_one(q_pair):
#         """정규화하지 않은 선형 보간의 중간값은 크기가 1 보다 작다."""
