# 👥 **팀 브리핑: 현재 상태 & 다음 단계**

## 🎯 **프로젝트 목표 복기**

### **제안서 핵심**

> "vision-based deep learning agent that plays a 2D game **purely from raw visual input**"

**파이프라인**:

```
RGB 프레임 → YOLO 탐지 → MLP 정책 → 액션
```

---

## ✅ **현재 완성된 것들 (래리)**

### 1️⃣ **웹 게임 인프라**

- ✅ Flask + SocketIO 실시간 게임
- ✅ GCP Cloud Run 배포: https://distilled-vision-agent-fhuhwhnu3a-uc.a.run.app
- ✅ 리더보드 시스템
- ✅ Human/AI 모드 전환

### 2️⃣ **데이터 수집 파이프라인 (부분 완성)**

```
web_app/collected_gameplay/session_*/
├── metadata.json              ✅ 세션 정보
├── states_actions.jsonl       ✅ State-Action-Reward (클로용)
└── bboxes.jsonl               ✅ Bbox 라벨 (제이용)
```

**수집 중인 데이터**:

- State-Action-Reward 로그 (RL 훈련용)
- Bounding Box 자동 생성 (YOLO 라벨용)
- 게임 통계 (점수, 생존 시간)

### 3️⃣ **인프라 도구**

- ✅ 데이터 증강 (`src/data/augmentation.py`)
- ✅ ONNX 최적화 (`src/deployment/onnx_optimizer.py`)
- ✅ 시각화 도구 (`src/utils/visualization.py`)

---

## ❌ **제안서 대비 부족한 부분**

### 🔴 **Critical - 즉시 필요**

#### **1. RGB 프레임 이미지가 없음!** ⭐⭐⭐

**문제**:

```
현재:   State vector만 저장 (x, y, vy, obstacles)
제안서: "purely from raw visual input" (RGB 프레임)
```

**영향**:

- **제이**: YOLO 훈련 불가능 (이미지 없음)
- **클로**: Vision-based RL 불가능
- **프로젝트**: 핵심 목표 미달성

**해결 중**: 래리가 Canvas 프레임 캡처 구현 예정

---

#### **2. 모델 훈련 미시작**

| 모델                | 담당 | 상태      | 데이터 준비    |
| ------------------- | ---- | --------- | -------------- |
| YOLO                | 제이 | ❌ 미시작 | ⚠️ 프레임 필요 |
| Policy Distillation | 제이 | ❌ 미시작 | ✅ 준비됨      |
| PPO/DQN             | 클로 | ❌ 미시작 | ✅ 준비됨      |

---

## 📊 **현재 저장되는 데이터 상세**

### **1. metadata.json** (세션 정보)

```json
{
  "session_id": "h3Xjmoo_WItEEp6jAAAN",
  "mode": "human",
  "score": 0,
  "survival_time": 4.35,
  "total_frames": 116,
  "final_state": {
    "player_x": 430,
    "player_y": 520,
    "obstacles_count": 8
  }
}
```

### **2. states_actions.jsonl** (클로용 - RL 훈련)

```jsonl
{"frame": 0, "state": {"player_x": 480, "player_y": 360, "player_vy": 0, "obstacles": []}, "action": "stay", "reward": 1.0, "done": false}
{"frame": 1, "state": {"player_x": 480, "player_y": 361, "player_vy": 1, "obstacles": []}, "action": "stay", "reward": 1.0, "done": false}
```

**클로가 할 일**:

```python
# 이 파일을 직접 읽어서 PPO/DQN 훈련
import json

states, actions, rewards = [], [], []
with open('states_actions.jsonl', 'r') as f:
    for line in f:
        data = json.loads(line)
        states.append(data['state'])
        actions.append(data['action'])
        rewards.append(data['reward'])

# → PPO 훈련
```

### **3. bboxes.jsonl** (제이용 - YOLO 라벨)

```jsonl
{"frame": 0, "objects": [{"class": "player", "x": 480, "y": 360, "w": 50, "h": 50}]}
{"frame": 1, "objects": [{"class": "player", "x": 480, "y": 361, "w": 50, "h": 50}, {"class": "obstacle", "x": 120, "y": -50, "w": 50, "h": 50}]}
```

**제이가 할 일**:

```python
# 1. 래리가 프레임 이미지 추가할 때까지 대기
# 2. YOLO 포맷으로 변환 (래리가 스크립트 제공)
# 3. YOLOv8 훈련

from ultralytics import YOLO
model = YOLO('yolov8n.pt')
results = model.train(data='dataset.yaml', epochs=100)
```

---

## 🛠️ **다음 단계 - 우선순위별**

### **🔴 Phase 1: 데이터 완성 (래리) - 진행 중**

#### **작업 1: RGB 프레임 캡처 추가**

```
목표: collected_gameplay/session_*/frames/frame_*.png 생성
예상 시간: 3-4시간
```

#### **작업 2: 전문가 시연 데이터 수집**

```
목표: 50+ 세션, 각 60초 이상 생존
예상 시간: 2-3시간 (웹 게임 반복 플레이)
```

#### **작업 3: 데이터 증강 파이프라인 연결**

```
목표: 1,000 프레임 → 5,000 프레임 (증강)
예상 시간: 2시간
```

---

### **🟢 Phase 2: YOLO & Policy (제이) - 대기 중**

#### **준비 완료**:

- ✅ Bbox 라벨 (`bboxes.jsonl`)
- ⚠️ 프레임 이미지 (래리 작업 대기)

#### **작업 내용**:

1. **YOLO 훈련** (1-2일)

   ```bash
   python scripts/convert_to_yolo.py  # 래리 제공
   python src/models/train_yolo.py    # 제이 작성
   ```

   - 목표: mAP ≥ 70%

2. **Policy Distillation** (1일)
   ```python
   # src/training/train_policy.py
   # Expert 데이터 → MLP 정책
   ```
   - 목표: ≥ 75% action agreement

---

### **🟣 Phase 3: RL 훈련 (클로) - 즉시 시작 가능!**

#### **준비 완료**:

- ✅ State-Action-Reward (`states_actions.jsonl`)
- ✅ 116 프레임 (테스트용)

#### **작업 내용**:

1. **데이터 로더 작성**

   ```python
   # src/training/data_loader.py
   def load_gameplay_sessions(session_dir):
       # states_actions.jsonl 읽기
       # → Replay Buffer 변환
   ```

2. **PPO/DQN 훈련** (1-2일)

   ```python
   # src/training/train_ppo.py
   from stable_baselines3 import PPO

   model = PPO('MlpPolicy', env)
   model.learn(total_timesteps=100000)
   ```

   - 목표: ≥ 20% 생존 시간 향상

**⚠️ 주의**:

- 현재 데이터는 State-based (x, y, vy)
- Vision-based로 전환하려면 YOLO 완성 필요
- 우선 State-based로 시작 권장 (빠른 검증)

---

## 📊 **성공 기준 체크리스트**

| 기준                   | 목표            | 담당 | 현재 상태      |
| ---------------------- | --------------- | ---- | -------------- |
| **Detection Quality**  | ≥70% mAP        | 제이 | ❌ 0% (미시작) |
| **Imitation Accuracy** | ≥75% agreement  | 제이 | ❌ 0% (미시작) |
| **Performance Gain**   | ≥20% survival ↑ | 클로 | ❌ 0% (미시작) |
| **Real-time**          | ≥60 FPS         | 래리 | ⚠️ 30 FPS (웹) |

---

## 🎯 **각자 해야 할 일 요약**

### **래리 (Minsuk)**

```
✅ 완료: 웹 게임, 데이터 수집 파이프라인 (부분)
🔨 진행 중: RGB 프레임 캡처 구현
📋 다음: 전문가 데이터 수집, 증강 파이프라인
```

### **제이 (Jeewon)**

```
⏸️ 대기 중: 프레임 이미지 (래리 작업 완료 시)
📋 준비: YOLO 훈련 코드 작성 시작 가능
📋 다음: YOLOv8 훈련 → Policy Distillation
```

### **클로 (Chloe)**

```
✅ 데이터 준비됨: states_actions.jsonl 사용 가능
🚀 즉시 시작 가능: PPO/DQN 훈련
📋 옵션: State-based 먼저, Vision-based 나중에
```

---

## 📚 **참고 문서**

| 문서                          | 내용             | 위치             |
| ----------------------------- | ---------------- | ---------------- |
| **IMPLEMENTATION_ROADMAP.md** | 상세 구현 계획   | `final_project/` |
| **DATA_STRATEGY.md**          | 데이터 저장 전략 | `final_project/` |
| **README.md**                 | 프로젝트 개요    | `final_project/` |
| **.agent_context/**           | 개발 기록        | `final_project/` |

---

## 💬 **팀원 커뮤니케이션**

### **제이에게**:

```
안녕 제이!

현재 Bbox 라벨 (bboxes.jsonl)은 준비됐어.
하지만 프레임 이미지 (PNG)가 아직 없어서
YOLO 훈련은 조금 기다려야 해.

지금 할 수 있는 것:
1. YOLO 훈련 코드 미리 작성
2. 데이터 변환 로직 준비
3. 내가 프레임 추가하면 바로 훈련 시작!

예상 대기 시간: 3-4시간 (오늘 중)
```

### **클로에게**:

```
안녕 클로!

State-Action-Reward 데이터는 완전히 준비됐어!
지금 바로 RL 훈련 시작할 수 있어.

데이터 위치:
web_app/collected_gameplay/session_*/states_actions.jsonl

시작 방법:
1. 이 JSONL 파일 읽기
2. Replay Buffer로 변환
3. PPO/DQN 훈련

제안: State-based로 먼저 시작하고
      나중에 Vision-based로 전환
```

---

## 🔗 **유용한 링크**

- **웹 게임**: https://distilled-vision-agent-fhuhwhnu3a-uc.a.run.app
- **GitHub (팀)**: https://github.com/gitgutgit/YOLO-You-Only-Live-Once
- **GCP Console**: https://console.cloud.google.com/run?project=vision-final-478501

---

**작성자**: 래리 (Minsuk Kim)  
**날짜**: 2025-11-18  
**업데이트**: 실시간
