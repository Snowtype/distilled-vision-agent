# 🤖 YOLO 모델을 AI 모드에 통합하는 방법

## 📊 현재 구조 분석

### 현재 AI 모드 동작 방식

**위치**: `web_app/app.py`의 `ai_decision()` 함수

**현재 방식**:

```python
def ai_decision(game):
    # 게임 내부 상태를 직접 읽음
    for obs in game.obstacles:  # ← 게임 엔진에서 직접 가져옴
        # 휴리스틱으로 의사결정
        if obj_type == 'meteor':
            # 메테오 회피 로직
```

**문제점**:

- 게임 내부 상태를 직접 읽음 (Vision 기반이 아님)
- YOLO 모델이 있어도 사용하지 않음
- "Vision 기반 인식"이라는 프로젝트 목표와 맞지 않음

### 현재 CV 모듈 사용 현황

**위치**: `web_app/app.py`의 `Game` 클래스

**사용 중인 곳**:

1. 라바 감지: `detect_lava_with_cv()` ✅
2. AI 모드: **사용 안 함** ❌

---

## 🎯 해결 방안

### 옵션 1: 기존 AI 모드에 YOLO 통합 (권장) ✅

**장점**:

- ✅ "Vision 기반 인식" 프로젝트 목표 달성
- ✅ 별도 모드 불필요 (간단함)
- ✅ YOLO 모델이 완성되면 자동으로 Vision 기반으로 전환

**구현 방법**:

1. AI 모드에서 CV 모듈 사용
2. YOLO 감지 결과를 AI 입력으로 변환
3. 기존 휴리스틱은 폴백으로 유지

### 옵션 2: 별도 "Vision AI" 모드 추가

**장점**:

- ✅ 기존 AI 모드 유지 (비교 가능)
- ✅ Vision 기반 vs 내부 상태 기반 비교 가능

**단점**:

- ❌ UI 복잡도 증가 (모드 선택)
- ❌ 코드 중복 가능성

---

## ✅ 권장: 옵션 1 (기존 AI 모드에 통합)

### 구현 계획

#### 1. AI 모드에서 YOLO 감지 결과 사용

**수정 위치**: `web_app/app.py`의 `ai_decision()` 함수

**현재 코드**:

```python
def ai_decision(game):
    # 게임 내부 상태 직접 읽기
    for obs in game.obstacles:
        # ...
```

**수정 후**:

```python
def ai_decision(game):
    # 1. YOLO로 객체 감지 (Vision 기반)
    game_state = game.get_state()
    dummy_frame = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
    detections = game.cv_module.detect_objects(dummy_frame, game_state)

    # 2. YOLO 감지 결과를 AI 입력으로 변환
    if detections:
        # YOLO 감지 결과 사용
        return ai_decision_from_yolo(detections, game)
    else:
        # 폴백: 기존 휴리스틱
        return ai_decision_heuristic(game)
```

#### 2. YOLO 감지 결과 → AI 입력 변환

**새 함수 추가**:

```python
def ai_decision_from_yolo(detections: List[CVDetectionResult], game) -> str:
    """
    YOLO 감지 결과를 기반으로 AI 의사결정

    Args:
        detections: YOLO가 감지한 객체들
        game: 게임 상태

    Returns:
        action: 'stay', 'left', 'right', 'jump'
    """
    player_x = game.player_x
    player_y = game.player_y
    player_center_x = player_x + PLAYER_SIZE / 2

    # YOLO 감지 결과에서 플레이어, 메테오, 별 찾기
    detected_player = None
    detected_meteors = []
    detected_stars = []
    detected_lava = None

    for det in detections:
        if det.class_id == 0 or det.class_name == "Player":
            detected_player = det
        elif det.class_id == 1 or det.class_name == "meteor":
            detected_meteors.append(det)
        elif det.class_id == 2 or det.class_name == "star":
            detected_stars.append(det)
        elif det.class_id == 4 or det.class_name == "Lava":
            detected_lava = det

    # Vision 기반 의사결정 로직
    # 1. 가장 가까운 메테오 회피
    nearest_meteor = None
    nearest_meteor_dist = float('inf')

    for meteor in detected_meteors:
        bbox = meteor.bbox
        meteor_center_x = (bbox[0] + bbox[2]) / 2
        meteor_center_y = (bbox[1] + bbox[3]) / 2

        dist = abs(meteor_center_x - player_center_x) + abs(meteor_center_y - player_y)
        if dist < nearest_meteor_dist:
            nearest_meteor_dist = dist
            nearest_meteor = meteor

    # 2. 의사결정
    if nearest_meteor and nearest_meteor_dist < 150:
        # 메테오 회피
        meteor_bbox = nearest_meteor.bbox
        meteor_center_x = (meteor_bbox[0] + meteor_bbox[2]) / 2

        if meteor_center_x < player_center_x:
            return 'right'  # 오른쪽으로 회피
        else:
            return 'left'   # 왼쪽으로 회피

    # 3. 별 수집
    nearest_star = None
    nearest_star_dist = float('inf')

    for star in detected_stars:
        bbox = star.bbox
        star_center_x = (bbox[0] + bbox[2]) / 2
        star_center_y = (bbox[1] + bbox[3]) / 2

        dist = abs(star_center_x - player_center_x) + abs(star_center_y - player_y)
        if dist < nearest_star_dist:
            nearest_star_dist = dist
            nearest_star = star

    if nearest_star and nearest_star_dist < 100:
        star_bbox = nearest_star.bbox
        star_center_x = (star_bbox[0] + star_bbox[2]) / 2

        if star_center_x < player_center_x - 20:
            return 'left'
        elif star_center_x > player_center_x + 20:
            return 'right'

    # 4. 라바 회피
    if detected_lava:
        lava_bbox = detected_lava.bbox
        player_in_lava = (
            player_x < lava_bbox[2] and
            player_x + PLAYER_SIZE > lava_bbox[0] and
            player_y + PLAYER_SIZE > lava_bbox[1]
        )

        if player_in_lava:
            # 라바에서 벗어나기
            lava_center_x = (lava_bbox[0] + lava_bbox[2]) / 2
            if player_center_x < lava_center_x:
                return 'left'
            else:
                return 'right'

    return 'stay'  # 기본: 대기
```

#### 3. 폴백 메커니즘

**YOLO 모델이 없거나 실패 시**:

- 기존 휴리스틱 사용
- 사용자에게 투명하게 동작

```python
def ai_decision(game):
    try:
        # YOLO 감지 시도
        detections = game.cv_module.detect_objects(...)

        if detections and len(detections) > 0:
            # Vision 기반 의사결정
            return ai_decision_from_yolo(detections, game)
    except Exception as e:
        print(f"⚠️ YOLO 감지 실패, 휴리스틱 사용: {e}")

    # 폴백: 기존 휴리스틱
    return ai_decision_heuristic(game)
```

---

## 🔄 통합 후 동작 방식

### 시나리오 1: YOLO 모델 있음

```
AI 모드 시작
    ↓
YOLO로 객체 감지 (Vision 기반)
    ↓
감지 결과 → AI 의사결정
    ↓
행동 실행 (left/right/jump/stay)
```

### 시나리오 2: YOLO 모델 없음 (현재 상태)

```
AI 모드 시작
    ↓
YOLO 모델 없음 → 시뮬레이션 모드
    ↓
기존 휴리스틱 사용
    ↓
행동 실행
```

---

## 📝 구현 체크리스트

### Jeewon 모델 완성 후

- [ ] `web_app/models/yolo/best.pt`에 모델 저장
- [ ] `cv_module.py`에서 실제 YOLO 로드 구현
- [ ] `_real_yolo_detection()` 구현

### AI 모드 통합

- [ ] `ai_decision()` 함수 수정
- [ ] `ai_decision_from_yolo()` 함수 추가
- [ ] YOLO 감지 결과 → AI 입력 변환 로직
- [ ] 폴백 메커니즘 테스트

### 테스트

- [ ] YOLO 모델 있을 때: Vision 기반 AI 동작 확인
- [ ] YOLO 모델 없을 때: 휴리스틱 폴백 확인
- [ ] 성능 테스트 (60 FPS 유지)

---

## 🎯 결론

### ✅ **권장: 기존 AI 모드에 YOLO 통합**

**이유**:

1. **프로젝트 목표 달성**: "Vision 기반 인식" 강조
2. **자동 전환**: YOLO 모델 완성 시 자동으로 Vision 기반으로 전환
3. **간단함**: 별도 모드 불필요
4. **투명함**: 사용자는 모드 변경 없이 자동으로 개선된 AI 사용

**구현 시점**:

- Jeewon 모델 완성 후 즉시 통합 가능
- 현재 코드 구조상 큰 변경 불필요
- `ai_decision()` 함수만 수정하면 됨

---

**작성일**: 2025-11-22
**상태**: Jeewon 모델 훈련 중 (epoch 50)
