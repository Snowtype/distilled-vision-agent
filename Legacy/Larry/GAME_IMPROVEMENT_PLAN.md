# 🎮 **게임 메커니즘 개선 계획**

## 📋 **제안 사항**

### **제이 (Jeewon)**

1. ✅ 대각선 낙하 (전략적 회피)
2. ✅ 메테오(회피) + 별(보상)
3. ⚠️ 용암지대 (점프 강제)

### **클로 (Chloe)**

- 점프 제거 → 더 단순한 학습

---

## 🎯 **최종 결정: 하이브리드 접근**

### **✅ Phase 1: 즉시 구현 (점프 유지, 용암 제외)**

#### **이유**:

1. **점프 유지**: 현재 이미 구현됨, 제거하면 후퇴
2. **대각선 낙하**: RL 복잡도 증가 (더 의미 있는 학습)
3. **메테오 + 별**: 멀티클래스 YOLO 학습
4. **용암 제외**: 복잡도 과다, 시간 부족

---

## 📊 **영향도 분석**

### **1. 대각선 낙하** ⭐⭐⭐

| 항목               | Before      | After                  | 영향        |
| ------------------ | ----------- | ---------------------- | ----------- |
| **장애물 움직임**  | 수직 (vy=5) | 대각선 (vx=-2~2, vy=5) | RL 복잡도 ↑ |
| **YOLO 훈련**      | 단순 패턴   | 다양한 궤적            | 강건성 ↑    |
| **Data Diversity** | 낮음        | 높음                   | 품질 ↑      |
| **구현 시간**      | -           | 5분                    | ✅ 즉시     |

**코드 변경**:

```python
# Before
self.obstacles.append({
    'x': random.randint(0, WIDTH - OBSTACLE_SIZE),
    'y': -OBSTACLE_SIZE,
    'size': OBSTACLE_SIZE
})

# After
self.obstacles.append({
    'x': random.randint(0, WIDTH - OBSTACLE_SIZE),
    'y': -OBSTACLE_SIZE,
    'vx': random.randint(-2, 2),  # 좌우 속도
    'vy': 5,                       # 하강 속도
    'size': OBSTACLE_SIZE,
    'type': 'meteor'
})
```

---

### **2. 메테오 + 별** ⭐⭐⭐

| 항목          | Before         | After              | 영향              |
| ------------- | -------------- | ------------------ | ----------------- |
| **객체 타입** | 1개 (obstacle) | 2개 (meteor, star) | YOLO 멀티클래스   |
| **RL 전략**   | 단순 회피      | Risk-Reward        | 의사결정 복잡도 ↑ |
| **보상 함수** | 생존 +1        | 별 획득 +20        | 학습 동기 ↑       |
| **구현 시간** | -              | 15분               | ✅ 즉시           |

**코드 변경**:

```python
# 객체 타입 정의
OBJECT_TYPES = {
    'meteor': {'color': 'red', 'reward': -100, 'score': 0},   # 충돌 시 게임 오버
    'star': {'color': 'yellow', 'reward': 20, 'score': 10}    # 획득 시 보너스
}

# 생성 시
if random.random() < 0.03:  # 3% 확률로 별
    obj_type = 'star'
else:
    obj_type = 'meteor'

self.obstacles.append({
    'type': obj_type,
    'x': random.randint(0, WIDTH - OBSTACLE_SIZE),
    'y': -OBSTACLE_SIZE,
    'vx': random.randint(-2, 2),
    'vy': 5 if obj_type == 'meteor' else 3,  # 별은 느리게
    'size': 30 if obj_type == 'star' else OBSTACLE_SIZE
})
```

---

### **3. 점프 유지 (현재 상태)** ✅

| 항목             | 클로 제안 (제거)        | 현재 (유지)  | 최종 결정 |
| ---------------- | ----------------------- | ------------ | --------- |
| **Action Space** | 3개 (stay, left, right) | 4개 (+ jump) | ✅ 유지   |
| **RL 수렴**      | 빠름                    | 느림         | ⚠️ 감수   |
| **전략 다양성**  | 낮음                    | 높음         | ✅ 유지   |
| **구현 상태**    | 제거 필요               | 이미 구현됨  | ✅ 유지   |

**이유**:

- 점프는 **이미 구현**되어 있음
- 제거하면 **후퇴** (기능 축소)
- **별 획득**에 점프 활용 가능
- RL이 느려도 **의미 있는 학습 문제**

---

### **4. 용암지대 (제외)** ❌

| 항목              | 구현 시   | 제외 시 | 최종 결정 |
| ----------------- | --------- | ------- | --------- |
| **복잡도**        | 매우 높음 | 낮음    | ❌ 제외   |
| **구현 시간**     | 1-2시간   | 0       | ❌ 제외   |
| **버그 위험**     | 높음      | 낮음    | ❌ 제외   |
| **프로젝트 필수** | 아님      | 아님    | ❌ 제외   |

**이유**:

- 시간 부족 (프레임 캡처 우선)
- 복잡도 과다
- 핵심 목표에 불필요

---

## 🛠️ **구현 계획**

### **✅ 즉시 구현 (오늘, 20분)**

#### **Step 1: 대각선 낙하** (5분)

```python
# app.py - Game.update()에서 장애물 생성 부분 수정

# 기존 (수직)
self.obstacles.append({
    'x': random.randint(0, WIDTH - OBSTACLE_SIZE),
    'y': -OBSTACLE_SIZE,
    'size': OBSTACLE_SIZE
})

# 새로운 (대각선)
self.obstacles.append({
    'x': random.randint(0, WIDTH - OBSTACLE_SIZE),
    'y': -OBSTACLE_SIZE,
    'vx': random.randint(-2, 2),  # ← 추가
    'vy': 5,                       # ← 추가
    'size': OBSTACLE_SIZE,
    'type': 'meteor'               # ← 추가
})

# 장애물 이동 로직 수정
for obs in self.obstacles:
    obs['x'] += obs.get('vx', 0)  # 좌우 이동
    obs['y'] += obs.get('vy', 5)  # 하강

    # 화면 밖으로 나가면 반대편에서 등장
    if obs['x'] < -OBSTACLE_SIZE:
        obs['x'] = WIDTH
    elif obs['x'] > WIDTH:
        obs['x'] = -OBSTACLE_SIZE
```

#### **Step 2: 메테오 + 별** (15분)

```python
# 객체 타입 정의 (app.py 상단)
OBJECT_TYPES = {
    'meteor': {
        'color': '#FF4444',
        'reward_collision': -100,
        'score': 0
    },
    'star': {
        'color': '#FFD700',
        'reward_collect': 20,
        'score': 10,
        'size': 30
    }
}

# 생성 로직
def spawn_object(self):
    """객체 생성 (메테오 또는 별)"""
    # 3% 확률로 별, 나머지는 메테오
    obj_type = 'star' if random.random() < 0.03 else 'meteor'

    obj = {
        'type': obj_type,
        'x': random.randint(0, WIDTH - OBSTACLE_SIZE),
        'y': -OBSTACLE_SIZE,
        'vx': random.randint(-2, 2),
        'vy': 3 if obj_type == 'star' else 5,  # 별은 느리게
        'size': 30 if obj_type == 'star' else OBSTACLE_SIZE
    }

    self.obstacles.append(obj)

# 충돌 감지 수정
def check_collisions(self):
    """충돌 검사 (메테오=게임오버, 별=획득)"""
    for obs in self.obstacles[:]:  # 복사본으로 순회
        if (self.player_x < obs['x'] + obs['size'] and
            self.player_x + PLAYER_SIZE > obs['x'] and
            self.player_y < obs['y'] + obs['size'] and
            self.player_y + PLAYER_SIZE > obs['y']):

            if obs['type'] == 'meteor':
                # 메테오 충돌: 게임 오버
                self.game_over = True
                self.running = False
                print(f"💥 메테오 충돌! 게임 오버!")

            elif obs['type'] == 'star':
                # 별 획득: 점수 증가
                self.score += OBJECT_TYPES['star']['score']
                self.obstacles.remove(obs)
                print(f"⭐ 별 획득! +{OBJECT_TYPES['star']['score']}점")
```

---

## 📊 **예상 효과**

### **YOLO 훈련 (제이)**

```python
# Before
yolo_classes = ['player', 'obstacle']  # 2 클래스

# After
yolo_classes = ['player', 'meteor', 'star']  # 3 클래스

# 학습 데이터 예시
bboxes = [
    {"frame": 100, "objects": [
        {"class": "player", "x": 480, "y": 360, "w": 50, "h": 50},
        {"class": "meteor", "x": 300, "y": 100, "w": 50, "h": 50, "vx": -1, "vy": 5},
        {"class": "meteor", "x": 600, "y": 200, "w": 50, "h": 50, "vx": 2, "vy": 5},
        {"class": "star", "x": 450, "y": 50, "w": 30, "h": 30, "vx": 0, "vy": 3}
    ]}
]

# 더 다양한 포즈 → 강건한 YOLO 모델
```

### **RL 훈련 (클로)**

```python
# Reward 함수 개선
def calculate_reward(self):
    reward = 1.0  # 생존 기본

    # 메테오 회피 성공
    if meteor_avoided:
        reward += 10

    # 별 획득
    if star_collected:
        reward += 20  # 높은 보상!

    # 메테오 충돌
    if game_over:
        reward = -100

    return reward

# 학습 목표: Risk-Reward 밸런스
# - 안전하게 메테오 회피
# - 기회 되면 별 획득 (위험 감수)
```

---

## 🎯 **팀원별 영향**

### **제이 (Jeewon)**

✅ **긍정적**:

- 멀티클래스 YOLO 학습 (더 현실적)
- 다양한 데이터 (대각선 궤적)
- mAP ≥ 70% 달성 가능성 ↑

### **클로 (Chloe)**

⚠️ **도전적**:

- Action Space 4개 유지 (stay, left, right, jump)
- Risk-Reward 학습 (별 vs 안전)
- RL 수렴 느릴 수 있음

**대응책**:

1. **Reward Shaping**: 별 보상 높게 (20점)
2. **Curriculum Learning**: 초기에는 별 없이, 나중에 추가
3. **State-based 먼저**: Vision-based 전환 전 검증

### **래리 (너)**

✅ **작업량 증가 (20분)**:

- 대각선 낙하 구현
- 메테오 + 별 로직
- Bbox 라벨 업데이트

---

## 📋 **체크리스트**

### **즉시 구현**

- [ ] 대각선 낙하 (vx 추가)
- [ ] 메테오 + 별 타입 구분
- [ ] 충돌 로직 개선 (메테오=오버, 별=획득)
- [ ] Bbox 라벨에 타입 추가
- [ ] 프론트엔드 렌더링 (색상 구분)

### **테스트**

- [ ] 대각선 이동 동작 확인
- [ ] 별 획득 시 점수 증가
- [ ] 메테오 충돌 시 게임 오버
- [ ] Bbox 라벨 정확성

### **데이터 수집**

- [ ] 새 게임으로 50+ 세션 수집
- [ ] YOLO 훈련 데이터 준비
- [ ] RL 훈련 데이터 준비

---

## 💬 **팀원 커뮤니케이션**

### **제이에게**

```
제안 감사! 1번, 2번은 즉시 구현할게.

✅ 대각선 낙하: YOLO 학습에 도움
✅ 메테오 + 별: 멀티클래스 학습

용암지대는 시간 관계상 제외.
점프는 별 획득용으로 활용!
```

### **클로에게**

```
점프 유지하는 방향으로 결정했어.

이유:
1. 이미 구현되어 있음
2. 별 획득에 활용 가능
3. 더 의미 있는 RL 학습

걱정되면:
- State-based로 먼저 검증
- 수렴 느리면 Reward Shaping
- Curriculum Learning 적용
```

---

**작성자**: 래리 (Minsuk Kim)  
**날짜**: 2025-11-18  
**상태**: 구현 준비 완료
