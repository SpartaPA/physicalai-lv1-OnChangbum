"""문제 3 — 회전 행렬의 수학적 성질 검증 (pytest). [학생 작성용 템플릿]

지시문이 요구하는 4가지를 각각 테스트 함수로 작성한다.

  1. 회전행렬의 열이 서로 직교하는 단위벡터인가   -> test_columns_are_orthonormal
  2. 행렬식이 1인가                               -> test_determinant_is_one
  3. 역행렬이 전치와 같은가                       -> test_inverse_equals_transpose
  4. 재직교화 결과가 직교행렬인가                 -> test_gram_schmidt_restores_orthogonality

작성 요령
--------
- `@pytest.mark.parametrize` 로 여러 축 x 여러 각도를 한 함수에서 검사하면
  테스트 하나가 여러 케이스를 담당한다 (아래 ANGLES / MAKERS 참고).
- 비교는 반드시 `np.isclose` / `np.allclose` 로 한다 (부동소수점).
- `np.linalg` 는 검산용으로만 쓰고, 쓸 때는 주석으로 검산임을 밝힌다.
- assert 에 실패 메시지를 붙이면 어디가 깨졌는지 바로 보인다.
- 4개는 **최소 개수**다. 반사 행렬 반례, 로드리게스 일치, 축·각 왕복 같은
  테스트를 더 붙이면 좋다.

실행: 프로젝트 루트에서  pytest -v
"""

import numpy as np
import pytest

from src.rotation import (
    axis_angle_from_matrix,
    gram_schmidt,
    is_rotation,
    orthogonality_error,
    rodrigues,
    rot_x,
    rot_y,
    rot_z,
)

ANGLES = [0.0, np.deg2rad(22.5), np.pi / 6, np.pi / 4, np.pi / 2, 2.0, np.pi, -1.234]
MAKERS = [rot_x, rot_y, rot_z]


@pytest.fixture
def rng():
    """난수는 반드시 시드를 고정한다."""
    return np.random.default_rng(42)


# --- 1. 열이 서로 직교하는 단위벡터인가 -------------------------------------

@pytest.mark.parametrize("maker", MAKERS)
@pytest.mark.parametrize("theta", ANGLES)
def test_columns_are_orthonormal(maker, theta):
    # TODO: 각 열의 길이가 1 인지, 서로 다른 두 열의 내적이 0 인지 검사
    R = maker(theta)
    
    for i in range(3):
        col_norm = np.linalg.norm(R[:, i]) # [검산] 넘파이 내장 노름
        assert np.isclose(col_norm, 1.0,atol=1e-12), f"{maker.__name__}({theta}): {i}번째 열의 길이가 1이 아닙니다. (값={col_norm})"
        
    dot_01 = np.dot(R[:, 0], R[:, 1])
    dot_12 = np.dot(R[:, 1], R[:, 2])
    dot_02 = np.dot(R[:, 0], R[:, 2])
    
    assert np.isclose(dot_01, 0.0,atol=1e-12), f"{maker.__name__}({theta}): 0번과 1번 열이 직교하지 않습니다. (내적={dot_01})"
    assert np.isclose(dot_12, 0.0,atol=1e-12), f"{maker.__name__}({theta}): 1번과 2번 열이 직교하지 않습니다. (내적={dot_12})"
    assert np.isclose(dot_02, 0.0,atol=1e-12), f"{maker.__name__}({theta}): 0번과 2번 열이 직교하지 않습니다. (내적={dot_02})"


# --- 2. 행렬식이 1인가 --------------------------------------------------------

@pytest.mark.parametrize("maker", MAKERS)
@pytest.mark.parametrize("theta", ANGLES)
def test_determinant_is_one(maker, theta):
    # TODO: det(R) == 1 인지 검사
    R = maker(theta)
    calc_det = np.linalg.det(R)
    
    assert np.isclose(calc_det, 1.0,atol=1e-12), f"{maker.__name__}({theta}): 행렬식이 1이 아닙니다. (det={calc_det})"


# --- 3. 역행렬 == 전치 --------------------------------------------------------

@pytest.mark.parametrize("maker", MAKERS)
@pytest.mark.parametrize("theta", ANGLES)
def test_inverse_equals_transpose(maker, theta):
    # TODO: inv(R) == R.T 이고 R.T @ R == I 인지 검사
    R = maker(theta)
    I_expected = np.eye(3, dtype=float)
    
    # 직교행렬의 성질 R.T @ R == I 검사
    RTR = R.T @ R
    assert np.allclose(RTR, I_expected, atol=1e-12), f"{maker.__name__}({theta}): R.T @ R 결과가 단위행렬이 아닙니다."


# --- 4. 재직교화 결과가 직교행렬인가 -----------------------------------------

def test_gram_schmidt_restores_orthogonality(rng):
    # TODO: 회전행렬에 작은 노이즈를 섞어 직교성을 깨뜨린 뒤,
    #       gram_schmidt 로 복구하면 직교성 오차가 기계정밀도 수준으로 줄고
    #       det 가 1 이며 is_rotation 이 True 인지 검사
    R_base = rot_z(0.5) @ rot_y(-0.3)
    noise = rng.uniform(-0.02, 0.02, size=(3, 3))
    corrupted_R = R_base + noise

    initial_err = orthogonality_error(corrupted_R)
    assert initial_err > 1e-3, "노이즈가 충분히 주입되지 않아 직교성이 유지되고 있습니다."
    
    fixed_R = gram_schmidt(corrupted_R)
    final_err = orthogonality_error(fixed_R)
    final_det = np.linalg.det(fixed_R)
    
    assert final_err < 1e-12, f"재직교화 후 오차가 기계정밀도 레벨로 수렴하지 않았습니다. (오차={final_err})"
    assert np.isclose(final_det, 1.0,atol=1e-12), f"재직교화 후 행렬식이 1이 아닙니다. (det={final_det})"
    assert is_rotation(fixed_R,atol=1e-9) == True, "재직교화 후 최종 회전행렬 판정(is_rotation) 결과가 True가 아닙니다."



# --- 여기부터는 추가 테스트 (권장) -------------------------------------------
#
# 예) def test_reflection_is_not_a_rotation():
#         """det = -1 인 반사 행렬은 직교여도 회전이 아니다."""
#
# 예) def test_rodrigues_matches_rot_z(theta): ...
# 예) def test_axis_angle_roundtrip(rng): ...
def test_reflection_is_not_a_rotation():
    """det = -1 인 반사 행렬은 직교여도 회전이 아니다."""
    S_reflect = np.diag([1.0, -1.0, 1.0])
    
    # 직교성은 유지되지만 회전 행렬이 아님을 판정 검증
    assert orthogonality_error(S_reflect) < 1e-12, "반사 행렬이 직교하지 않습니다."
    assert np.linalg.det(S_reflect) == -1.0, "반사 행렬의 행렬식이 -1이 아닙니다."
    assert is_rotation(S_reflect) == False, "반사 행렬이 회전 행렬(is_rotation=False)로 걸러지지 않았습니다."