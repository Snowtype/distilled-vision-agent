# AI 모드 동작 원리 설명

## 🤖 AI 모드에서 무엇이 동작하는가?

### 현재 AI 모드 구조

```
AI Mode 클릭
    ↓
game_loop() 실행
    ↓
ai_decision() 호출 (매 프레임마다)
    ↓
[현재] 휴리스틱 정책 사용 (RL 모델 없음)
    ↓
게임 업데이트
    ↓
CV 모듈 호출 (라바 감지용)
    ↓
[현재] 시뮬레이션 모드 사용 (게임 상태 기반)
```

### 1. AI 의사결정 (AI Decision)

**위치**: `web_app/app.py` → `ai_decision()` 함수

**현재 상태**:

- ✅ **휴리스틱 정책 사용 중** (규칙 기반 AI)
- ❌ RL 모델 없음 (Chloe가 아직 훈련 중)
- 전략: 메테오 회피, 별 수집, 중앙 유지

**코드**:

```python
def ai_decision(game):
    # RL 모델이 있으면 사용 (현재는 없음)
    if RL_MODEL_AVAILABLE and RL_MODEL is not None:
        # TODO: RL 모델 추론
        pass

    # 휴리스틱 정책 (현재 사용 중)
    # 1. 메테오 회피
    # 2. 별 수집
    # 3. 중앙 유지
```

### 2. YOLO 모델 (Vision 기반 라바 감지)

**위치**: `web_app/app.py` → `Game.__init__()` → `cv_module`

**현재 상태**:

- ✅ **지원님이 훈련한 YOLO 모델 로드됨** (`AI_model/best_112217.pt`)
- ✅ 모델은 로드되지만, **현재는 시뮬레이션 모드 사용** (성능 최적화)
- 용도: 라바 감지 (Vision 기반 인식 강조)

**코드**:

```python
# Game.__init__()
yolo_model_path = 'AI_model/best_112217.pt'
self.cv_module = ComputerVisionModule(model_path=yolo_model_path)

# detect_lava_with_cv()
# 게임 상태가 있으면 시뮬레이션 모드 사용 (더 빠름)
detections = self.cv_module.detect_objects(dummy_frame, game_state)
```

### 3. 모델 상태 요약

| 모델          | 상태                 | 용도               | 위치                      |
| ------------- | -------------------- | ------------------ | ------------------------- |
| **YOLO 모델** | ✅ 훈련 완료, 로드됨 | 라바 감지 (Vision) | `AI_model/best_112217.pt` |
| **RL 모델**   | ❌ 훈련 중 (Chloe)   | AI 의사결정        | 아직 없음                 |

## 📊 데이터 수집 현황

### 현재 Frames 카운팅 문제

**현재 코드**:

```javascript
// index.html
document.getElementById("collectedFrames").textContent =
  this.gameState.frame || 0;
```

**문제점**:

- `game.frame` = 게임 프레임 카운터 (매 프레임마다 증가, 30 FPS)
- 실제 저장되는 데이터와 다름
- 예: 게임 10초 플레이 = 300 프레임, 하지만 실제 저장은 더 적음

### 실제 데이터 저장

**저장되는 데이터**:

1. **State-Action-Reward 로그**: `game.collected_states` (매 프레임마다 저장)
2. **프레임 이미지**: `frame_capture` 이벤트 (10프레임마다 = 3 FPS)
3. **Bounding Box 라벨**: `game.collected_states` 기반

**실제 저장 개수**:

- State-Action 로그: `len(game.collected_states)` 개
- 프레임 이미지: `game.frame / 10` 개 (10프레임마다)
- Bbox 라벨: `len(game.collected_states)` 개

## 🔧 수정 제안

### 1. AI 모드 설명 추가

UI에 명확한 설명 추가:

- "AI Mode: 휴리스틱 정책 사용 중 (RL 모델 훈련 대기)"
- "YOLO 모델: 로드됨 (라바 감지용)"

### 2. 데이터 수집 표시 개선

**현재**: `game.frame` (게임 프레임 카운터)
**개선**: 실제 저장된 데이터 개수

```javascript
// 실제 수집된 데이터 개수 표시
collectedStates: this.gameState.collected_states_count || 0;
collectedImages: this.gameState.collected_images_count || 0;
```
