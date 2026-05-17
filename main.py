# main.py
# 메인 실행 파일 - 전체 시뮬레이션 관리

import numpy as np
import pandas as pd
import os
import sys
from datetime import datetime

import config
from simulation import ParticleSimulation
from metrics import MetricsCalculator, StatisticalAnalysis
from visualization import Visualizer


def run_simulation_case(case_name, nodes_config, num_replicates, use_phase_gain=False):
    """
    한 케이스에 대해 여러 번 반복 실험 수행

    Args:
        case_name (str): 케이스 이름
        nodes_config (list): 노드 설정
        num_replicates (int): 반복 횟수
        use_phase_gain (bool): 위상 보정 적용 여부

    Returns:
        dict: 결과 딕셔너리
    """
    print(f"\n[{case_name}] Running {num_replicates} replicates...", end=' ')

    results = []
    trajectories_list = []
    final_positions_list = []

    for rep in range(num_replicates):
        # 시뮬레이션 생성 및 초기화
        sim = ParticleSimulation(
            channel_length=config.CHANNEL_LENGTH,
            channel_width=config.CHANNEL_WIDTH,
            num_particles=config.NUM_PARTICLES,
            dt=config.DT,
            total_time=config.TOTAL_TIME,
            flow_velocity=config.FLOW_VELOCITY_DEFAULT,
            noise_sigma=config.NOISE_SIGMA,
            nodes_config=nodes_config
        )

        sim.initialize_particles(random_seed=None)

        # 시뮬레이션 실행
        sim.run(
            use_phase_gain=use_phase_gain,
            target_phase=config.PHASE_TARGET,
            k_phase=config.K_PHASE,
            k_interference=config.K_INTERFERENCE
        )

        # 결과 수집
        initial_pos = sim.get_initial_positions()
        final_pos = sim.get_final_positions()
        trajectories = sim.get_trajectories()

        # 지표 계산
        metrics_calc = MetricsCalculator(
            capture_zone_x_min=config.CAPTURE_ZONE_X_MIN,
            capture_zone_y_min=config.CAPTURE_ZONE_Y_MIN,
            channel_length=config.CHANNEL_LENGTH,
            channel_width=config.CHANNEL_WIDTH
        )

        metrics = metrics_calc.get_all_metrics(initial_pos, final_pos, nodes_config, use_phase_gain)
        results.append(metrics)

        # 첫 번째 반복의 궤적만 저장 (시각화용)
        if rep == 0:
            trajectories_list.append(trajectories)
            final_positions_list.append(final_pos)

        sys.stdout.write('.')
        sys.stdout.flush()

    print(' Done!')

    # 평균 계산
    mean_metrics = {}
    for key in results[0].keys():
        if isinstance(results[0][key], (int, float)):
            mean_metrics[f'{key}_mean'] = np.mean([r[key] for r in results])
            mean_metrics[f'{key}_std'] = np.std([r[key] for r in results])

    return {
        'case_name': case_name,
        'replicates': results,
        'mean_metrics': mean_metrics,
        'trajectories': trajectories_list[0] if trajectories_list else None,
        'final_positions': final_positions_list[0] if final_positions_list else None,
        'nodes_config': nodes_config
    }


def run_all_cases():
    """모든 실험 케이스 실행"""
    print("=" * 70)
    print("AquaDAN Particle Deflection Simulation")
    print("=" * 70)
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Number of Particles: {config.NUM_PARTICLES}")
    print(f"Simulation Time: {config.TOTAL_TIME} s")
    print(f"Number of Replicates: {config.NUM_REPLICATES}")

    # 시각화 준비
    visualizer = Visualizer(output_dir=config.OUTPUT_DIR, dpi=config.FIGURE_DPI)

    # ==================== Case 0: 음향 OFF ====================
    case0_results = run_simulation_case(
        'Case 0: Acoustic OFF',
        config.NODES_CASE0,
        config.NUM_REPLICATES,
        use_phase_gain=False
    )

    # ==================== Case 1: 단일 노드 ====================
    case1_results = run_simulation_case(
        'Case 1: Single Node',
        config.NODES_CASE1,
        config.NUM_REPLICATES,
        use_phase_gain=False
    )

    # ==================== Case 2: 3개 노드 ====================
    case2_results = run_simulation_case(
        'Case 2: Three Nodes',
        config.NODES_CASE2,
        config.NUM_REPLICATES,
        use_phase_gain=False
    )

    # ==================== Case 3: 5개 노드 ====================
    case3_results = run_simulation_case(
        'Case 3: Five Nodes',
        config.NODES_CASE3,
        config.NUM_REPLICATES,
        use_phase_gain=False
    )

    # ==================== Case 4: 5개 노드 + 위상 정렬 ====================
    case4_results = run_simulation_case(
        'Case 4: Five Nodes + Phase Aligned',
        config.NODES_CASE3,
        config.NUM_REPLICATES,
        use_phase_gain=True
    )

    # 결과 저장
    all_results = {
        'OFF': case0_results,
        'SINGLE': case1_results,
        'THREE': case2_results,
        'FIVE': case3_results,
        'FIVE_PHASE': case4_results
    }

    # ==================== 시각화 ====================
    print("\n" + "=" * 70)
    print("Generating Visualizations...")

    for case_key, result in all_results.items():
        if result['trajectories'] is not None:
            node_positions = np.array([
                [n['x'], n['y']] for n in result['nodes_config']
            ]) if result['nodes_config'] else np.empty((0, 2))

            visualizer.plot_trajectories(
                result['trajectories'],
                config.CHANNEL_LENGTH,
                config.CHANNEL_WIDTH,
                node_positions,
                config.CAPTURE_ZONE_X_MIN,
                config.CAPTURE_ZONE_Y_MIN,
                filename=f'{case_key.lower()}_trajectories.png',
                title=f'{result["case_name"]} Trajectories'
            )

    # 비교 그래프
    results_dict = {
        case_key: {
            'mean_displacement': result['mean_metrics']['mean_displacement_mean'],
            'std_displacement': result['mean_metrics']['mean_displacement_std'],
            'capture_rate': result['mean_metrics']['capture_rate_mean']
        }
        for case_key, result in all_results.items()
    }

    visualizer.plot_displacement_comparison(results_dict)
    visualizer.plot_capture_rate_comparison(results_dict)

    # 노드 수 vs 편향
    all_results_list = []
    for result in all_results.values():
        for rep in result['replicates']:
            all_results_list.append(rep)

    visualizer.plot_node_count_vs_displacement(all_results_list)

    # 위상 정렬 효과
    visualizer.plot_phase_gain_effect(
        case4_results['replicates'],
        case3_results['replicates']
    )

    # ==================== 통계 분석 ====================
    print("Performing Statistical Tests...")

    stat_analyzer = StatisticalAnalysis()

    # Case 0 vs 다른 케이스 t-test
    case0_displacement = [r['mean_displacement'] for r in case0_results['replicates']]

    print("\nT-Tests (Case 0 vs Others):")
    print(f"  Case 0 mean: {np.mean(case0_displacement):.6f} ± {np.std(case0_displacement):.6f} m")

    t_test_results = {}
    for case_key in ['SINGLE', 'THREE', 'FIVE', 'FIVE_PHASE']:
        case_displacement = [r['mean_displacement'] for r in all_results[case_key]['replicates']]
        t_result = stat_analyzer.t_test(case0_displacement, case_displacement)
        t_test_results[case_key] = t_result
        print(f"  {case_key}: t={t_result['t_statistic']:.4f}, p={t_result['p_value']:.6f}, "
              f"Significant={t_result['significant']}")

    # ANOVA
    print("\nANOVA (All Cases):")
    groups = [
        [r['mean_displacement'] for r in all_results[key]['replicates']]
        for key in all_results.keys()
    ]
    anova_result = stat_analyzer.anova(*groups)
    print(f"  F={anova_result['f_statistic']:.4f}, p={anova_result['p_value']:.6f}, "
          f"Significant={anova_result['significant']}")

    # ==================== 결과 요약 ====================
    print("\n" + "=" * 70)
    print("SIMULATION RESULTS SUMMARY")
    print("=" * 70)

    summary_data = []
    for case_key, result in all_results.items():
        metrics = result['mean_metrics']
        summary_data.append({
            'Case': case_key,
            'Num_Nodes': len(result['nodes_config']),
            'With_Phase': result['replicates'][0]['with_phase'],
            'Mean_Displacement (m)': metrics.get('mean_displacement_mean', 0),
            'Std_Displacement (m)': metrics.get('mean_displacement_std', 0),
            'Capture_Rate (%)': metrics.get('capture_rate_mean', 0),
            'Concentration_Factor': metrics.get('concentration_factor_mean', 0),
            'Energy_Efficiency': metrics.get('energy_efficiency_mean', 0)
        })

    summary_df = pd.DataFrame(summary_data)
    print(summary_df.to_string(index=False))

    # CSV 저장
    summary_df.to_csv(os.path.join(config.OUTPUT_DIR, 'simulation_results.csv'), index=False)
    print(f"\nResults saved to: {config.OUTPUT_DIR}")

    # ==================== 해석 ====================
    print("\n" + "=" * 70)
    print("INTERPRETATION")
    print("=" * 70)

    # 긍정적 조건 확인
    positive_conditions = 0

    if t_test_results['SINGLE']['significant']:
        print("[O] Single node shows significant deflection effect")
        positive_conditions += 1
    else:
        print("[X] Single node shows no significant deflection effect")

    if all_results['THREE']['mean_metrics']['mean_displacement_mean'] > \
       all_results['SINGLE']['mean_metrics']['mean_displacement_mean']:
        print("[O] Three nodes show greater deflection than single node")
        positive_conditions += 1
    else:
        print("[X] Three nodes show less/equal deflection compared to single node")

    if all_results['FIVE']['mean_metrics']['capture_rate_mean'] > 0:
        print("[O] Five nodes show capture zone arrival")
        positive_conditions += 1
    else:
        print("[X] Five nodes show no capture zone arrival")

    phase_gain_ratio = (all_results['FIVE_PHASE']['mean_metrics']['mean_displacement_mean'] /
                       (all_results['FIVE']['mean_metrics']['mean_displacement_mean'] + 1e-6))
    if phase_gain_ratio > 1.0:
        print(f"[O] Phase alignment enhances deflection (gain ratio: {phase_gain_ratio:.2f})")
        positive_conditions += 1
    else:
        print(f"[X] Phase alignment does not enhance deflection (gain ratio: {phase_gain_ratio:.2f})")

    if anova_result['significant']:
        print("[O] ANOVA shows significant difference between cases (p < 0.05)")
        positive_conditions += 1
    else:
        print("[X] ANOVA shows no significant difference between cases (p >= 0.05)")

    mean_conc = summary_df['Concentration_Factor'].mean()
    if mean_conc > 1.0:
        print(f"[O] Average concentration factor > 1 ({mean_conc:.2f})")
        positive_conditions += 1
    else:
        print(f"[X] Average concentration factor <= 1 ({mean_conc:.2f})")

    print(f"\n>> Positive conditions met: {positive_conditions}/6")

    if positive_conditions >= 3:
        print("\n[SUCCESS] Initial feasibility is indicated by the simulation.")
        print("  The multi-node acoustic deflection system shows potential for")
        print("  guiding particles toward the capture zone.")
    else:
        print("\n[LIMITED] Limited feasibility indicated in this 2D model.")
        print("  Further investigation in low-velocity zones or controlled")
        print("  environments is recommended.")

    print("\n" + "=" * 70)
    print(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)


if __name__ == '__main__':
    # 출력 디렉토리 생성
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)

    # 시뮬레이션 실행
    run_all_cases()
