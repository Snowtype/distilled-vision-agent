# 🎮 Distilled Vision Agent: YOLO, You Only Live Once

**Team: Prof.Peter.backward()**

| 팀원           | UNI    | 역할                          | 담당 모듈                                                                            |
| -------------- | ------ | ----------------------------- | ------------------------------------------------------------------------------------ |
| **Jeewon Kim** | jk4864 | 컴퓨터 비전 & YOLOv8          | `src/models/yolo_detector.py`<br>`web_app/modules/cv_module.py`                      |
| **Chloe Lee**  | cl4490 | 강화학습 & PPO/DQN            | `src/training/ppo_trainer.py`<br>`web_app/modules/ai_module.py`                      |
| **Minsuk Kim** | mk4434 | 웹 플랫폼 & 데이터 파이프라인 | `web_app/app.py`<br>`src/data/augmentation.py`<br>`src/deployment/onnx_optimizer.py` |

## 🌐 Live Demo

**웹 게임 플랫폼**: https://distilled-vision-agent-fhuhwhnu3a-uc.a.run.app

- **Human Mode**: 직접 플레이하며 전문가 시연 데이터 수집
- **AI Mode**: AI 에이전트의 실시간 플레이 관찰
- **Leaderboard**: 전 세계 플레이어 순위

## 📝 Project Overview

**목표**: Vision-based Deep Learning Agent가 2D 게임을 순수 시각 정보만으로 학습하고 플레이

**핵심 파이프라인**:

```
RGB 프레임 → YOLO 탐지 → MLP 정책 네트워크→ 액션 결정
```

### Key Features

- 🎯 **Real-time Performance**: 60 FPS 목표 (≤16.7ms/frame)
- 👁️ **Vision-Only Input**: 게임 내부 상태 접근 없이 순수 RGB 이미지만 사용
- 🧠 **Dual Learning**: Policy Distillation + Self-Play RL
- 🚀 **End-to-End Pipeline**: 데이터 수집 → 훈련 → 배포
- ☁️ **Cloud Deployment**: GCP Cloud Run 실시간 서비스

## 📁 Project Structure

```
final_project/
├── 📱 web_app/                      # 웹 게임 플랫폼 (완성)
│   ├── app.py                       # Flask 서버 (메인)
│   ├── app_modular.py               # 모듈화 버전
│   ├── modules/                     # 팀원별 모듈
│   │   ├── game_engine.py          # 공통 게임 로직 (수정 금지)
│   │   ├── cv_module.py            # 👁️ Jeewon - YOLO 통합
│   │   ├── ai_module.py            # 🤖 Chloe - PPO/DQN 통합
│   │   └── web_session.py          # 🔗 Minsuk - 세션 관리
│   ├── templates/                   # HTML UI
│   ├── static/                      # CSS/JS
│   ├── collected_gameplay/          # 수집된 게임 데이터
│   │   └── session_*/
│   │       ├── metadata.json        # 세션 정보
│   │       ├── states_actions.jsonl # RL 훈련 데이터
│   │       ├── bboxes.jsonl        # YOLO 라벨 데이터
│   │       └── frames/             # RGB 프레임 (구현 중)
│   ├── Dockerfile                   # GCP 배포 설정
│   └── requirements.txt
│
├── 🔬 src/                          # 소스 코드 모듈
│   ├── data/                        # 데이터 파이프라인 (완성)
│   │   ├── __init__.py
│   │   └── augmentation.py         # GameFrameAugmenter
│   ├── models/                      # 모델 (통합 대기)
│   │   ├── yolo_detector.py        # 🚧 Jeewon 작업 필요
│   │   └── policy_network.py       # 🚧 Chloe 작업 필요
│   ├── training/                    # 훈련 파이프라인 (통합 대기)
│   │   ├── train_yolo.py           # 🚧 Jeewon 작업 필요
│   │   ├── train_policy.py         # 🚧 Jeewon 작업 필요
│   │   ├── ppo_trainer.py          # 🚧 Chloe 작업 필요
│   │   └── data_loader.py          # 🚧 Chloe 작업 필요
│   ├── utils/                       # 유틸리티 (완성)
│   │   ├── __init__.py
│   │   ├── visualization.py        # GameVisualizer
│   │   └── rl_instrumentation.py   # RLInstrumentationLogger
│   └── deployment/                  # 배포 최적화 (완성)
│       ├── __init__.py
│       └── onnx_optimizer.py       # ONNXModelOptimizer
│
├── 📊 data/                         # 데이터셋 저장소
│   ├── raw/                        # 원본 게임플레이 기록
│   ├── labeled/                    # YOLO 포맷 라벨
│   └── augmented/                  # 증강된 훈련 데이터
│
├── 🧪 scripts/                      # 테스트 스크립트 (완성)
│   ├── simple_test.py              # 의존성 없는 기본 테스트
│   ├── test_core_logic.py          # 핵심 알고리즘 테스트
│   └── test_pipeline.py            # 전체 파이프라인 테스트
│
├── 🎮 Game/                         # 원형 게임 환경
│   ├── game_agent.py               # 게임 에이전트 프로토타입
│   ├── interactive_game.py         # 대화형 게임
│   └── requirements.txt
│
├── 📚 docs/                         # 문서 및 보고서
├── configs/                         # 훈련 설정 파일
└── 📋 Documentation Files
    ├── README.md                    # 이 파일
    ├── TEAM_BRIEFING.md            # 팀 현황 브리핑
    ├── IMPLEMENTATION_ROADMAP.md   # 구현 로드맵
    ├── TEAM_INTEGRATION.md         # 팀 통합 가이드
    ├── DATA_STRATEGY.md            # 데이터 전략
    └── web_app/
        ├── DATA_COLLECTION_GUIDE.md # 데이터 수집 가이드
        └── TEAM_GUIDE.md           # 팀원별 작업 가이드
```

## Quick Start

### Option 1: Full Installation (Recommended)

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run full test suite
python scripts/test_pipeline.py

# Run current prototype
cd Game
python game_agent.py
```

### Option 2: Core Logic Testing (No Dependencies)

```bash
# Test basic functionality without external packages
python3 scripts/simple_test.py

# Test core algorithms
python3 scripts/test_core_logic.py
```

### Verified Working Components ✅

- **Data Augmentation**: Algorithmic logic tested and working
- **Visualization Tools**: Core rendering and profiling logic verified
- **Performance Profiling**: Timing and FPS calculation systems operational
- **RL Instrumentation**: Episode logging and analysis systems functional
- **ONNX Optimization**: Model export and inference pipeline logic validated

## 🗓️ Development Roadmap & Team Responsibilities

### ✅ Phase 1: 인프라 & 데이터 수집 (Minsuk - 완료)

**완성된 작업**:

- ✅ 웹 게임 플랫폼 (Flask + SocketIO)
- ✅ GCP Cloud Run 배포
- ✅ 데이터 수집 파이프라인 (State-Action-Reward, Bounding Boxes)
- ✅ 데이터 증강 시스템 (`src/data/augmentation.py`)
- ✅ ONNX 최적화 도구 (`src/deployment/onnx_optimizer.py`)
- ✅ 시각화 & 프로파일링 도구 (`src/utils/`)

**진행 중**:

- 🚧 RGB 프레임 캡처 구현 (Canvas → PNG 저장)
- 🚧 전문가 시연 데이터 수집 (50+ 세션)

---

### 🔴 Phase 2: 컴퓨터 비전 (Jeewon - 시작 필요)

**담당 파일**:

- `src/models/yolo_detector.py` - YOLOv8 모델 래퍼
- `src/training/train_yolo.py` - YOLOv8 훈련 스크립트
- `src/training/train_policy.py` - Policy Distillation 구현
- `web_app/modules/cv_module.py` - 웹 통합 모듈

**작업 내용**:

1. **YOLOv8 훈련** (1-2일)

   - [ ] `bboxes.jsonl` → YOLO 포맷 변환
   - [ ] YOLOv8 훈련 (목표: mAP ≥ 70%)
   - [ ] 모델 검증 및 평가
   - [ ] ONNX 내보내기

2. **Policy Distillation** (1일)

   - [ ] 전문가 시연 데이터 로드
   - [ ] MLP 정책 네트워크 훈련
   - [ ] 목표: ≥75% action agreement

3. **웹 통합** (0.5일)
   - [ ] `cv_module.py`에 실제 YOLO 추론 구현
   - [ ] 실시간 성능 테스트 (60 FPS 목표)

**Input 데이터**:

- `web_app/collected_gameplay/session_*/frames/` (RGB 프레임)
- `web_app/collected_gameplay/session_*/bboxes.jsonl` (라벨)

**Output**:

- `models/yolo_best.pt` - 훈련된 YOLO 모델
- `models/yolo_best.onnx` - 최적화된 ONNX 모델
- `models/policy_distilled.pt` - 정책 네트워크

---

### 🟣 Phase 3: 강화학습 (Chloe - 즉시 시작 가능)

**담당 파일**:

- `src/training/ppo_trainer.py` - PPO/DQN 훈련 구현
- `src/training/data_loader.py` - RL 데이터 로더
- `src/models/policy_network.py` - 정책 네트워크 아키텍처
- `web_app/modules/ai_module.py` - 웹 통합 모듈

**작업 내용**:

1. **데이터 로더 구현** (0.5일)

   - [ ] `states_actions.jsonl` 읽기
   - [ ] Replay Buffer 구현
   - [ ] 데이터 전처리 파이프라인

2. **PPO/DQN 훈련** (1-2일)

   - [ ] State-based 정책 먼저 구현
   - [ ] Self-Play 환경 구축
   - [ ] 목표: ≥20% 생존 시간 향상

3. **Vision-based RL** (선택, 1일)

   - [ ] YOLO 출력 → RL 입력 변환
   - [ ] End-to-End Vision-based 정책

4. **웹 통합** (0.5일)
   - [ ] `ai_module.py`에 실제 PPO/DQN 추론 구현
   - [ ] 실시간 의사결정 테스트

**Input 데이터**:

- `web_app/collected_gameplay/session_*/states_actions.jsonl` (즉시 사용 가능)
- `web_app/collected_gameplay/session_*/frames/` (Vision-based용, 선택)

**Output**:

- `models/ppo_agent.zip` - 훈련된 PPO 에이전트
- `models/ppo_agent.onnx` - 최적화된 정책

---

### 🔵 Phase 4: 통합 & 최적화 (All Team - 협업)

**작업 내용**:

- [ ] End-to-End 파이프라인 통합 테스트 (Minsuk 주도)
- [ ] 60 FPS 성능 벤치마크 (Minsuk)
- [ ] 최종 모델 검증 (Jeewon + Chloe)
- [ ] GCP 배포 업데이트 (Minsuk)
- [ ] 문서화 & 보고서 작성 (All)

**예상 시간**: 1-2일

---

### 📊 팀원별 예상 작업 시간

| 팀원       | Phase   | 작업                | 예상 시간 | 우선순위    |
| ---------- | ------- | ------------------- | --------- | ----------- |
| **Minsuk** | Phase 1 | RGB 프레임 캡처     | 3-4시간   | 🔴 Critical |
| **Minsuk** | Phase 1 | 전문가 데이터 수집  | 2-3시간   | 🔴 Critical |
| **Jeewon** | Phase 2 | YOLO 훈련 & 통합    | 2-3일     | 🔴 Critical |
| **Chloe**  | Phase 3 | PPO/DQN 훈련 & 통합 | 2-3일     | 🔴 Critical |
| **All**    | Phase 4 | 통합 & 최적화       | 1-2일     | 🟡 High     |

**총 예상 프로젝트 완성 시간**: 5-7일

## 📊 Data Collection System

### 🎮 Web Application for Data Collection

A Flask-based web application is provided to collect training data from real gameplay:

```bash
cd web_app
python app.py
# Access at http://localhost:5000
```

**Features**:

- **Human Mode**: Play manually to collect expert demonstrations
- **AI Mode**: Observe AI behavior and collect diverse gameplay
- **Automatic Save**: Game sessions are automatically saved to `collected_data/`
- **Real-time Stats**: Monitor FPS, score, and data collection status

### 📤 Export Training Datasets

After collecting gameplay data, export datasets for training:

**For YOLO Training (Jeewon)**:

```bash
curl -X POST http://localhost:5000/api/data/export/yolo
# → Creates training_exports/yolo_dataset/ with images + labels
```

**For RL Training (Chloe)**:

```bash
curl -X POST http://localhost:5000/api/data/export/rl
# → Creates training_exports/rl_dataset/ with observations, actions, rewards
```

**Check Collection Stats**:

```bash
curl http://localhost:5000/api/data/stats
```

📖 **Detailed Guide**: See [web_app/DATA_COLLECTION_GUIDE.md](web_app/DATA_COLLECTION_GUIDE.md) for complete documentation.

### 🔒 Security Note

- GCP credentials (`.json` files) are automatically excluded from Git via `.gitignore`
- Training data folders (`collected_data/`, `training_exports/`) are not pushed to GitHub
- Share exported datasets with team via Google Drive or GCS buckets

## 🎯 Success Criteria (Project Evaluation)

| 기준                      | 목표                  | 담당자 | 현재 상태      | 중요도      |
| ------------------------- | --------------------- | ------ | -------------- | ----------- |
| **Detection Quality**     | mAP ≥ 70%             | Jeewon | ❌ 0% (미시작) | 🔴 Critical |
| **Imitation Accuracy**    | ≥75% action agreement | Jeewon | ❌ 0% (미시작) | 🔴 Critical |
| **Performance Gain**      | ≥20% survival time ↑  | Chloe  | ❌ 0% (미시작) | 🔴 Critical |
| **Real-time Performance** | ≥60 FPS inference     | All    | ⚠️ 30 FPS (웹) | 🟡 High     |
| **Data Collection**       | ≥5,000 frames         | Minsuk | 🟡 ~500 frames | 🔴 Critical |

---

## 🔗 Git & Collaboration

### **Git 브랜치 상태** (2025-11-18 기준)

```bash
# 현재 최신 브랜치: main (91aebe3)
* main                    ✅ 최신 (데이터 수집 시스템 완성)
  team/main              ✅ 동기화됨
  team/chloe             ⏸️ 오래된 커밋 (병합 필요)
  team/jeewon            ⏸️ 오래된 커밋 (병합 필요)
  team/minsuk-web-deployment  ✅ 웹 배포 완료
```

### **팀원별 작업 브랜치 전략**

```bash
# Jeewon - YOLO 작업용
git checkout -b jeewon-cv-module
# 작업 후: git push origin jeewon-cv-module

# Chloe - RL 작업용
git checkout -b chloe-ai-module
# 작업 후: git push origin chloe-ai-module

# 병합 시
git checkout main
git pull origin main
git merge jeewon-cv-module  # 또는 chloe-ai-module
git push origin main
```

### **팀 저장소**

- **Team Repo**: https://github.com/gitgutgit/YOLO-You-Only-Live-Once
- **Minsuk Personal**: https://github.com/Snowtype/distilled-vision-agent

---

## 📚 Additional Documentation

| 문서                                 | 설명                       | 위치             |
| ------------------------------------ | -------------------------- | ---------------- |
| **TEAM_BRIEFING.md**                 | 팀 현황 & 다음 단계 브리핑 | `final_project/` |
| **IMPLEMENTATION_ROADMAP.md**        | 상세 구현 로드맵           | `final_project/` |
| **TEAM_INTEGRATION.md**              | 팀 통합 가이드             | `final_project/` |
| **DATA_STRATEGY.md**                 | 데이터 저장 전략           | `final_project/` |
| **web_app/DATA_COLLECTION_GUIDE.md** | 데이터 수집 상세 가이드    | `web_app/`       |
| **web_app/TEAM_GUIDE.md**            | 팀원별 모듈 작업 가이드    | `web_app/`       |

---

## 🚨 Critical Next Steps (우선순위 순)

### 🔴 **즉시 필요 (이번 주)**

1. **Minsuk**: RGB 프레임 캡처 구현 (3-4시간)

   - Canvas → PNG 저장 기능 추가
   - `collected_gameplay/session_*/frames/` 디렉토리 생성

2. **Jeewon**: YOLO 훈련 준비 시작

   - 데이터 변환 스크립트 작성
   - YOLOv8 환경 설정

3. **Chloe**: RL 데이터 로더 구현
   - `states_actions.jsonl` 읽기 코드 작성
   - PPO/DQN 환경 설정

### 🟡 **다음 단계 (다음 주)**

4. **Jeewon**: YOLOv8 훈련 & 평가 (2-3일)
5. **Chloe**: PPO/DQN 훈련 & 평가 (2-3일)
6. **All**: 통합 테스트 & 최적화 (1-2일)

---

## 🤝 Team Communication

### **연락 방법**

- **GitHub Issues**: 기술적 질문 & 버그 리포트
- **Pull Requests**: 코드 리뷰 & 병합
- **팀 미팅**: 주 2회 진행 상황 공유

### **팀원 정보**

- **Jeewon Kim (jk4864)**: 컴퓨터 비전 전문
- **Chloe Lee (cl4490)**: 강화학습 전문
- **Minsuk Kim (mk4434)**: 웹 개발 & MLOps

---

## 📋 License

Academic project for **COMS W4995 - Deep Learning for Computer Vision**, Columbia University

**Team: Prof.Peter.backward()**  
**Fall 2025**
