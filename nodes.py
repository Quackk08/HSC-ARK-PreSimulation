# nodes.py
# 음향 노드 클래스 정의

import numpy as np
import math


class AcousticNode:
    """음향 노드 클래스"""

    def __init__(self, x, y, strength, radius, phase, direction):
        """
        음향 노드 초기화

        Args:
            x (float): 노드 x 좌표 (m)
            y (float): 노드 y 좌표 (m)
            strength (float): 유도 강도 (m/s)
            radius (float): 영향 반경 (m)
            phase (float): 위상 (rad)
            direction (tuple): 방향 벡터 (dx, dy)
        """
        self.x = x
        self.y = y
        self.strength = strength
        self.radius = radius
        self.phase = phase
        self.direction = np.array(direction, dtype=float)
        self.direction = self.direction / np.linalg.norm(self.direction)  # 정규화

    def compute_influence(self, particle_positions):
        """
        입자들에 대한 영향장(Influence field) 계산
        Gaussian influence: exp(-r^2 / (2 * R^2))

        Args:
            particle_positions (np.ndarray): 입자 위치 배열 (N, 2)

        Returns:
            np.ndarray: 각 입자에 대한 영향 계수 (N,)
        """
        # 입자와 노드 사이의 거리 계산
        distances = np.sqrt(
            (particle_positions[:, 0] - self.x) ** 2 +
            (particle_positions[:, 1] - self.y) ** 2
        )

        # Gaussian influence field
        influence = np.exp(-distances ** 2 / (2 * self.radius ** 2))

        return influence

    def compute_acoustic_velocity(self, particle_positions, phase_gain=1.0):
        """
        입자들에 대한 음향 유도 속도 계산
        v_acoustic_i = A_i * influence * direction * phase_gain

        Args:
            particle_positions (np.ndarray): 입자 위치 배열 (N, 2)
            phase_gain (float): 위상 보정 계수 (기본값: 1.0)

        Returns:
            np.ndarray: 각 입자에 대한 음향 속도 벡터 (N, 2)
        """
        influence = self.compute_influence(particle_positions)

        # 음향 강도에 위상 보정 계수 적용
        effective_strength = self.strength * phase_gain

        # 속도 벡터 계산: influence * strength * direction
        acoustic_velocity = np.outer(
            influence * effective_strength,
            self.direction
        )

        return acoustic_velocity

    def compute_phase_gain(self, target_phase, k_phase=0.3):
        """
        위상 정렬에 따른 강도 보정 계수 계산
        phase_gain = 1 + k_phase * cos(phi - phi_target)

        Args:
            target_phase (float): 목표 위상 (rad)
            k_phase (float): 위상 정렬 효과 강도

        Returns:
            float: 위상 보정 계수
        """
        phase_diff = self.phase - target_phase
        phase_gain = 1.0 + k_phase * np.cos(phase_diff)

        return max(0.5, min(1.5, phase_gain))  # 0.5 ~ 1.5 범위 제한

    def get_position(self):
        """노드 위치 반환"""
        return np.array([self.x, self.y])


class NodeManager:
    """여러 음향 노드를 관리하는 클래스"""

    def __init__(self, nodes_config_list):
        """
        NodeManager 초기화

        Args:
            nodes_config_list (list): 노드 설정 딕셔너리 리스트
        """
        self.nodes = []
        for config in nodes_config_list:
            node = AcousticNode(
                x=config['x'],
                y=config['y'],
                strength=config['strength'],
                radius=config['radius'],
                phase=config['phase'],
                direction=config['direction']
            )
            self.nodes.append(node)

    def compute_total_acoustic_velocity(self, particle_positions, use_phase_gain=False,
                                       target_phase=0.0, k_phase=0.3, k_interference=0.2):
        """
        모든 노드의 음향 속도를 합산

        Args:
            particle_positions (np.ndarray): 입자 위치 배열 (N, 2)
            use_phase_gain (bool): 위상 보정 적용 여부
            target_phase (float): 목표 위상 (rad)
            k_phase (float): 위상 정렬 효과 강도
            k_interference (float): 노드 간 간섭 계수

        Returns:
            np.ndarray: 총 음향 속도 벡터 (N, 2)
        """
        if len(self.nodes) == 0:
            return np.zeros_like(particle_positions)

        total_velocity = np.zeros_like(particle_positions)

        # 각 노드의 음향 속도 계산
        for node in self.nodes:
            if use_phase_gain:
                phase_gain = node.compute_phase_gain(target_phase, k_phase)
            else:
                phase_gain = 1.0

            acoustic_vel = node.compute_acoustic_velocity(particle_positions, phase_gain)
            total_velocity += acoustic_vel

        # 노드 간 간섭 효과 적용 (선택사항)
        if use_phase_gain and len(self.nodes) > 1:
            interference_factor = self._compute_interference(particle_positions, k_interference)
            total_velocity *= interference_factor[:, np.newaxis]

        return total_velocity

    def _compute_interference(self, particle_positions, k_interference):
        """
        노드 간 간섭 효과 계산
        interference_gain = 1 + k_interference * Σ cos(phi_i - phi_j) * overlap_ij

        Args:
            particle_positions (np.ndarray): 입자 위치 배열 (N, 2)
            k_interference (float): 간섭 계수

        Returns:
            np.ndarray: 간섭 보정 계수 배열 (N,)
        """
        n_particles = particle_positions.shape[0]
        interference_factor = np.ones(n_particles)

        # 모든 노드 쌍에 대해 간섭 계산
        for i in range(len(self.nodes)):
            for j in range(i + 1, len(self.nodes)):
                node_i = self.nodes[i]
                node_j = self.nodes[j]

                # 각 입자에서의 두 노드 영향장 중복도 계산
                influence_i = node_i.compute_influence(particle_positions)
                influence_j = node_j.compute_influence(particle_positions)
                overlap = influence_i * influence_j

                # 위상 차이에 따른 보강/상쇄
                phase_diff = node_i.phase - node_j.phase
                phase_factor = np.cos(phase_diff)

                # 간섭 효과 추가
                interference_factor += k_interference * phase_factor * overlap

        # 범위 제한 (0.5 ~ 2.0)
        interference_factor = np.clip(interference_factor, 0.5, 2.0)

        return interference_factor

    def get_node_positions(self):
        """모든 노드의 위치 반환"""
        if len(self.nodes) == 0:
            return np.empty((0, 2))
        return np.array([node.get_position() for node in self.nodes])

    def get_num_nodes(self):
        """노드 개수 반환"""
        return len(self.nodes)
