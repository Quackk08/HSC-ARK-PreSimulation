# metrics.py
# 시뮬레이션 결과 평가 지표 계산

import numpy as np
from scipy import stats


class MetricsCalculator:
    """시뮬레이션 결과 평가 지표 계산 클래스"""

    def __init__(self, capture_zone_x_min, capture_zone_y_min, channel_length, channel_width):
        """
        MetricsCalculator 초기화

        Args:
            capture_zone_x_min (float): 회수 구역 x 최소값
            capture_zone_y_min (float): 회수 구역 y 최소값
            channel_length (float): 수로 길이
            channel_width (float): 수로 폭
        """
        self.capture_zone_x_min = capture_zone_x_min
        self.capture_zone_y_min = capture_zone_y_min
        self.channel_length = channel_length
        self.channel_width = channel_width

    def compute_lateral_displacement(self, initial_positions, final_positions):
        """
        평균 측면 변위 계산
        Δy = y_final - y_initial

        Args:
            initial_positions (np.ndarray): 초기 위치 (N, 2)
            final_positions (np.ndarray): 최종 위치 (N, 2)

        Returns:
            dict: 평균 변위, 표준편차 등
        """
        displacement = final_positions[:, 1] - initial_positions[:, 1]

        return {
            'mean_displacement': np.mean(displacement),
            'std_displacement': np.std(displacement),
            'min_displacement': np.min(displacement),
            'max_displacement': np.max(displacement)
        }

    def compute_capture_rate(self, final_positions):
        """
        회수 구역 도달률 계산
        R = N_capture / N_total * 100

        Args:
            final_positions (np.ndarray): 최종 위치 (N, 2)

        Returns:
            float: 회수율 (%)
        """
        in_capture_zone = (final_positions[:, 0] > self.capture_zone_x_min) & \
                          (final_positions[:, 1] > self.capture_zone_y_min)

        capture_rate = np.sum(in_capture_zone) / len(final_positions) * 100

        return capture_rate

    def compute_concentration_factor(self, initial_positions, final_positions):
        """
        농축 계수 계산
        C = (N_capture / capture_area) / (N_total / total_area)

        Args:
            initial_positions (np.ndarray): 초기 위치 (N, 2)
            final_positions (np.ndarray): 최종 위치 (N, 2)

        Returns:
            float: 농축 계수
        """
        # 회수 구역 내 입자 개수
        in_capture_zone = (final_positions[:, 0] > self.capture_zone_x_min) & \
                          (final_positions[:, 1] > self.capture_zone_y_min)
        n_capture = np.sum(in_capture_zone)

        # 초기 회수 구역 내 입자 개수 (거의 0)
        initial_in_capture = (initial_positions[:, 0] > self.capture_zone_x_min) & \
                             (initial_positions[:, 1] > self.capture_zone_y_min)
        n_initial_capture = np.sum(initial_in_capture)

        # 회수 구역 면적 계산
        capture_area = (self.channel_length - self.capture_zone_x_min) * \
                       (self.channel_width - self.capture_zone_y_min)
        total_area = self.channel_length * self.channel_width

        # 농축 계수 계산 (분모가 0이 되지 않도록 처리)
        if n_capture == 0:
            return 0.0

        concentration_factor = (n_capture / capture_area) / (len(final_positions) / total_area)

        return concentration_factor

    def compute_energy_efficiency(self, node_strength_sum, mean_displacement):
        """
        편향 효율 계산
        E = mean_Δy / energy_input

        Args:
            node_strength_sum (float): 노드 강도 합
            mean_displacement (float): 평균 측면 변위

        Returns:
            float: 편향 효율
        """
        if node_strength_sum == 0:
            return 0.0

        energy_efficiency = mean_displacement / (node_strength_sum + 1e-6)

        return energy_efficiency

    def compute_phase_gain_ratio(self, mean_displacement_aligned, mean_displacement_no_phase):
        """
        위상 보강 효과 계산
        G_phase = mean_Δy_aligned / mean_Δy_no_phase

        Args:
            mean_displacement_aligned (float): 위상 정렬 조건 평균 변위
            mean_displacement_no_phase (float): 위상 미적용 평균 변위

        Returns:
            float: 위상 보강 계수
        """
        if mean_displacement_no_phase == 0:
            return 1.0

        phase_gain = mean_displacement_aligned / mean_displacement_no_phase

        return phase_gain

    def get_all_metrics(self, initial_positions, final_positions, node_configs, use_phase=False):
        """
        모든 지표 한번에 계산

        Args:
            initial_positions (np.ndarray): 초기 위치
            final_positions (np.ndarray): 최종 위치
            node_configs (list): 노드 설정 리스트
            use_phase (bool): 위상 적용 여부

        Returns:
            dict: 모든 지표를 포함한 딕셔너리
        """
        displacement_dict = self.compute_lateral_displacement(initial_positions, final_positions)
        capture_rate = self.compute_capture_rate(final_positions)
        concentration_factor = self.compute_concentration_factor(initial_positions, final_positions)

        # 노드 강도 합 계산
        node_strength_sum = sum(node['strength'] for node in node_configs)

        energy_efficiency = self.compute_energy_efficiency(
            node_strength_sum,
            displacement_dict['mean_displacement']
        )

        metrics = {
            'mean_displacement': displacement_dict['mean_displacement'],
            'std_displacement': displacement_dict['std_displacement'],
            'min_displacement': displacement_dict['min_displacement'],
            'max_displacement': displacement_dict['max_displacement'],
            'capture_rate': capture_rate,
            'concentration_factor': concentration_factor,
            'energy_efficiency': energy_efficiency,
            'num_nodes': len(node_configs),
            'with_phase': use_phase
        }

        return metrics


class StatisticalAnalysis:
    """통계 분석 클래스"""

    @staticmethod
    def t_test(data_control, data_treatment):
        """
        독립표본 t-test 수행

        Args:
            data_control (list): 대조군 데이터
            data_treatment (list): 처리군 데이터

        Returns:
            dict: t-통계량, p-값 등
        """
        t_stat, p_value = stats.ttest_ind(data_treatment, data_control)

        return {
            't_statistic': t_stat,
            'p_value': p_value,
            'significant': p_value < 0.05
        }

    @staticmethod
    def anova(*groups):
        """
        일원배치 ANOVA 수행

        Args:
            *groups: 여러 그룹 데이터

        Returns:
            dict: F-통계량, p-값 등
        """
        f_stat, p_value = stats.f_oneway(*groups)

        return {
            'f_statistic': f_stat,
            'p_value': p_value,
            'significant': p_value < 0.05
        }

    @staticmethod
    def correlation(x, y):
        """
        Pearson 상관관계 계산

        Args:
            x (list): X 변수
            y (list): Y 변수

        Returns:
            dict: 상관계수, p-값
        """
        corr_coef, p_value = stats.pearsonr(x, y)

        return {
            'correlation': corr_coef,
            'p_value': p_value,
            'significant': p_value < 0.05
        }
