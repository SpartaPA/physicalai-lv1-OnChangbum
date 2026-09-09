"""문제 4 — 궤적 보간. (학생 작성용 템플릿)

경유점(waypoint)을 지나는 궤적을 선형 보간 / 큐빅 스플라인으로 만들고,
시작·끝에서 속도와 가속도가 0 이 되는 5차 다항식 프로파일을 구현한다.

입력 규약
--------
- t_wp : (M,) 경유점 시각, 오름차순
- q_wp : (M,) 스칼라 궤적 또는 (M, D) 다차원 궤적 (예: 3차원 위치는 D = 3)
- t    : (N,) 평가할 시각 (t_wp[0] <= t <= t_wp[-1])
- 반환 : q_wp 가 (M,) 이면 (N,), (M, D) 이면 (N, D)

큐빅 스플라인은 `scipy.interpolate.CubicSpline` 을 써도 된다 (axis=0).
"""

from __future__ import annotations

import numpy as np
from scipy.interpolate import CubicSpline

__all__ = ["linear_interp", "cubic_spline_interp", "quintic_profile", "finite_diff"]


def linear_interp(t_wp, q_wp, t) -> np.ndarray:
    """경유점 사이를 직선으로 잇는 보간. 각 차원마다 `np.interp` 를 쓰면 된다.

    위치는 이어지지만 경유점에서 속도가 불연속(꺾임)이다.
    """
    # TODO: 문제 4-1
    t_wp = np.asarray(t_wp, dtype=float)
    q_wp = np.asarray(q_wp, dtype=float)
    t = np.asarray(t, dtype=float)
    
    if q_wp.ndim == 1:
        return np.interp(t, t_wp, q_wp)
    else:
        D = q_wp.shape[1]
        result = np.zeros((len(t), D), dtype=float)
        for d in range(D):
            result[:, d] = np.interp(t, t_wp, q_wp[:, d])
        return result


def cubic_spline_interp(t_wp, q_wp, t, bc_type: str = "natural") -> np.ndarray:
    """경유점을 지나는 큐빅 스플라인 보간 (위치·속도·가속도가 모두 연속, C2).

    bc_type : 양끝 경계 조건. "natural" (양끝 가속도 0) 또는 "clamped" (양끝 속도 0).
    """
    # TODO: 문제 4-1
    t_wp = np.asarray(t_wp, dtype=float)
    q_wp = np.asarray(q_wp, dtype=float)
    t = np.asarray(t, dtype=float)
    
    # SciPy CubicSpline을 활용하여 축방향(axis=0) 보간 수행
    cs = CubicSpline(t_wp, q_wp, axis=0, bc_type=bc_type)
    return cs(t)


def quintic_profile(t, t0: float, tf: float, q0, qf,
                    v0=0.0, vf=0.0, a0=0.0, af=0.0):
    """5차 다항식 궤적 q(t) 와 그 도함수 (q, qd, qdd) 를 돌려준다.

    경계 조건 6개 — q(t0)=q0, q(tf)=qf, qd(t0)=v0, qd(tf)=vf, qdd(t0)=a0, qdd(tf)=af —
    로 계수 6개 (c0 ~ c5) 를 정한다. 경계 속도·가속도가 모두 0 인 기본형은

        tau = (t - t0) / (tf - t0)
        s(tau) = 10 tau^3 - 15 tau^4 + 6 tau^5
        q(t) = q0 + (qf - q0) s(tau)

    로 닫힌 꼴이 있고, 일반형은 6x6 선형계를 풀면 된다. 어느 쪽으로 구현해도 된다.
    q0, qf 가 스칼라이면 (N,), (D,) 이면 (N, D) 를 돌려준다.

    Returns
    -------
    q, qd, qdd : 위치, 속도, 가속도 (해석적 미분. 유한차분이 아니다)
    """
    # TODO: 문제 4-4
    t = np.asarray(t, dtype=float)
    q0 = np.asarray(q0, dtype=float)
    qf = np.asarray(qf, dtype=float)
    
    T = tf - t0
    if np.isclose(T, 0.0):
        raise ValueError("tf와 t0는 같을 수 없습니다.")
        
    # 시간 정규화 및 다항식 결합을 위한 해석적 도함수 설계
    # 기본형 닫힌 꼴 수식 확장 및 속도/가속도 체인룰 반영 미분 유도
    tau = (t - t0) / T
    
    # 경계 속도와 가속도가 모두 0인 정규화 5차 준수 프로파일
    s = 10.0 * tau**3 - 15.0 * tau**4 + 6.0 * tau**5
    sd = (30.0 * tau**2 - 60.0 * tau**3 + 30.0 * tau**4) / T
    sdd = (60.0 * tau - 180.0 * tau**2 + 120.0 * tau**3) / (T**2)
    
    # q0, qf의 형상(스칼라 또는 다차원 벡터)에 유연하게 대응하도록 외부곱 브로드캐스팅 처리
    if q0.ndim == 0:
        q = q0 + (qf - q0) * s
        qd = (qf - q0) * sd
        qdd = (qf - q0) * sdd
    else:
        q = q0 + np.outer(s, (qf - q0))
        qd = np.outer(sd, (qf - q0))
        qdd = np.outer(sdd, (qf - q0))
        
    return q, qd, qdd


def finite_diff(y, t) -> np.ndarray:
    """시간축(axis 0)에 대한 수치 미분. `np.gradient(y, t, axis=0)` 를 쓰면 된다.

    y : (N,) 또는 (N, D),  t : (N,)
    속도 = finite_diff(q, t),  가속도 = finite_diff(속도, t)
    """
    # TODO: 문제 4-2
    y = np.asarray(y, dtype=float)
    t = np.asarray(t, dtype=float)
    return np.gradient(y, t, axis=0)