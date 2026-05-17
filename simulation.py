# simulation.py
# 입자 추적 시뮬레이션 클래스

import numpy as np
from nodes import NodeManager


class ParticleSimulation:
    """2D 입자 추적 시뮬레이션 클래스"""

    def __init__(self, channel_length, channel_width, num_particles, dt, total_time,
                 flow_velocity, noise_sigma, nodes_config=None):
        """
        시뮬레이션 초기화

        Args:
            channel_length (float): 수로 길이 (m)
            channel_width (float): 수로 폭 (m)
            num_particles (int): 입자 개수
            dt (float): 시간 간격 (s)
            total_time (float): 총 시뮬레이션 시간 (s)
            flow_velocity (float): 기본 유속 (m/s)
            noise_sigma (float): 노이즈 표준편차 (m/s)
            nodes_config (list): 노드 설정 리스트
        """
        self.channel_length = channel_length
        self.channel_width = channel_width
        self.num_particles = num_particles
        self.dt = dt
        self.total_time = total_time
        self.flow_velocity = flow_velocity
        self.noise_sigma = noise_sigma

        # 노드 관리자 초기화
        if nodes_config is None:
            nodes_config = []
        self.node_manager = NodeManager(nodes_config)

        # 시간 스텝 개수 계산
        self.num_steps = int(np.ceil(self.total_time / self.dt))

        # 입자 위치 및 궤적 저장
        self.positions = None
        self.trajectories = None
        self.initial_positions = None

    def initialize_particles(self, random_seed=None):
        """
        입자 초기 위치 설정 (균등 분포)

        Args:
            random_seed (int): 난수 시드
        """
        if random_seed is not None:
            np.random.seed(random_seed)

        # 초기 위치: 수로 시작 부분, y 방향 균등 분포
        self.positions = np.zeros((self.num_particles, 2))
        self.positions[:, 0] = np.random.uniform(0.05, 0.15, self.num_particles)  # x: 0.05~0.15 m
        self.positions[:, 1] = np.random.uniform(0, self.channel_width, self.num_particles)  # y: 0~0.4 m

        # 초기 위치 저장
        self.initial_positions = self.positions.copy()

        # 궤적 저장용 배열 초기화 (각 타임스텝마다 저장)
        self.trajectories = np.zeros((self.num_steps + 1, self.num_particles, 2))
        self.trajectories[0] = self.positions.copy()

    def apply_flow_velocity(self):
        """기본 유속 적용"""
        return np.array([self.flow_velocity, 0.0])

    def apply_acoustic_velocity(self, use_phase_gain=False, target_phase=0.0,
                               k_phase=0.3, k_interference=0.2):
        """
        음향 유도 속도 계산

        Args:
            use_phase_gain (bool): 위상 보정 적용 여부
            target_phase (float): 목표 위상
            k_phase (float): 위상 정렬 강도
            k_interference (float): 간섭 계수

        Returns:
            np.ndarray: 음향 유도 속도 벡터 (N, 2)
        """
        return self.node_manager.compute_total_acoustic_velocity(
            self.positions,
            use_phase_gain=use_phase_gain,
            target_phase=target_phase,
            k_phase=k_phase,
            k_interference=k_interference
        )

    def apply_noise(self):
        """난류/노이즈 적용 (Gaussian)"""
        noise = np.random.normal(0, self.noise_sigma, (self.num_particles, 2))
        return noise

    def apply_boundary_conditions(self):
        """경계 조건 적용 (주기적 또는 반사)"""
        # x축: 하천을 벗어난 입자는 우측으로 이동하므로 제거 처리
        # y축: 상하단에 닿은 입자는 반사 또는 경계에 고정
        out_of_bounds = (self.positions[:, 1] < 0) | (self.positions[:, 1] > self.channel_width)
        self.positions[out_of_bounds & (self.positions[:, 1] < 0), 1] = 0
        self.positions[out_of_bounds & (self.positions[:, 1] > self.channel_width), 1] = self.channel_width

    def step(self, use_phase_gain=False, target_phase=0.0, k_phase=0.3, k_interference=0.2):
        """
        한 타임스텝 시뮬레이션 수행

        Args:
            use_phase_gain (bool): 위상 보정 적용 여부
            target_phase (float): 목표 위상
            k_phase (float): 위상 정렬 강도
            k_interference (float): 간섭 계수
        """
        # 각 속도 성분 계산
        v_flow = self.apply_flow_velocity()
        v_acoustic = self.apply_acoustic_velocity(use_phase_gain, target_phase, k_phase, k_interference)
        v_noise = self.apply_noise()

        # 총 속도 = flow + acoustic + noise
        v_total = v_flow + v_acoustic + v_noise

        # 위치 업데이트
        self.positions = self.positions + v_total * self.dt

        # 경계 조건 적용
        self.apply_boundary_conditions()

    def run(self, use_phase_gain=False, target_phase=0.0, k_phase=0.3, k_interference=0.2):
        """
        전체 시뮬레이션 실행

        Args:
            use_phase_gain (bool): 위상 보정 적용 여부
            target_phase (float): 목표 위상
            k_phase (float): 위상 정렬 강도
            k_interference (float): 간섭 계수
        """
        for step_idx in range(self.num_steps):
            self.step(use_phase_gain, target_phase, k_phase, k_interference)
            self.trajectories[step_idx + 1] = self.positions.copy()

    def get_final_positions(self):
        """최종 입자 위치 반환"""
        return self.positions.copy()

    def get_initial_positions(self):
        """초기 입자 위치 반환"""
        return self.initial_positions.copy()

    def get_trajectories(self):
        """모든 궤적 데이터 반환"""
        return self.trajectories.copy()

    def get_node_manager(self):
        """노드 관리자 반환"""
        return self.node_manager
