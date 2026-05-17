# AquaDAN 음향 기반 미세오염물 입자 유도 시뮬레이션

## 프로젝트 개요

본 프로젝트는 AquaDAN 시스템의 핵심 가설을 Python 기반 2D 입자 추적 시뮬레이션으로 검증합니다.

**핵심 가설:**
다중 음향 노드를 사선 방향으로 배치하고 위상·공명·음향장 중첩 효과를 반영하면, 미세오염물 입자의 측면 편향 이동이 누적되어 강 또는 수로의 가장자리 회수 구역으로 유도될 수 있다.

## 프로젝트 구조

```
SIMULATION/
├── config.py              # 전역 설정 파일
├── nodes.py              # 음향 노드 클래스
├── simulation.py         # 입자 추적 시뮬레이션
├── metrics.py           # 평가 지표 계산
├── visualization.py     # 결과 시각화
├── main.py             # 메인 실행 파일
├── README.md           # 이 파일
└── output/             # 결과 저장 디렉토리 (자동 생성)
    ├── *.png           # 그래프 이미지
    ├── simulation_results.csv  # 결과 CSV
    └── ...
```

## 설치 및 실행

### 필수 라이브러리

```bash
pip install numpy scipy matplotlib pandas
```

### 기본 실행

```bash
python main.py
```

## 설정 파일 (config.py)

주요 설정 변수:

- `NUM_PARTICLES`: 입자 개수 (기본: 300)
- `TOTAL_TIME`: 시뮬레이션 총 시간 (기본: 20 s)
- `FLOW_VELOCITY_DEFAULT`: 기본 유속 (기본: 0.10 m/s)
- `NOISE_SIGMA`: 난류 노이즈 강도 (기본: 0.005 m/s)
- `NUM_REPLICATES`: 반복 실험 횟수 (기본: 10)

커스터마이징하려면 `config.py`의 값들을 수정하세요.

## 실험 케이스

시뮬레이션은 다음 5가지 케이스를 자동으로 실행합니다:

1. **Case 0: Acoustic OFF**
   - 음향 노드 없음
   - 기준선 역할

2. **Case 1: Single Node**
   - 1개의 음향 노드
   - 단일 노드 효과 확인

3. **Case 2: Three Nodes**
   - 3개의 음향 노드 (사선 배열)
   - 다중 노드 릴레이 효과

4. **Case 3: Five Nodes**
   - 5개의 음향 노드 (사선 배열)
   - 노드 수 증가 효과

5. **Case 4: Five Nodes + Phase Aligned**
   - 5개 노드 + 위상 정렬
   - 위상 보강 효과 검증

## 평가 지표

각 케이스에 대해 다음 지표들을 계산합니다:

- **평균 측면 변위 (Mean Lateral Displacement)**
  - 초기 y 좌표 대비 최종 y 좌표의 변화량
  - 음향 유도 효과의 주요 지표

- **회수 구역 도달률 (Capture Rate)**
  - 최종적으로 회수 구역에 도달한 입자의 비율 (%)

- **농축 계수 (Concentration Factor)**
  - 회수 구역에서의 입자 밀도 / 전체 평균 밀도
  - C > 1이면 입자가 농축된 상태

- **에너지 효율 (Energy Efficiency)**
  - 에너지 입력 대비 측면 변위

- **위상 보강 계수 (Phase Gain Ratio)**
  - 위상 정렬 조건 vs 미정렬 조건의 편향 비율

## 통계 분석

자동으로 다음 통계 분석을 수행합니다:

- **t-test**: Case 0 vs 다른 케이스들
- **ANOVA**: 모든 케이스 간 평균 차이 검정
- **상관 분석**: 변수 간 상관관계

## 출력 결과

### 그래프 파일 (output 디렉토리)

- `off_trajectories.png` - 음향 OFF 궤적
- `single_trajectories.png` - 단일 노드 궤적
- `three_trajectories.png` - 3개 노드 궤적
- `five_trajectories.png` - 5개 노드 궤적
- `five_phase_trajectories.png` - 위상 정렬 궤적
- `mean_displacement_comparison.png` - 측면 변위 비교
- `capture_rate_comparison.png` - 회수율 비교
- `node_count_vs_displacement.png` - 노드 수 vs 편향
- `phase_gain_effect.png` - 위상 정렬 효과

### 데이터 파일

- `simulation_results.csv` - 모든 평가 지표

### 콘솔 출력

- 각 케이스별 평균 지표
- 통계 검정 결과 (t-test, ANOVA)
- 최종 해석 및 결론

## 해석 기준

다음 중 **3개 이상**을 만족하면 초기 가능성이 있다고 평가합니다:

1. Acoustic ON 조건에서 OFF 대비 평균 측면 변위가 유의미하게 증가 (p < 0.05)
2. 3개 노드가 단일 노드보다 더 큰 평균 측면 변위를 보임
3. 5개 노드에서 회수 구역 도달률이 증가
4. 위상 정렬 조건에서 phase gain ratio > 1
5. ANOVA p-value < 0.05
6. 회수 구역 농축 계수 C > 1

## 주의사항

이 Python 모델의 한계:

- 실제 acoustic pressure field를 직접 계산하지 않음
- 3D 난류를 반영하지 않음
- 입자 간 상호작용 단순화
- 음향 감쇠를 단순 모델로 처리
- 실제 트랜스듀서 지향성은 근사 처리

따라서 결과 해석 시:

**부적절한 표현:**
> "실제 하천에서도 동일 수치로 작동한다."

**적절한 표현:**
> "단순화된 2D 모델에서 다중 음향 노드와 위상 정렬이 입자 편향을 강화할 가능성이 확인되었다."

## 파일별 설명

### config.py
- 모든 시뮬레이션 파라미터 중앙 집중식 관리
- 실험 케이스별 노드 배치 정의
- 쉬운 커스터마이징

### nodes.py
- `AcousticNode` 클래스: 개별 음향 노드
- `NodeManager` 클래스: 다중 노드 관리
- 음향 유도 속도, 위상 보정, 간섭 효과 계산

### simulation.py
- `ParticleSimulation` 클래스: 메인 시뮬레이션 엔진
- 입자 초기화, 타임스텝 업데이트
- 기본 유속, 음향 속도, 노이즈 적용
- 경계 조건 처리

### metrics.py
- `MetricsCalculator` 클래스: 평가 지표 계산
- `StatisticalAnalysis` 클래스: 통계 분석 (t-test, ANOVA, 상관분석)

### visualization.py
- `Visualizer` 클래스: 결과 시각화
- 8가지 유형의 그래프 자동 생성
- 고해상도 PNG 저장

### main.py
- 전체 시뮬레이션 오케스트레이션
- 모든 케이스 자동 실행
- 결과 통합 및 해석
- 콘솔 보고서 생성

## 결과 해석 예시

**긍정적 결과:**
```
✓ Single node shows significant deflection effect
✓ Three nodes show greater deflection than single node
✓ Five nodes show capture zone arrival
✓ Phase alignment enhances deflection (gain ratio: 1.35)
✓ ANOVA shows significant difference between cases (p < 0.05)
✓ Average concentration factor > 1 (1.42)

→ Positive conditions met: 6/6
✓ CONCLUSION: Initial feasibility is indicated by the simulation.
```

**부정적 또는 제한적 결과:**
```
✗ Limited feasibility indicated in this 2D model.
  Further investigation in low-velocity zones or controlled
  environments is recommended.
```

## 커스터마이징

### 노드 배치 변경

`config.py`의 `NODES_CASE*` 딕셔너리를 수정:

```python
NODES_CASE2 = [
    {
        'x': 0.35,          # x 좌표 (m)
        'y': 0.15,          # y 좌표 (m)
        'strength': 0.05,   # 유도 강도 (m/s)
        'radius': 0.25,     # 영향 반경 (m)
        'phase': 0.0,       # 위상 (rad)
        'direction': (0, 1) # 방향 벡터
    },
    # ... 더 많은 노드
]
```

### 시뮬레이션 파라미터 변경

`config.py`의 상단 설정값 수정:

```python
NUM_PARTICLES = 500         # 입자 수 증가
TOTAL_TIME = 30.0           # 시뮬레이션 시간 연장
FLOW_VELOCITY_DEFAULT = 0.15 # 유속 변경
NOISE_SIGMA = 0.01          # 난류 강도 증가
```

## 확장 가능성

- 추가 케이스 정의 (예: 다양한 노드 배열)
- 유속 민감도 분석 추가
- 온도/농도 필드 추가
- 3D 모델링 확장
- 실험 데이터와의 검증

## 라이선스

교육 및 연구 목적 사용

## 문의

한화사이언스 챌린지 - AquaDAN 프로젝트
