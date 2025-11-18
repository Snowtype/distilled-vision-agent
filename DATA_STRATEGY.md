# 📊 프로젝트 데이터 저장 전략

## 🎯 목표

1. **제이 (YOLO 훈련)**: 게임 화면 프레임 + bbox 라벨
2. **클로 (RL 훈련)**: State-Action-Reward 시퀀스
3. **래리 (인프라)**: 리더보드 + 세션 관리

---

## 🏗️ **최종 아키텍처: JSON + 파일 저장 (DB 불필요)**

### ✅ **선택 이유**

| 기준                | JSON + 파일        | PostgreSQL/MySQL  | Firebase/Supabase |
| ------------------- | ------------------ | ----------------- | ----------------- |
| **프로젝트 규모**   | ✅ 수백~수천 세션  | ❌ 오버킬         | ❌ 오버킬         |
| **쿼리 복잡도**     | ✅ 단순 정렬/필터  | ❌ 불필요한 JOIN  | ⚠️ 제한적         |
| **팀 스킬**         | ✅ Python 기반     | ⚠️ SQL 학습 필요  | ⚠️ API 학습 필요  |
| **배포 간편성**     | ✅ 파일시스템 충분 | ❌ DB 서버 관리   | ⚠️ 외부 의존성    |
| **훈련 워크플로우** | ✅ 파일 직접 읽기  | ❌ Export 필요    | ❌ Export 필요    |
| **비용**            | ✅ 무료            | ⚠️ Cloud SQL 비용 | ⚠️ 무료 한도 제한 |

**결론**: 프로젝트 규모와 목적상 **JSON + 파일 저장**이 최적!

---

## 🗂️ **디렉토리 구조**

```
final_project/
├── web_app/                          # 웹 게임 (GCP 배포)
│   ├── data/                         # 운영 데이터 (Git 제외)
│   │   ├── leaderboard.json          # 리더보드
│   │   └── sessions/                 # 세션 메타데이터
│   │       └── session_*.json
│   └── collected_gameplay/           # 📦 수집된 원본 데이터 (Git 제외)
│       └── session_YYYYMMDD_HHMMSS_MODE/
│           ├── metadata.json              # 세션 정보
│           ├── frames/                    # 🎯 제이용: 프레임 이미지
│           │   ├── frame_0000.png
│           │   ├── frame_0001.png
│           │   └── ...
│           ├── states_actions.jsonl       # 🎯 클로용: (state, action, reward)
│           └── bboxes.jsonl               # 🎯 제이용: bbox (선택)
│
├── data/                             # 팀 공동 훈련 데이터
│   ├── raw/                          # 원본 (web_app에서 복사)
│   │   └── gameplay_sessions/
│   ├── labeled/                      # 🎯 제이 작업: YOLO 훈련 데이터
│   │   ├── images/
│   │   │   ├── train/
│   │   │   ├── val/
│   │   │   └── test/
│   │   ├── labels/
│   │   │   └── (YOLO format .txt)
│   │   └── dataset.yaml
│   └── augmented/                    # 🎯 래리 작업: 증강 데이터
│
└── training_outputs/                 # Git 제외
    ├── yolo_weights/                 # 제이 모델
    └── rl_checkpoints/               # 클로 모델
```

---

## 📋 **데이터 포맷**

### 1️⃣ **Leaderboard (JSON)**

**파일**: `web_app/data/leaderboard.json`

```json
{
  "scores": [
    {
      "player": "Player_abc123",
      "score": 42,
      "time": 18.5,
      "mode": "human",
      "date": "2025-11-18T14:30:00",
      "session_id": "session_abc123"
    }
  ]
}
```

**특징**:

- 단순 배열, 메모리 내 정렬
- Top 100만 유지
- GCP와 로컬 모두 동일 구조

---

### 2️⃣ **세션 메타데이터 (JSON)**

**파일**: `web_app/data/sessions/session_{timestamp}_{sid}.json`

```json
{
  "session_id": "abc123xyz",
  "mode": "human",
  "score": 42,
  "survival_time": 18.5,
  "total_frames": 555,
  "final_state": {
    "player_x": 480,
    "player_y": 360,
    "obstacles_count": 8
  },
  "timestamp": "2025-11-18T14:30:00",
  "data_collected": true,
  "frames_saved": 555,
  "training_data_path": "collected_gameplay/session_20251118_143000_human"
}
```

**용도**:

- 빠른 통계 조회
- 훈련 데이터 인덱스

---

### 3️⃣ **프레임 이미지 (PNG)** - 🎯 제이용

**경로**: `web_app/collected_gameplay/session_*/frames/frame_XXXX.png`

**포맷**:

- PNG (무손실)
- 960x720 해상도
- RGB 채널

**수집 방법**:

- 게임 루프에서 매 프레임 Canvas 캡처
- 또는 2-3 프레임마다 샘플링 (용량 절약)

---

### 4️⃣ **State-Action-Reward 로그 (JSONL)** - 🎯 클로용

**파일**: `web_app/collected_gameplay/session_*/states_actions.jsonl`

**포맷**: JSON Lines (한 줄에 하나의 JSON 객체)

```jsonl
{"frame": 0, "state": {"player_x": 480, "player_y": 360, "player_vy": 0, "obstacles": [{"x": 120, "y": -50, "size": 50}]}, "action": "jump", "reward": 1.0, "done": false}
{"frame": 1, "state": {"player_x": 480, "player_y": 350, "player_vy": -15, "obstacles": [{"x": 120, "y": -45, "size": 50}]}, "action": "stay", "reward": 1.0, "done": false}
{"frame": 2, "state": {"player_x": 480, "player_y": 340, "player_vy": -14, "obstacles": [{"x": 120, "y": -40, "size": 50}]}, "action": "stay", "reward": 1.0, "done": false}
...
{"frame": 554, "state": {"player_x": 480, "player_y": 680, "player_vy": 20, "obstacles": [{"x": 480, "y": 650, "size": 50}]}, "action": "stay", "reward": -100, "done": true}
```

**특징**:

- JSONL은 대용량 로그에 최적 (한 줄씩 읽기 가능)
- 클로가 직접 RL 훈련에 사용

---

### 5️⃣ **Bounding Box 라벨 (JSONL, 선택)** - 🎯 제이용

**파일**: `web_app/collected_gameplay/session_*/bboxes.jsonl`

```jsonl
{"frame": 0, "objects": [{"class": "player", "x": 455, "y": 335, "w": 50, "h": 50}, {"class": "obstacle", "x": 95, "y": -75, "w": 50, "h": 50}]}
{"frame": 1, "objects": [{"class": "player", "x": 455, "y": 325, "w": 50, "h": 50}, {"class": "obstacle", "x": 95, "y": -70, "w": 50, "h": 50}]}
```

**용도**:

- YOLO 훈련 라벨
- 게임 상태에서 자동 생성 (수동 라벨링 불필요!)

---

## 🔄 **데이터 흐름**

```
[사용자 플레이]
    ↓
[웹 게임 (app.py)]
    ↓ 실시간 수집
[web_app/collected_gameplay/]
    ├── frames/*.png          (제이용)
    ├── states_actions.jsonl  (클로용)
    └── bboxes.jsonl          (제이용)
    ↓
[래리: 데이터 검증 & 복사]
    ↓
[final_project/data/raw/]
    ↓
[제이: YOLO 라벨링]
    ↓
[final_project/data/labeled/]
    ↓
[래리: 데이터 증강]
    ↓
[final_project/data/augmented/]
    ↓
[제이 & 클로: 모델 훈련]
    ↓
[training_outputs/]
    ├── yolo_weights/
    └── rl_checkpoints/
```

---

## 🚀 **구현 단계**

### ✅ **Phase 1: 현재 (완료됨)**

- [x] 리더보드 JSON 저장
- [x] 세션 메타데이터 저장

### 🔨 **Phase 2: 데이터 수집 강화 (다음 작업)**

- [ ] Canvas 프레임 캡처 (JavaScript → Base64 → Python)
- [ ] State-Action-Reward 로그 (JSONL)
- [ ] Bbox 자동 생성 (게임 상태 → YOLO 포맷)

### 📊 **Phase 3: 팀원 협업**

- [ ] 제이: YOLO 라벨링 도구 (Label Studio 또는 자동)
- [ ] 클로: RL 훈련 파이프라인
- [ ] 래리: 데이터 증강 & 품질 관리

---

## 📏 **용량 예상**

### 1세션 (평균 10초, 300 프레임)

| 데이터                | 크기       |
| --------------------- | ---------- |
| metadata.json         | 1 KB       |
| frames/\*.png (300장) | 30 MB      |
| states_actions.jsonl  | 100 KB     |
| bboxes.jsonl          | 50 KB      |
| **합계**              | **~30 MB** |

### 100 세션

- **총 용량**: ~3 GB
- **Git LFS 사용** 또는 **Google Drive 공유**
- **GCP Cloud Storage** (나중에 스케일링 시)

---

## 🛠️ **추가 개선 사항 (선택)**

### 🔹 **1. 데이터 압축**

- PNG → JPEG (화질 손실 최소)
- 프레임 다운샘플링 (960x720 → 480x360)
- → **용량 50% 절감**

### 🔹 **2. 클라우드 동기화**

- GCP Cloud Storage Bucket
- `gsutil rsync` 자동화
- → **팀원 간 실시간 공유**

### 🔹 **3. 데이터 버전 관리**

- Git LFS (2GB 무료)
- DVC (Data Version Control)
- → **훈련 데이터 재현성**

---

## 📚 **참고 자료**

- [YOLO 데이터셋 포맷](https://docs.ultralytics.com/datasets/detect/)
- [RL Replay Buffer 구조](https://stable-baselines3.readthedocs.io/en/master/guide/examples.html)
- [JSONL (JSON Lines)](https://jsonlines.org/)

---

## ❓ **FAQ**

### Q1: DB 없이 정말 괜찮을까요?

**A**: 네! 프로젝트 규모상 수백~수천 세션이면 JSON으로 충분합니다.

- Leaderboard: 메모리 내 정렬 (100개 항목 → 1ms 이내)
- 세션 조회: 파일 시스템 (1000개 파일 → 수십 ms)

### Q2: GCP 배포 시 파일 저장은?

**A**: Cloud Run의 파일시스템은 임시이므로:

1. **중요한 데이터**: Cloud Storage Bucket에 자동 백업
2. **리더보드**: Cloud Firestore (선택) 또는 주기적 백업

### Q3: 팀원들과 데이터 공유는?

**A**:

- **로컬 개발**: Google Drive 공유 폴더
- **대용량**: Git LFS 또는 Cloud Storage
- **협업**: `data/` 디렉토리 symlink

---

**작성자**: 래리 (Minsuk Kim)  
**최종 수정**: 2025-11-18
