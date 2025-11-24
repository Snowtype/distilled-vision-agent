# 🎯 YOLO 훈련 완전 정리 (쉽게 설명)

## 📚 기본 개념

### Q: 데이터만 수집하는 건가요? 모델을 생성하는 건가요?

**A: 둘 다입니다! 하지만 단계가 다릅니다.**

```
1단계: 데이터 수집 (이미 완료 ✅)
   ↓
2단계: 모델 훈련 (Jeewon이 지금 하는 중 🔄)
   ↓
3단계: 모델 사용 (훈련 완료 후 ✅)
```

---

## 🔄 전체 프로세스

### 1️⃣ **데이터 수집** (이미 완료)

**위치**: `web_app/game_dataset/`

```
web_app/game_dataset/
├── data.yaml              # 데이터셋 설정 파일
├── images/
│   └── train/
│       ├── game_20251121_KDGYYnKq_00010.jpg  ← 게임 화면 이미지
│       ├── game_20251121_KDGYYnKq_00020.jpg
│       └── ... (119개 이미지)
└── labels/
    └── train/
        ├── game_20251121_KDGYYnKq_00010.txt  ← 라벨 (어디에 뭐가 있는지)
        ├── game_20251121_KDGYYnKq_00020.txt
        └── ... (119개 라벨)
```

**라벨 파일 예시** (`game_00010.txt`):

```
0 0.619792 0.754167 0.052083 0.069444  ← 플레이어 위치
1 0.927083 0.256944 0.052083 0.069444  ← 장애물 위치
1 0.983333 0.222222 0.052083 0.069444  ← 또 다른 장애물
```

**의미**:

- `0` = 플레이어 (class_id)
- `0.619792 0.754167` = 중심 좌표 (정규화됨)
- `0.052083 0.069444` = 너비, 높이 (정규화됨)

### 2️⃣ **모델 훈련** (Jeewon이 지금 하는 중)

**Jeewon이 실행한 명령어**:

```bash
cd web_app
yolo detect train data=game_dataset/data.yaml model=yolov8n.pt epochs=50
```

**이 명령어가 하는 일**:

1. `game_dataset/data.yaml` 읽기 (어디에 이미지/라벨이 있는지)
2. `yolov8n.pt` 다운로드 (사전 훈련된 작은 모델)
3. **우리 게임 데이터로 학습** (50번 반복)
4. **새로운 모델 파일 생성** ✨

**모델이 생성되는 위치**:

```
runs/detect/train*/weights/
├── best.pt    ← 최고 성능 모델 (이걸 사용!)
├── last.pt    ← 마지막 체크포인트
└── ...
```

**훈련 과정**:

```
Epoch 1/50:  모델이 이미지 보고 "이게 플레이어구나" 학습
Epoch 2/50:  조금 더 정확해짐
...
Epoch 50/50: 최종 모델 완성! → best.pt 생성
```

### 3️⃣ **모델 사용** (훈련 완료 후)

**모델을 어디서 사용하나요?**

**코드 위치**: `web_app/modules/cv_module.py`

```python
# 현재 코드 (시뮬레이션 모드)
def _initialize_model(self):
    if self.model_path:
        # TODO: 실제 구현
        # self.model = YOLO(self.model_path)  ← 이 부분 구현 필요
        print(f"🤖 [Jeewon TODO] YOLOv8 모델 로드: {self.model_path}")
```

**훈련 완료 후 Jeewon이 해야 할 일**:

1. `best.pt`를 `web_app/models/yolo/best.pt`로 복사
2. `cv_module.py`의 TODO 부분 구현:
   ```python
   self.model = YOLO(self.model_path)  # 실제 모델 로드
   ```

---

## 📂 현재 프로젝트 구조

### 데이터 흐름

```
게임 플레이 (웹)
    ↓
데이터 수집 (app.py)
    ↓
web_app/game_dataset/  ← 이미지 + 라벨 저장
    ↓
YOLO 훈련 (Jeewon)
    ↓
runs/detect/train*/weights/best.pt  ← 모델 생성
    ↓
web_app/models/yolo/best.pt  ← 복사해서 저장
    ↓
web_app/modules/cv_module.py  ← 모델 로드해서 사용
```

### 파일 위치 정리

| 단계        | 파일/디렉토리   | 위치                                 | 설명                       |
| ----------- | --------------- | ------------------------------------ | -------------------------- |
| **데이터**  | `game_dataset/` | `web_app/game_dataset/`              | 이미지 + 라벨 (119개)      |
| **설정**    | `data.yaml`     | `web_app/game_dataset/data.yaml`     | 데이터셋 설정              |
| **훈련 중** | `runs/`         | 프로젝트 루트                        | 훈련 중 생성되는 임시 파일 |
| **모델**    | `best.pt`       | `runs/detect/train*/weights/best.pt` | 훈련 완료 후 생성          |
| **저장**    | `models/yolo/`  | `web_app/models/yolo/`               | 최종 모델 저장 위치        |
| **사용**    | `cv_module.py`  | `web_app/modules/cv_module.py`       | 모델 로드해서 사용         |

---

## 🚀 GCP 배포 방법

### 문제점

**현재 상황**:

- 모델 파일(`.pt`)은 `.gitignore`에 포함되어 Git에 커밋 안 됨
- Docker 빌드 시 모델 파일이 이미지에 포함 안 됨
- 배포 시 모델을 찾을 수 없음

### 해결 방법: Cloud Storage 사용

#### 1️⃣ **Jeewon이 할 일 (로컬에서)**

```bash
# 1. 훈련 완료 후 모델 확인
ls runs/detect/train*/weights/best.pt

# 2. 모델을 프로젝트로 복사
cp runs/detect/train*/weights/best.pt web_app/models/yolo/best.pt

# 3. (선택) ONNX 변환 (더 빠름)
# ... ONNX 변환 코드 ...

# 4. Cloud Storage에 업로드
gsutil cp web_app/models/yolo/best.pt \
  gs://distilled-vision-game-data/models/yolo/best.pt

# 또는 ONNX 버전
gsutil cp web_app/models/yolo/best.onnx \
  gs://distilled-vision-game-data/models/yolo/best.onnx
```

#### 2️⃣ **코드 수정 필요**

**`web_app/modules/cv_module.py` 수정**:

```python
def _initialize_model(self):
    if self.model_path:
        # Cloud Storage 경로 처리
        if self.model_path.startswith('gs://'):
            # Cloud Storage에서 다운로드
            local_path = self._download_from_gcs(self.model_path)
            self.model = YOLO(local_path)
        else:
            # 로컬 경로
            self.model = YOLO(self.model_path)

        if self.use_onnx:
            # ONNX 변환 및 최적화
            optimizer = ONNXModelOptimizer()
            onnx_path = optimizer.export_yolo_model(self.model, 'optimized_yolo.onnx')
            self.onnx_session = optimizer.create_inference_session(onnx_path)
```

**`_download_from_gcs()` 메서드 추가 필요**:

```python
def _download_from_gcs(self, gcs_path: str) -> str:
    """Cloud Storage에서 모델 다운로드"""
    from google.cloud import storage

    # gs://bucket/path/to/file.pt → bucket, path 분리
    bucket_name = gcs_path.split('/')[2]
    blob_path = '/'.join(gcs_path.split('/')[3:])

    # 로컬 임시 경로
    local_path = f"/tmp/{blob_path.split('/')[-1]}"

    # 다운로드
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(blob_path)
    blob.download_to_filename(local_path)

    return local_path
```

#### 3️⃣ **배포 설정 수정**

**`web_app/cloudbuild.yaml` 수정**:

```yaml
"--set-env-vars",
"ENVIRONMENT=production,GCS_BUCKET_NAME=distilled-vision-game-data,YOLO_MODEL_PATH=gs://distilled-vision-game-data/models/yolo/best.onnx,YOLO_USE_ONNX=true",
```

#### 4️⃣ **배포 실행**

```bash
cd web_app
gcloud builds submit --config cloudbuild.yaml
```

---

## 📊 현재 상태 체크리스트

### ✅ 완료된 것

- [x] 데이터 수집 (119개 이미지 + 라벨)
- [x] `game_dataset/` 구조 생성
- [x] `data.yaml` 설정 파일
- [x] YOLO 훈련 시작 (epoch 50, 진행 중)

### 🔄 진행 중

- [ ] YOLO 훈련 완료 대기 (Jeewon)
- [ ] 모델 파일 생성 (`best.pt`)

### ❌ 아직 안 된 것

- [ ] 모델을 `web_app/models/yolo/`로 복사
- [ ] `cv_module.py`에서 실제 모델 로드 구현
- [ ] Cloud Storage 업로드
- [ ] GCP 배포 설정 수정
- [ ] 배포 테스트

---

## 🎯 요약

### 데이터 vs 모델

| 항목       | 설명                    | 위치                                           |
| ---------- | ----------------------- | ---------------------------------------------- |
| **데이터** | 게임 화면 이미지 + 라벨 | `web_app/game_dataset/`                        |
| **모델**   | 데이터로 학습한 AI 모델 | `runs/detect/train*/weights/best.pt` (훈련 중) |

### 프로세스

1. **데이터 수집** → `game_dataset/` (완료 ✅)
2. **모델 훈련** → `runs/detect/train*/weights/best.pt` (진행 중 🔄)
3. **모델 저장** → `web_app/models/yolo/best.pt` (예정)
4. **모델 사용** → `cv_module.py`에서 로드 (예정)
5. **GCP 배포** → Cloud Storage에서 다운로드 (예정)

### GCP 배포 핵심

1. **모델을 Cloud Storage에 업로드**
2. **환경 변수로 경로 지정**: `YOLO_MODEL_PATH=gs://...`
3. **코드에서 Cloud Storage 다운로드 로직 추가**
4. **배포 시 자동으로 모델 다운로드 후 사용**

---

**작성일**: 2025-11-22
**상태**: Jeewon이 epoch 50 훈련 중
