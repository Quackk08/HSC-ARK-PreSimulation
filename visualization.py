# visualization.py
# 시뮬레이션 결과 시각화

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib import rcParams
import os


class Visualizer:
    """시뮬레이션 결과 시각화 클래스"""

    def __init__(self, output_dir='./output/', dpi=300):
        """
        Visualizer 초기화

        Args:
            output_dir (str): 출력 디렉토리
            dpi (int): 그림 해상도
        """
        self.output_dir = output_dir
        self.dpi = dpi

        # 한글 폰트 설정
        rcParams['font.family'] = 'DejaVu Sans'
        rcParams['axes.unicode_minus'] = False

        # 출력 디렉토리 생성
        os.makedirs(output_dir, exist_ok=True)

    def plot_trajectories(self, trajectories, channel_length, channel_width,
                         node_positions, capture_zone_x_min, capture_zone_y_min,
                         filename='trajectories.png', title='Particle Trajectories'):
        """
        입자 궤적 그래프

        Args:
            trajectories (np.ndarray): 궤적 데이터 (T, N, 2)
            channel_length (float): 수로 길이
            channel_width (float): 수로 폭
            node_positions (np.ndarray): 노드 위치 (M, 2)
            capture_zone_x_min (float): 회수 구역 x 최소값
            capture_zone_y_min (float): 회수 구역 y 최소값
            filename (str): 저장 파일명
            title (str): 그래프 제목
        """
        fig, ax = plt.subplots(figsize=(12, 5), dpi=self.dpi)

        # 샘플 입자 궤적 플롯 (모든 입자를 그리면 복잡하므로 일부만 선택)
        num_samples = min(50, trajectories.shape[1])
        sample_indices = np.linspace(0, trajectories.shape[1] - 1, num_samples, dtype=int)

        for idx in sample_indices:
            ax.plot(trajectories[:, idx, 0], trajectories[:, idx, 1], 'b-', alpha=0.3, linewidth=0.5)

        # 초기 위치 표시
        ax.scatter(trajectories[0, sample_indices, 0], trajectories[0, sample_indices, 1],
                  c='green', s=20, marker='o', label='Start', zorder=5)

        # 최종 위치 표시
        ax.scatter(trajectories[-1, sample_indices, 0], trajectories[-1, sample_indices, 1],
                  c='red', s=20, marker='x', label='End', zorder=5)

        # 노드 위치 표시
        if len(node_positions) > 0:
            ax.scatter(node_positions[:, 0], node_positions[:, 1],
                      c='orange', s=100, marker='*', label='Acoustic Node', zorder=10)

        # 회수 구역 표시
        capture_rect = patches.Rectangle(
            (capture_zone_x_min, capture_zone_y_min),
            channel_length - capture_zone_x_min,
            channel_width - capture_zone_y_min,
            linewidth=2, edgecolor='red', facecolor='yellow', alpha=0.2, label='Capture Zone'
        )
        ax.add_patch(capture_rect)

        # 축 범위 설정
        ax.set_xlim(-0.05, channel_length + 0.05)
        ax.set_ylim(-0.05, channel_width + 0.05)
        ax.set_aspect('equal')
        ax.set_xlabel('X (m)', fontsize=12)
        ax.set_ylabel('Y (m)', fontsize=12)
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.legend(loc='upper right')
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, filename), dpi=self.dpi)
        plt.close()

    def plot_displacement_comparison(self, results_dict, filename='mean_displacement_comparison.png'):
        """
        평균 측면 변위 비교 그래프

        Args:
            results_dict (dict): 케이스별 결과 딕셔너리
            filename (str): 저장 파일명
        """
        fig, ax = plt.subplots(figsize=(10, 6), dpi=self.dpi)

        cases = list(results_dict.keys())
        means = [results_dict[case]['mean_displacement'] for case in cases]
        stds = [results_dict[case]['std_displacement'] for case in cases]

        x_pos = np.arange(len(cases))
        colors = ['gray', 'blue', 'green', 'red']

        bars = ax.bar(x_pos, means, yerr=stds, capsize=5, color=colors[:len(cases)], alpha=0.7)

        ax.set_xlabel('Case', fontsize=12)
        ax.set_ylabel('Mean Lateral Displacement (m)', fontsize=12)
        ax.set_title('Mean Lateral Displacement Comparison', fontsize=14, fontweight='bold')
        ax.set_xticks(x_pos)
        ax.set_xticklabels(cases)
        ax.grid(True, alpha=0.3, axis='y')

        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, filename), dpi=self.dpi)
        plt.close()

    def plot_capture_rate_comparison(self, results_dict, filename='capture_rate_comparison.png'):
        """
        회수율 비교 그래프

        Args:
            results_dict (dict): 케이스별 결과 딕셔너리
            filename (str): 저장 파일명
        """
        fig, ax = plt.subplots(figsize=(10, 6), dpi=self.dpi)

        cases = list(results_dict.keys())
        capture_rates = [results_dict[case]['capture_rate'] for case in cases]

        x_pos = np.arange(len(cases))
        colors = ['gray', 'blue', 'green', 'red']

        bars = ax.bar(x_pos, capture_rates, color=colors[:len(cases)], alpha=0.7)

        ax.set_xlabel('Case', fontsize=12)
        ax.set_ylabel('Capture Rate (%)', fontsize=12)
        ax.set_title('Capture Rate Comparison', fontsize=14, fontweight='bold')
        ax.set_xticks(x_pos)
        ax.set_xticklabels(cases)
        ax.set_ylim(0, 100)
        ax.grid(True, alpha=0.3, axis='y')

        # 각 바 위에 값 표시
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2., height,
                   f'{height:.1f}%', ha='center', va='bottom')

        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, filename), dpi=self.dpi)
        plt.close()

    def plot_node_count_vs_displacement(self, results_list, filename='node_count_vs_displacement.png'):
        """
        노드 수 vs 평균 측면 변위

        Args:
            results_list (list): 반복 실험 결과 리스트
            filename (str): 저장 파일명
        """
        fig, ax = plt.subplots(figsize=(10, 6), dpi=self.dpi)

        # 케이스별로 그룹화
        cases = {}
        for result in results_list:
            num_nodes = result['num_nodes']
            if num_nodes not in cases:
                cases[num_nodes] = []
            cases[num_nodes].append(result['mean_displacement'])

        node_counts = sorted(cases.keys())
        means = [np.mean(cases[n]) for n in node_counts]
        stds = [np.std(cases[n]) for n in node_counts]

        ax.errorbar(node_counts, means, yerr=stds, marker='o', markersize=8,
                   capsize=5, capthick=2, linewidth=2, color='blue', label='Mean ± Std')

        ax.set_xlabel('Number of Nodes', fontsize=12)
        ax.set_ylabel('Mean Lateral Displacement (m)', fontsize=12)
        ax.set_title('Effect of Node Count on Deflection', fontsize=14, fontweight='bold')
        ax.set_xticks(node_counts)
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, filename), dpi=self.dpi)
        plt.close()

    def plot_flow_velocity_sensitivity(self, results_dict, filename='flow_velocity_sensitivity.png'):
        """
        유속 민감도 분석 그래프

        Args:
            results_dict (dict): 유속별 결과 딕셔너리
            filename (str): 저장 파일명
        """
        fig, ax = plt.subplots(figsize=(10, 6), dpi=self.dpi)

        velocities = sorted(results_dict.keys())
        capture_rates = [results_dict[v]['capture_rate'] for v in velocities]
        displacements = [results_dict[v]['mean_displacement'] for v in velocities]

        ax2 = ax.twinx()

        line1 = ax.plot(velocities, capture_rates, 'b-o', linewidth=2, markersize=8, label='Capture Rate')
        line2 = ax2.plot(velocities, displacements, 'r-s', linewidth=2, markersize=8, label='Mean Displacement')

        ax.set_xlabel('Flow Velocity (m/s)', fontsize=12)
        ax.set_ylabel('Capture Rate (%)', fontsize=12, color='b')
        ax2.set_ylabel('Mean Displacement (m)', fontsize=12, color='r')
        ax.set_title('Flow Velocity Sensitivity', fontsize=14, fontweight='bold')
        ax.tick_params(axis='y', labelcolor='b')
        ax2.tick_params(axis='y', labelcolor='r')
        ax.grid(True, alpha=0.3)

        # 범례 통합
        lines = line1 + line2
        labels = [l.get_label() for l in lines]
        ax.legend(lines, labels, loc='upper left')

        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, filename), dpi=self.dpi)
        plt.close()

    def plot_phase_gain_effect(self, results_with_phase, results_without_phase,
                              filename='phase_gain_effect.png'):
        """
        위상 정렬 효과 비교 그래프

        Args:
            results_with_phase (list): 위상 적용 결과
            results_without_phase (list): 위상 미적용 결과
            filename (str): 저장 파일명
        """
        fig, ax = plt.subplots(figsize=(10, 6), dpi=self.dpi)

        cases = ['No Phase', 'Phase Aligned']
        with_phase_mean = np.mean([r['mean_displacement'] for r in results_with_phase])
        without_phase_mean = np.mean([r['mean_displacement'] for r in results_without_phase])

        with_phase_std = np.std([r['mean_displacement'] for r in results_with_phase])
        without_phase_std = np.std([r['mean_displacement'] for r in results_without_phase])

        means = [without_phase_mean, with_phase_mean]
        stds = [without_phase_std, with_phase_std]

        x_pos = np.arange(len(cases))
        bars = ax.bar(x_pos, means, yerr=stds, capsize=5, color=['blue', 'red'], alpha=0.7)

        ax.set_ylabel('Mean Lateral Displacement (m)', fontsize=12)
        ax.set_title('Phase Alignment Effect on Deflection', fontsize=14, fontweight='bold')
        ax.set_xticks(x_pos)
        ax.set_xticklabels(cases)
        ax.grid(True, alpha=0.3, axis='y')

        # 각 바 위에 값 표시
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2., height,
                   f'{height:.4f}', ha='center', va='bottom')

        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, filename), dpi=self.dpi)
        plt.close()
