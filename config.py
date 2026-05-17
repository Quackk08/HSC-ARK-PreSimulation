# config.py
# 시뮬레이션 전역 설정 파일

# ==================== 수역 설정 ====================
CHANNEL_LENGTH = 1.2  # m
CHANNEL_WIDTH = 0.4   # m

# ==================== 입자 설정 ====================
NUM_PARTICLES = 300   # 입자 개수
DT = 0.01             # 시간 간격 (s)
TOTAL_TIME = 20.0     # 총 시뮬레이션 시간 (s)

# ==================== 기본 유속 ====================
FLOW_VELOCITY_DEFAULT = 0.10  # m/s
FLOW_VELOCITY_RANGE = [0.05, 0.10, 0.15, 0.20]  # 민감도 분석용

# ==================== 노이즈 설정 ====================
NOISE_SIGMA = 0.005   # Gaussian noise 표준편차 (m/s)

# ==================== 회수 구역 설정 ====================
# 회수 구역: x > 1.05 m and y > 0.30 m
CAPTURE_ZONE_X_MIN = 1.05
CAPTURE_ZONE_Y_MIN = 0.30

# ==================== 노드 설정 ====================
# Case 0: 음향 OFF
NODES_CASE0 = []

# Case 1: 단일 노드
NODES_CASE1 = [
    {
        'x': 0.60,
        'y': 0.20,
        'strength': 0.05,      # 유도 강도 (m/s)
        'radius': 0.25,        # 영향 반경 (m)
        'phase': 0.0,          # 위상 (rad)
        'direction': (0, 1)    # 방향: y축 양의 방향
    }
]

# Case 2: 3개 노드 사선 배열
NODES_CASE2 = [
    {
        'x': 0.35,
        'y': 0.15,
        'strength': 0.05,
        'radius': 0.25,
        'phase': 0.0,
        'direction': (0, 1)
    },
    {
        'x': 0.60,
        'y': 0.22,
        'strength': 0.05,
        'radius': 0.25,
        'phase': 0.0,
        'direction': (0, 1)
    },
    {
        'x': 0.85,
        'y': 0.29,
        'strength': 0.05,
        'radius': 0.25,
        'phase': 0.0,
        'direction': (0, 1)
    }
]

# Case 3: 5개 노드 사선 배열
NODES_CASE3 = [
    {
        'x': 0.20,
        'y': 0.08,
        'strength': 0.05,
        'radius': 0.25,
        'phase': 0.0,
        'direction': (0, 1)
    },
    {
        'x': 0.40,
        'y': 0.15,
        'strength': 0.05,
        'radius': 0.25,
        'phase': 0.0,
        'direction': (0, 1)
    },
    {
        'x': 0.60,
        'y': 0.22,
        'strength': 0.05,
        'radius': 0.25,
        'phase': 0.0,
        'direction': (0, 1)
    },
    {
        'x': 0.80,
        'y': 0.29,
        'strength': 0.05,
        'radius': 0.25,
        'phase': 0.0,
        'direction': (0, 1)
    },
    {
        'x': 1.00,
        'y': 0.36,
        'strength': 0.05,
        'radius': 0.25,
        'phase': 0.0,
        'direction': (0, 1)
    }
]

# ==================== 위상 정렬 설정 ====================
ENABLE_PHASE_GAIN = True
K_PHASE = 0.3         # 위상 정렬 효과 강도 (0~0.5)
PHASE_TARGET = 0.0    # 목표 위상 (rad)
K_INTERFERENCE = 0.2  # 노드 간 간섭 계수

# ==================== 실험 케이스 ====================
CASES = {
    'OFF': NODES_CASE0,
    'SINGLE': NODES_CASE1,
    'THREE': NODES_CASE2,
    'FIVE': NODES_CASE3
}

# ==================== 반복 실험 ====================
NUM_REPLICATES = 10  # 각 케이스별 반복 횟수

# ==================== 시각화 설정 ====================
OUTPUT_DIR = './output/'
FIGURE_DPI = 300
