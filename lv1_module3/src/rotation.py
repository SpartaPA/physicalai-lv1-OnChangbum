"""문제 2·3 — 회전 행렬 모듈. (학생 작성용 템플릿)

축별 회전 행렬, 로드리게스 공식(임의 축 회전), Gram-Schmidt 재직교화,
회전행렬 판정과 고유값 분해 기반 축·각 복원을 직접 구현한다.

문제 1 에서 만든 `src/vectors.py` 를 그대로 재사용한다.
"""

from __future__ import annotations

import numpy as np

from .vectors import det, normalize, skew, norm

__all__ = [
    "rot_x",
    "rot_y",
    "rot_z",
    "rodrigues",
    "gram_schmidt",
    "orthogonality_error",
    "is_rotation",
    "axis_angle_from_matrix",
    "quaternion_from_axis_angle",
]


# ------------------------------------------------------------ 축별 회전 행렬

def rot_x(theta: float) -> np.ndarray:
    """x축 기준 회전 행렬 (theta 는 **라디안**). x 성분은 보존된다."""
    # TODO: 문제 2-1
    c = np.cos(theta)
    s = np.sin(theta)
    return np.array([
        [1.0, 0.0, 0.0],
        [0.0,   c,  -s],
        [0.0,   s,   c]
    ], dtype=float)


def rot_y(theta: float) -> np.ndarray:
    """y축 기준 회전 행렬 (theta 는 라디안). y 성분은 보존된다.

    부호 배치가 x·z 와 반대로 보이는 이유는 노트북 2-1 에서 설명한다.
    """
    # TODO: 문제 2-1
    c = np.cos(theta)
    s = np.sin(theta)
    return np.array([
        [  c, 0.0,   s],
        [0.0, 1.0, 0.0],
        [ -s, 0.0,   c]
    ], dtype=float)


def rot_z(theta: float) -> np.ndarray:
    """z축 기준 회전 행렬 (theta 는 라디안). z 성분은 보존된다."""
    # TODO: 문제 2-1
    c = np.cos(theta)
    s = np.sin(theta)
    return np.array([
        [  c,  -s, 0.0],
        [  s,   c, 0.0],
        [0.0, 0.0, 1.0]
    ], dtype=float)


def rodrigues(axis, theta: float) -> np.ndarray:
    """로드리게스 공식으로 임의 축 회전 행렬을 만든다.

        R = I + sin(theta) * K + (1 - cos(theta)) * K @ K,   K = [k]_x

    - 축은 함수 안에서 단위벡터로 정규화한다
      (정규화되지 않은 축을 넣어도 같은 결과가 나와야 한다).
    - 문제 1 의 `skew` 를 반드시 사용한다.
    """
    # TODO: 문제 2-5
    # 임의의 축을 단위 벡터로 정규화
    k = normalize(axis)
    
    # 문제 1의 skew 사용
    K = skew(k)
    I = np.eye(3, dtype=float)
    
    c = np.cos(theta)
    s = np.sin(theta)
    
    return I + s * K + (1.0 - c) * (K @ K)


# ------------------------------------------------------------- 재직교화 관련

def gram_schmidt(A) -> np.ndarray:
    """**열벡터**에 대해 Gram-Schmidt 직교정규화를 수행한다.

        q1 = a1 / |a1|
        vj = aj - sum_{i<j} (qi · aj) qi
        qj = vj / |vj|

    각 열에서 앞선 열 방향 성분(정사영)을 빼고 정규화하는 것이며,
    문제 1 의 project / reject 와 같은 연산의 반복이다.

    수치적으로는 성분을 빼자마자 갱신하는 modified Gram-Schmidt 가 더 안정적이다.
    앞선 열들에 종속인 열이 있으면 ValueError.
    """
    # TODO: 문제 3-2
    A_mat = np.array(A, dtype=float)
    m, n = A_mat.shape
    Q = np.zeros_like(A_mat)
    
    # 수정된 그람-슈미트(Modified Gram-Schmidt) 방식 채택
    for j in range(n):
        v = A_mat[:, j].copy()
        for i in range(j):
            # 이미 계산된 앞선 열 q_i 방향 성분을 제거
            v -= np.dot(Q[:, i], v) * Q[:, i]
            
        v_norm = norm(v)
        # 선형 종속(동일선상 또는 영벡터화) 검증 허용오차
        if v_norm < 1e-12:
            raise ValueError(f"입력 행렬의 {j}번째 열이 앞선 열들과 선형 종속 관계입니다.")
            
        Q[:, j] = v / v_norm
        
    return Q


def orthogonality_error(R) -> float:
    """직교성 이탈 지표: || R^T R - I ||_F  (프로베니우스 노름).

    완전한 직교행렬이면 0 이고, 클수록 직교성이 무너진 것이다.
    """
    # TODO: 문제 3-1
    R_mat = np.asarray(R, dtype=float)
    I = np.eye(R_mat.shape[1], dtype=float)
    diff = (R_mat.T @ R_mat) - I
    # 프로베니우스 노름 계산 (원소별 제곱합의 제곱근)
    return float(np.sqrt(np.sum(diff ** 2)))


def is_rotation(R, atol: float = 1e-8) -> bool:
    """회전행렬 판정: 직교(R^T R = I) **그리고** det(R) = +1 이면 True.

    det = -1 이면 직교이긴 하지만 반사가 섞여 있어 회전이 아니다.
    3x3 이 아니면 False.
    """
    # TODO: 문제 3-2
    R_mat = np.asarray(R, dtype=float)
    if R_mat.shape != (3, 3):
        return False
        
    # 1. 직교성 검증
    if orthogonality_error(R_mat) > atol:
        return False
        
    # 2. 행렬식이 +1 인지 검증 (vectors.py에서 직접 구현한 det 사용)
    if np.abs(det(R_mat) - 1.0) > atol:
        return False
        
    return True


# --------------------------------------------------- 회전축·회전각·쿼터니언

def axis_angle_from_matrix(R, atol: float = 1e-8):
    """고유값 분해로 회전축을, 대각합으로 회전각을 복원한다.

    - 회전축은 고유값 1 에 대응하는 실수 고유벡터다 (R k = k).
      -> 여기서는 `np.linalg.eig` 를 써도 된다 (검산이 아니라 축 복원이 목적).
    - 회전각은 trace(R) = 1 + 2 cos(theta) 에서 구한다.
    - arccos 의 치역이 [0, pi] 라 '어느 쪽으로 도는지'는 알 수 없고,
      고유벡터도 부호가 정해지지 않는다. 반대칭 성분
      R - R^T = 2 sin(theta) [k]_x 를 이용해 부호를 맞춘다.
    - theta = 0 (회전 없음) 과 theta = pi (sin = 0) 는 따로 처리해야 한다.
      두 경우에 어떤 규약을 쓸지 정하고 주석으로 남긴다.

    Returns
    -------
    axis : 단위 회전축 (3,)
    angle : 회전각 [rad], 0 <= angle <= pi
    """
    # TODO: 문제 6-4
    R_mat = np.asarray(R, dtype=float)
    
    # 1. 대각합(Trace)을 이용해 코사인 값 복원 및 클리핑
    tr = float(np.trace(R_mat))
    cos_theta = (tr - 1.0) / 2.0
    cos_theta = np.clip(cos_theta, -1.0, 1.0)
    angle = float(np.arccos(cos_theta))
    
    # [특이 규약 처리 1] theta = 0 (회전이 없는 경우)
    # 규약: 회전각이 0이므로 어떤 축이든 상관없으나 기본 축인 [1, 0, 0] 벡터를 반환한다.
    if angle < atol:
        return np.array([1.0, 0.0, 0.0], dtype=float), 0.0
        
    # [특이 규약 처리 2] theta = pi (180도 회전하는 경우)
    # 규약: R - R^T = 0 이 되어 반대칭 부호 판정이 불가능하므로, (R + I)의 열들 혹은 고유벡터에서 직접 부호를 채택한다.
    if np.abs(angle - np.pi) < atol:
        # R k = k 이므로 (R - I)k = 0 이고, R 이 대칭행렬 구조가 됨
        # 고유값 분해를 통해 고유값 1에 가장 가까운 고유벡터를 직접 추출
        w, v = np.linalg.eig(R_mat)
        idx = np.argmin(np.abs(w - 1.0))
        axis = np.real(v[:, idx])
        return normalize(axis), np.pi

    # 3. 일반적인 경우 (0 < theta < pi)
    # 고유값 분해를 통해 회전축 k의 방향(라인) 확보
    w, v = np.linalg.eig(R_mat)
    idx = np.argmin(np.abs(w - 1.0))
    axis = np.real(v[:, idx])
    axis = normalize(axis)
    
    # 반대칭 성분 R - R^T = 2*sin(theta)*[k]_x 를 이용해 고유벡터 부호 정렬
    # K_skew = (R - R^T) / (2 * sin(theta))
    sin_theta = np.sin(angle)
    K_skew = (R_mat - R_mat.T) / (2.0 * sin_theta)
    
    # 복원된 K_skew에서 실제 방향 성분 추출 추출
    k_extracted = np.array([K_skew[2, 1], K_skew[0, 2], K_skew[1, 0]])
    
    # 기존 고유벡터가 반대 방향을 가리키고 있다면 부호 반전 수행
    if np.dot(axis, k_extracted) < 0:
        axis = -axis
        
    return axis, angle


def quaternion_from_axis_angle(axis, angle: float) -> np.ndarray:
    """축-각에서 단위 쿼터니언을 만든다.

        q = (k * sin(theta/2), cos(theta/2))

    반환 순서는 SciPy `Rotation.as_quat()` 와 같은 **(x, y, z, w)** 로 맞춘다
    (그래야 문제 6-5 에서 바로 비교할 수 있다).
    """
    # TODO: 문제 6-5
    k = normalize(axis)
    half_angle = angle / 2.0
    
    s = np.sin(half_angle)
    c = np.cos(half_angle)
    
    # (x, y, z, w) 순서 조합
    return np.array([k[0] * s, k[1] * s, k[2] * s, c], dtype=float)
