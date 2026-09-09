"""문제 5 — 4x4 동차변환 모듈. (학생 작성용 템플릿)

동차변환 생성/역변환, 점과 방향의 구분, 벡터화된 점군 변환,
정규방정식 기반 최소자승법을 직접 구현한다.
"""

from __future__ import annotations

import numpy as np

from .vectors import inverse_gauss_jordan

__all__ = [
    "make_T",
    "inv_T",
    "inv_T_batch",
    "to_homogeneous",
    "transform_point",
    "transform_direction",
    "transform_points",
    "least_squares_normal_equation",
    "rmse",
]


def make_T(R, t) -> np.ndarray:
    """회전 R(3x3)과 병진 t(3,)로 4x4 동차변환을 만든다.

        T = [[R, t],
             [0, 1]]

    R 이 3x3 이 아니면 ValueError.
    """
    # TODO: 문제 5-1
    R_mat = np.asarray(R, dtype=float)
    t_vec = np.asarray(t, dtype=float).flatten()
    
    if R_mat.shape != (3, 3):
        raise ValueError(f"R 은 3x3 행렬이어야 합니다. 받은 shape={R_mat.shape}")
    if t_vec.size != 3:
        raise ValueError(f"t 는 크기가 3인 벡터여야 합니다. 받은 size={t_vec.size}")
        
    T = np.eye(4, dtype=float)
    T[0:3, 0:3] = R_mat
    T[0:3, 3] = t_vec
    return T


def inv_T(T) -> np.ndarray:
    """동차변환의 역변환. **일반 역행렬 함수를 쓰지 않고** 공식으로 구한다.

        T^-1 = [[R^T, -R^T t],
                [  0,      1]]

    유도: T^-1 을 [[S, u], [0, 1]] 로 두고 T T^-1 = I 를 풀면
          R S = I -> S = R^T (R 이 직교),  R u + t = 0 -> u = -R^T t.

    4x4 가 아니면 ValueError.
    """
    # TODO: 문제 5-1
    T_mat = np.asarray(T, dtype=float)
    if T_mat.shape != (4, 4):
        raise ValueError(f"T 는 4x4 행렬이어야 합니다. 받은 shape={T_mat.shape}")
        
    R = T_mat[0:3, 0:3]
    t = T_mat[0:3, 3]
    
    R_T = R.T
    u = -R_T @ t
    
    T_inv = np.eye(4, dtype=float)
    T_inv[0:3, 0:3] = R_T
    T_inv[0:3, 3] = u
    return T_inv


def inv_T_batch(Ts) -> np.ndarray:
    """(N, 4, 4) 동차변환 묶음을 **반복문 없이** 한 번에 역변환한다.

    `inv_T` 와 같은 공식을 배치 축으로 확장한 것이다.
    문제 5-4 의 속도 비교에서 쓴다 — 단건 호출은 파이썬/NumPy 호출 오버헤드가
    지배해서 연산량 차이가 드러나지 않기 때문이다.

    힌트: 전치는 `np.swapaxes(..., 1, 2)`, 배치 행렬-벡터 곱은
          `np.einsum("nij,nj->ni", ...)` 로 쓸 수 있다.
    """
    # TODO: 문제 5-4
    Ts_mat = np.asarray(Ts, dtype=float)
    if Ts_mat.ndim != 3 or Ts_mat.shape[1:] != (4, 4):
        raise ValueError(f"Ts 는 (N, 4, 4) 구조여야 합니다. 받은 shape={Ts_mat.shape}")
        
    N = Ts_mat.shape[0]
    
    # 각 배치에서 R과 t 분리 추출
    R_batch = Ts_mat[:, 0:3, 0:3]  # (N, 3, 3)
    t_batch = Ts_mat[:, 0:3, 3]    # (N, 3)
    
    # R들의 전치 계산 (N, 3, 3)
    R_T_batch = np.swapaxes(R_batch, 1, 2)
    
    # 배치 행렬-벡터 곱셈 적용: u = -R^T * t
    u_batch = -np.einsum("nij,nj->ni", R_T_batch, t_batch)  # (N, 3)
    
    # 결과 (N, 4, 4) 단위행렬 묶음 생성 후 값 대입
    Ts_inv = np.zeros_like(Ts_mat)
    # 각 배치의 마지막 행을 [0, 0, 0, 1]로 초기화
    Ts_inv[:, 3, 3] = 1.0
    
    Ts_inv[:, 0:3, 0:3] = R_T_batch
    Ts_inv[:, 0:3, 3] = u_batch
    return Ts_inv


def to_homogeneous(P, w: float = 1.0) -> np.ndarray:
    """(3,) 또는 (N,3) 좌표에 마지막 성분 w 를 붙인다.

    w = 1 이면 점(위치), w = 0 이면 방향(벡터).
    """
    # TODO: 문제 5-2
    P_arr = np.asarray(P, dtype=float)
    
    if P_arr.ndim == 1:
        if P_arr.size != 3:
            raise ValueError(f"입력 벡터의 크기는 3이어야 합니다. 받은 크기={P_arr.size}")
        return np.append(P_arr, w)
        
    elif P_arr.ndim == 2:
        if P_arr.shape[1] != 3:
            raise ValueError(f"입력 점군의 두 번째 차원은 3이어야 합니다. 받은 shape={P_arr.shape}")
        N = P_arr.shape[0]
        w_col = np.full((N, 1), w, dtype=float)
        return np.hstack([P_arr, w_col])
        
    else:
        raise ValueError(f"지원하지 않는 차원 구조입니다: ndim={P_arr.ndim}")


def transform_point(T, p) -> np.ndarray:
    """점 변환 (w = 1): 회전과 병진이 모두 적용된다. 반환은 (3,)."""
    # TODO: 문제 5-2
    p_h = to_homogeneous(p, w=1.0)
    p_trans_h = np.asarray(T, dtype=float) @ p_h
    return p_trans_h[0:3]


def transform_direction(T, v) -> np.ndarray:
    """방향 변환 (w = 0): 회전만 적용되고 병진은 무시된다. 반환은 (3,)."""
    # TODO: 문제 5-2
    v_h = to_homogeneous(v, w=0.0)
    v_trans_h = np.asarray(T, dtype=float) @ v_h
    return v_trans_h[0:3]


def transform_points(T, P, w: float = 1.0) -> np.ndarray:
    """(N,3) 점군을 **반복문 없이** 한 번에 변환한다. (3,) 입력도 받아야 한다.

    힌트: (T @ P_h.T).T 대신 P_h @ T.T 를 쓰면 전치가 한 번으로 끝나고
          메모리 접근도 행 방향이라 캐시에 유리하다.
    """
    # TODO: 문제 5-2 / 6-2
    P_arr = np.asarray(P, dtype=float)
    T_mat = np.asarray(T, dtype=float)
    
    # (3,) 단건 입력 예외 처리 분기
    if P_arr.ndim == 1:
        p_h = to_homogeneous(P_arr, w=w)
        return (T_mat @ p_h)[0:3]
        
    # (N,3) 배치 점군 처리
    P_h = to_homogeneous(P_arr, w=w)
    P_trans_homo = P_h @ T_mat.T
    return P_trans_homo[:, 0:3]


def least_squares_normal_equation(A, b):
    """정규방정식 (A^T A) x = A^T b 를 직접 세워 최소자승해를 구한다.

    - (A^T A) 의 역행렬은 문제 4 에서 만든 `inverse_gauss_jordan` 으로 구한다
      (`np.linalg.lstsq` 는 노트북에서 **비교 대상**으로만 쓴다).
    - 근거: 잔차 r = b - A x 가 최소일 때 r 은 A 의 열공간에 수직이므로 A^T r = 0.

    Returns
    -------
    x : 최소자승해
    residual : b - A x
    """
    # TODO: 문제 5-5
    A_mat = np.array(A, dtype=float)
    b_vec = np.array(b, dtype=float)
    
    # 1. 정규방정식의 좌변(A^T A) 및 우변(A^T b) 계산
    ATA = A_mat.T @ A_mat
    ATb = A_mat.T @ b_vec
    
    # 2. 구현한 가우스-조던 함수를 이용해 역행렬 추출
    ATA_inv = inverse_gauss_jordan(ATA)
    
    # 3. 최소자승해 해 x 도출
    x = ATA_inv @ ATb
    
    # 4. 잔차 벡터 계산 (b - Ax)
    residual = b_vec - (A_mat @ x)
    
    return x, residual


def rmse(residual) -> float:
    """잔차의 RMSE = sqrt(mean(r^2))."""
    # TODO: 문제 5-5
    r = np.asarray(residual, dtype=float)
    return float(np.sqrt(np.mean(r ** 2)))
