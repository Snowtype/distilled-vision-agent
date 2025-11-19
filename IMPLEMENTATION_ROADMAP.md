# 🛣️ **프로젝트 제안서 대비 구현 로드맵**

## 📊 **현재 상태 분석**

### ✅ **완성된 것들**

1. **웹 게임 인프라** (래리)

   - Flask + SocketIO 실시간 게임
   - GCP Cloud Run 배포
   - 리더보드 시스템

2. **데이터 수집 파이프라인 (부분)** (래리)

   - State-Action-Reward 로깅 ✅
   - Bounding Box 자동 생성 ✅
   - 세션 메타데이터 저장 ✅

3. **인프라 도구** (래리)
   - 데이터 증강 코드 (`src/data/augmentation.py`) ✅
   - ONNX 최적화 코드 (`src/deployment/onnx_optimizer.py`) ✅
   - 시각화 도구 (`src/utils/visualization.py`) ✅

---

## ❌ **제안서 대비 부족한 부분**

### 🔴 **Critical - 프로젝트 실패 가능성**

| 항목                    | 제안서 요구사항                | 현재 상태 | 갭                        | 담당자 |
| ----------------------- | ------------------------------ | --------- | ------------------------- | ------ |
| **RGB 프레임**          | "purely from raw visual input" | ❌ 없음   | **이미지 저장 구현 필요** | 래리   |
| **YOLO 훈련**           | ≥70% mAP                       | ❌ 미시작 | 모델 훈련 필요            | 제이   |
| **Policy Distillation** | ≥75% action agreement          | ❌ 미시작 | MLP 정책 훈련 필요        | 제이   |
| **RL 훈련**             | ≥20% 성능 향상                 | ❌ 미시작 | PPO/DQN 훈련 필요         | 클로   |

---

## 🎯 **즉시 해결 필요 - Phase 1 (래리)**

### **1. RGB 프레임 캡처 구현** ⭐⭐⭐

#### **목표**

```
collected_gameplay/session_*/
├── frames/              # ← 이것 추가!
│   ├── frame_0000.png
│   ├── frame_0001.png
│   └── ...
├── states_actions.jsonl
└── bboxes.jsonl
```

#### **구현 방법**

##### **A. 클라이언트 (JavaScript) - Canvas 캡처**

```javascript
// index.html에 추가
class GameClient {
  constructor() {
    this.frameBuffer = []; // 프레임 버퍼
    this.captureInterval = 2; // 2프레임마다 캡처 (용량 절약)
  }

  captureFrame() {
    // Canvas를 Base64로 인코딩
    const frameData = this.canvas.toDataURL("image/png");

    // 서버로 전송 (버퍼링)
    this.frameBuffer.push({
      frame: this.gameState.frame,
      data: frameData.split(",")[1], // Base64만 추출
    });

    // 10프레임마다 일괄 전송
    if (this.frameBuffer.length >= 10) {
      this.socket.emit("save_frames", {
        session_id: this.sessionId,
        frames: this.frameBuffer,
      });
      this.frameBuffer = [];
    }
  }

  render() {
    // 게임 렌더링
    // ...

    // 프레임 캡처 (옵션)
    if (this.isRecording && this.gameState.frame % this.captureInterval === 0) {
      this.captureFrame();
    }
  }
}
```

##### **B. 서버 (Python) - 프레임 저장**

```python
# app.py에 추가
import base64
from PIL import Image
import io

@socketio.on('save_frames')
def handle_save_frames(data):
    """프레임 이미지 저장"""
    session_id = data['session_id']
    frames = data['frames']

    # 세션 디렉토리 찾기
    for session_dir in COLLECTED_DIR.glob(f"session_*"):
        metadata_file = session_dir / "metadata.json"
        if metadata_file.exists():
            with open(metadata_file, 'r') as f:
                metadata = json.load(f)
                if metadata['session_id'] == session_id:
                    # frames 디렉토리 생성
                    frames_dir = session_dir / 'frames'
                    frames_dir.mkdir(exist_ok=True)

                    # 프레임 저장
                    for frame_data in frames:
                        frame_num = frame_data['frame']
                        base64_data = frame_data['data']

                        # Base64 → PNG
                        image_bytes = base64.b64decode(base64_data)
                        image = Image.open(io.BytesIO(image_bytes))

                        # 저장
                        frame_file = frames_dir / f"frame_{frame_num:04d}.png"
                        image.save(frame_file, 'PNG')

                    print(f"💾 {len(frames)}개 프레임 저장: {frames_dir.name}")
                    break
```

#### **예상 용량**

```
1 프레임 (960x720 PNG): ~100 KB (압축)
10초 게임 (300 프레임, 2프레임마다 캡처): 150장 × 100 KB = 15 MB
```

---

### **2. 전문가 시연 데이터 수집**

#### **목표**

- 고품질 플레이 50~100 세션
- 각 세션 생존 시간 > 60초
- 총 프레임 수 > 5,000

#### **방법**

```bash
# 웹 게임에서 Human Mode로 여러 번 플레이
# 또는 스크립트로 자동 플레이

# 통계 확인
curl https://distilled-vision-agent-fhuhwhnu3a-uc.a.run.app/api/stats
```

---

### **3. 데이터 증강 파이프라인 연결**

#### **현재**

```python
# src/data/augmentation.py - 코드는 있음
class BackgroundRandomizer:
    def randomize_background(self, image, new_background):
        # ...
```

#### **필요**

```python
# 수집된 프레임에 자동 증강 적용
cd final_project
python scripts/augment_collected_data.py \
    --input web_app/collected_gameplay/ \
    --output data/augmented/ \
    --multiplier 5  # 1개 → 5개로 증강
```

**결과**:

```
data/augmented/
├── session_20251118_142209_human_aug_0/
├── session_20251118_142209_human_aug_1/
├── session_20251118_142209_human_aug_2/
└── ...
```

---

## 🔄 **Phase 2 - 팀원 작업 (제이 & 클로)**

### **제이 (Jeewon) - YOLO 훈련**

#### **Input 데이터**

```
web_app/collected_gameplay/session_*/
├── frames/frame_*.png      # RGB 이미지 (래리가 추가)
└── bboxes.jsonl           # 라벨 (이미 있음)
```

#### **작업**

1. **데이터 변환** (YOLO 포맷)

   ```python
   # scripts/convert_to_yolo.py (래리가 제공)
   python scripts/convert_to_yolo.py \
       --input web_app/collected_gameplay/ \
       --output data/labeled/
   ```

2. **YOLOv8 훈련**

   ```python
   # src/models/train_yolo.py (제이가 작성)
   from ultralytics import YOLO

   model = YOLO('yolov8n.pt')
   results = model.train(
       data='data/labeled/dataset.yaml',
       epochs=100,
       imgsz=640,
       batch=16
   )
   ```

3. **성공 기준 달성**
   - mAP ≥ 70% on test set

---

### **클로 (Chloe) - RL 훈련**

#### **Input 데이터**

```
web_app/collected_gameplay/session_*/
├── frames/frame_*.png         # RGB (래리가 추가)
├── states_actions.jsonl      # State-Action-Reward (이미 있음)
└── bboxes.jsonl              # 보조 데이터
```

#### **작업 옵션**

##### **Option 1: Vision-based RL (제안서 원래 의도)**

```python
# src/training/train_ppo_vision.py (클로가 작성)
from stable_baselines3 import PPO
from stable_baselines3.common.vec_env import DummyVecEnv

# 1. YOLO로 이미지 → State 변환
# 2. PPO로 Policy 학습
model = PPO(
    'CnnPolicy',  # 이미지 입력
    env,
    learning_rate=3e-4,
    n_steps=2048
)
model.learn(total_timesteps=100000)
```

##### **Option 2: State-based RL (현재 데이터 활용)**

```python
# src/training/train_ppo_state.py (클로가 작성)
from stable_baselines3 import PPO

# states_actions.jsonl 로드 → Replay Buffer
# → PPO 훈련

model = PPO(
    'MlpPolicy',  # State vector 입력
    env,
    learning_rate=3e-4
)
model.learn(total_timesteps=100000)
```

3. **성공 기준 달성**
   - 평균 생존 시간 ≥ 20% 향상

---

## 📊 **최종 목표 - End-to-End Pipeline**

### **완성된 시스템**

```
[웹 게임]
    ↓ RGB frames
[YOLO Detection] (제이)
    ↓ Bbox + State
[Policy Network] (클로)
    ↓ Action
[게임 실행]
    ↓ 60 FPS
[ONNX Runtime] (래리)
```

### **성능 검증**

```python
# scripts/benchmark.py
results = {
    'detection_mAP': 0.75,      # ≥ 0.70 ✅
    'imitation_accuracy': 0.78, # ≥ 0.75 ✅
    'survival_time_gain': 0.25, # ≥ 0.20 ✅
    'fps': 62                   # ≥ 60 ✅
}
```

---

## 🎯 **타임라인 (추정)**

| Phase | 작업                         | 담당 | 예상 시간 |
| ----- | ---------------------------- | ---- | --------- |
| **1** | RGB 프레임 캡처 구현         | 래리 | 3-4시간   |
| **1** | 전문가 데이터 수집 (50 세션) | 래리 | 2-3시간   |
| **1** | 데이터 증강 파이프라인       | 래리 | 2시간     |
| **2** | YOLO 훈련 & 검증             | 제이 | 1-2일     |
| **2** | Policy Distillation          | 제이 | 1일       |
| **3** | PPO/DQN 훈련                 | 클로 | 1-2일     |
| **4** | ONNX 통합 & 최적화           | 래리 | 1일       |
| **5** | 최종 벤치마크 & 보고서       | 전체 | 1일       |

**총 예상 시간**: 5-7일

---

## 📋 **체크리스트**

### **Phase 1 - 데이터 수집 완성 (래리)**

- [ ] Canvas 프레임 캡처 구현
- [ ] 전문가 시연 데이터 50+ 세션
- [ ] 데이터 증강 파이프라인 연결
- [ ] 데이터셋 검증 & 통계

### **Phase 2 - Vision 모듈 (제이)**

- [ ] YOLO 데이터셋 변환 스크립트
- [ ] YOLOv8 훈련 (mAP ≥ 70%)
- [ ] Policy Distillation 구현 (≥ 75% accuracy)
- [ ] ONNX Export

### **Phase 3 - RL 모듈 (클로)**

- [ ] PPO/DQN 환경 설정
- [ ] 전문가 데이터 Replay Buffer 로드
- [ ] Self-Play 훈련 (≥ 20% 성능 향상)
- [ ] ONNX Export

### **Phase 4 - 통합 & 최적화 (래리)**

- [ ] ONNX Runtime 통합
- [ ] 60 FPS 벤치마크
- [ ] GCP 배포
- [ ] 최종 테스트

### **Phase 5 - 문서화 & 보고서**

- [ ] 최종 보고서 작성
- [ ] 데모 비디오 제작
- [ ] GitHub README 업데이트
- [ ] 제출

---

## 🚨 **리스크 & 대응책**

| 리스크                    | 대응책                              |
| ------------------------- | ----------------------------------- |
| **프레임 캡처 용량 초과** | 2-3 프레임마다 샘플링, JPEG 압축    |
| **YOLO mAP < 70%**        | 데이터 증강 강화, 더 큰 모델 시도   |
| **RL 수렴 안 됨**         | Reward shaping, Curriculum learning |
| **60 FPS 미달**           | ONNX INT8 양자화, 모델 크기 축소    |

---

**작성자**: 래리 (Minsuk Kim)  
**최종 수정**: 2025-11-18  
**상태**: Phase 1 진행 중
