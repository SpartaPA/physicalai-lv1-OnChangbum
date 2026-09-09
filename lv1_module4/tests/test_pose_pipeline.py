"""문제 2 — PosePipeline 검증 (pytest). [학생 작성용 템플릿]

지시문이 요구하는 "2개 이상" 을 아래 두 테스트로 채운다.

  1. camera_to_base 가 모듈 ③ 체인(행렬 곱)과 같은 결과를 주는가  -> test_camera_to_base_matches_chain
  2. base 로 갔다가 camera 로 되돌리면 원래 점군이 나오는가       -> test_roundtrip_restores_points

작성 요령
--------
- 비교는 `np.allclose` (기본 허용오차) 로 한다.
- 난수는 반드시 시드를 고정한다 (fixture `rng`).
- 관절 각도 0 에서 파이프라인이 default_chain 과 같은지, 각도를 바꾸면 결과가 달라지는지 등
  테스트를 더 붙이면 좋다 (아래 권장 예시).

실행: 프로젝트 루트에서  pytest tests/test_pose_pipeline.py -v
"""

import numpy as np
import pytest

from src.coordinate_chain import default_chain
from src.pose_pipeline import PosePipeline
from src.transform import make_T, transform_points
from src.rotation import rot_x, rot_y, rot_z


@pytest.fixture
def rng():
    """난수는 반드시 시드를 고정한다."""
    return np.random.default_rng(42)


@pytest.fixture
def pipeline():
    """모듈 ③ default_chain 과 같은 값으로 만든 파이프라인."""
    chain = default_chain()
    return PosePipeline(chain.get("base", "link"), chain.get("link", "camera"))


# --- 1. camera_to_base == 체인/행렬 곱 --------------------------------------

def test_camera_to_base_matches_chain(pipeline, rng):
    # TODO: (N,3) 점군을 만들어 pipeline.camera_to_base 결과가
    #       default_chain().transform("base", "camera", P) 및
    #       transform_points(T_base_link @ T_link_camera, P) 와 같은지 검사
    P = rng.uniform(-1.0, 1.0, (50, 3))
    
    # 1. 파이프라인을 통한 정합 결과
    res_pipe = pipeline.camera_to_base(P)
    
    # 2. 모듈 ③ 체인 및 직접 수식 연산 대조
    res_chain = default_chain().transform(target="base", source="camera", P=P, w=1.0)
    
    T_composite = pipeline.T_base_link @ pipeline.T_link_camera
    res_manual = transform_points(T_composite, P, w=1.0)
    
    # 세 가지 도출값 상동 검사
    assert np.allclose(res_pipe, res_chain)
    assert np.allclose(res_pipe, res_manual)


# --- 2. 왕복 검증 -------------------------------------------------------------

def test_roundtrip_restores_points(pipeline, rng):
    # TODO: P_cam -> camera_to_base -> base_to_camera 가 P_cam 과 같은지 (allclose) 검사
    #       (3,) 단일 점과 (N,3) 점군 둘 다 확인
    # (N, 3) 배치 점군 검증
    P_cam_batch = rng.uniform(-0.5, 0.5, (100, 3))
    P_base_batch = pipeline.camera_to_base(P_cam_batch)
    P_back_batch = pipeline.base_to_camera(P_base_batch)
    assert np.allclose(P_cam_batch, P_back_batch)
    
    # (3,) 단일 점 검증
    p_cam_single = rng.uniform(-0.5, 0.5, (3,))
    p_base_single = pipeline.camera_to_base(p_cam_single)
    p_back_single = pipeline.base_to_camera(p_base_single)
    assert np.allclose(p_cam_single, p_back_single)

# --- 여기부터는 추가 테스트 (권장) -------------------------------------------

def test_joint_angle_zero_is_nominal(pipeline):
    """set_joint_angle(0) 이면 T_base_link 가 생성자에 준 값 그대로 유지되는지 검증"""
    T_nominal_link = pipeline.T_base_link.copy()
    pipeline.set_joint_angle(0.0)
    assert np.allclose(pipeline.T_base_link, T_nominal_link)

def test_joint_angle_changes_result(pipeline, rng):
    """관절 각도를 바꾸면 같은 관측이 base 에서 다른 위치로 편위되는지 검증"""
    P = rng.uniform(-0.5, 0.5, (10, 3))

    pipeline.set_joint_angle(0.0)
    res_0 = pipeline.camera_to_base(P)

    pipeline.set_joint_angle(0.5) # 라디안 단위 대입
    res_rot = pipeline.camera_to_base(P)

    assert not np.allclose(res_0, res_rot)

# 예) def test_distance_is_preserved(pipeline, rng):
#         """강체 변환은 두 점 사이 거리를 보존한다."""
#
# 예) def test_rejects_wrong_shape():
#         """(3,3) 을 넣으면 ValueError."""
