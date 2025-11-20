# ☁️ Cloud Storage 설정 가이드

## 📋 Phase 1 완료: 리더보드 Cloud Storage 연동

### ✅ 완료된 작업

1. **`requirements.txt`**: `google-cloud-storage` 추가
2. **`storage_manager.py`**: Cloud Storage 관리 모듈 생성
   - GCS와 로컬 파일 시스템 모두 지원 (자동 fallback)
   - 리더보드 읽기/쓰기 기능
   - 통계 API
3. **`.env.example`**: 환경 변수 템플릿
4. **`app.py`**: Storage Manager 연동

---

## 🚀 로컬에서 테스트하기

### 1️⃣ 의존성 설치

```bash
cd web_app
pip install -r requirements.txt
```

### 2️⃣ 환경 변수 설정 (로컬 개발용)

```bash
# .env 파일 생성
cp .env.example .env
```

`.env` 파일 내용 (로컬 테스트):

```bash
ENVIRONMENT=development
LOCAL_DATA_DIR=./data
PORT=5002
DEBUG=True
```

### 3️⃣ 서버 실행

```bash
python app.py
```

출력 예시:

```
🎮 게임 서버 시작!
🌐 http://localhost:5002
🤖 AI 모드: 휴리스틱 기반 (RL 모델 대기 중)
📦 환경: development
💾 로컬 스토리지 사용: /path/to/data
```

✅ **로컬에서는 기존과 동일하게 작동** (파일 시스템 사용)

---

## ☁️ GCP Cloud Storage 연동하기

### 1️⃣ GCP 버킷 생성

```bash
# GCP 프로젝트 확인
gcloud config get-value project
# 출력: vision-final-478501

# Cloud Storage 버킷 생성
gsutil mb -p vision-final-478501 -c STANDARD -l us-central1 gs://distilled-vision-game-data

# 버킷 확인
gsutil ls gs://distilled-vision-game-data
```

### 2️⃣ 버킷 구조 생성 (선택사항)

```bash
# 리더보드 디렉토리 생성 (빈 객체)
echo '{"scores": []}' | gsutil cp - gs://distilled-vision-game-data/leaderboard/leaderboard.json
```

### 3️⃣ 로컬에서 GCS 테스트 (선택사항)

로컬에서 GCS를 테스트하려면 서비스 계정 키가 필요합니다:

```bash
# 1. 서비스 계정 생성 (GCP 콘솔 또는 CLI)
gcloud iam service-accounts create game-storage-admin \
    --display-name="Game Storage Admin"

# 2. Storage Admin 권한 부여
gcloud projects add-iam-policy-binding vision-final-478501 \
    --member="serviceAccount:game-storage-admin@vision-final-478501.iam.gserviceaccount.com" \
    --role="roles/storage.admin"

# 3. 키 다운로드
gcloud iam service-accounts keys create ./credentials/gcp-service-account.json \
    --iam-account=game-storage-admin@vision-final-478501.iam.gserviceaccount.com
```

`.env` 파일 업데이트:

```bash
ENVIRONMENT=production
GCS_BUCKET_NAME=distilled-vision-game-data
GOOGLE_APPLICATION_CREDENTIALS=./credentials/gcp-service-account.json
```

서버 재실행:

```bash
python app.py
```

출력:

```
☁️ Cloud Storage 사용: gs://distilled-vision-game-data
```

---

## 🚢 GCP Cloud Run 배포

### 1️⃣ cloudbuild.yaml 업데이트 (이미 완료)

Cloud Run 환경에서는 자동으로 GCS를 사용합니다:

- `ENVIRONMENT=production` 설정됨
- 서비스 계정 자동 인증 (키 불필요)

### 2️⃣ Cloud Run 배포

```bash
cd web_app
./quick_deploy.sh
```

또는:

```bash
gcloud run deploy distilled-vision-agent \
    --source . \
    --region us-central1 \
    --allow-unauthenticated \
    --set-env-vars ENVIRONMENT=production,GCS_BUCKET_NAME=distilled-vision-game-data
```

### 3️⃣ Cloud Run 서비스 계정 권한 부여

```bash
# Cloud Run 서비스 계정 확인
SERVICE_ACCOUNT=$(gcloud run services describe distilled-vision-agent \
    --region us-central1 --format="value(spec.template.spec.serviceAccountName)")

# Storage 권한 부여
gcloud projects add-iam-policy-binding vision-final-478501 \
    --member="serviceAccount:${SERVICE_ACCOUNT}" \
    --role="roles/storage.admin"
```

---

## 🧪 테스트 체크리스트

### 로컬 테스트

- [ ] `pip install -r requirements.txt` 성공
- [ ] `.env` 파일 생성
- [ ] `python app.py` 서버 실행
- [ ] 게임 플레이 → 리더보드 저장 확인
- [ ] `data/leaderboard.json` 파일 생성 확인

### GCS 테스트 (선택)

- [ ] 버킷 생성 완료
- [ ] 서비스 계정 키 설정
- [ ] `ENVIRONMENT=production` 설정
- [ ] 게임 플레이 → GCS에 저장 확인
- [ ] `gsutil cat gs://distilled-vision-game-data/leaderboard/leaderboard.json` 출력 확인

### Cloud Run 배포

- [ ] Cloud Run 배포 성공
- [ ] 게임 플레이 → 리더보드 업데이트 확인
- [ ] 서버 재시작해도 데이터 유지 확인 ✅

---

## 📊 현재 상태

| 기능               | 로컬 개발 | GCP 배포 |
| ------------------ | --------- | -------- |
| 리더보드 읽기/쓰기 | ✅        | ✅       |
| 게임 세션 저장     | ✅ (로컬) | ⏳ 다음  |
| 이미지 저장        | ⏳ 다음   | ⏳ 다음  |

---

## 🔜 다음 단계 (Phase 2)

1. **게임 세션 저장** → Cloud Storage로 이동
2. **이미지 프레임 캡처** → Cloud Storage에 업로드
3. **팀원 데이터 접근** → Jay, Chloe, Larry가 GCS에서 직접 다운로드

---

## 🆘 문제 해결

### Q1. "ImportError: google-cloud-storage"

```bash
pip install google-cloud-storage
```

### Q2. 로컬에서 GCS 연결 안 됨

→ 정상입니다! 로컬에서는 자동으로 `./data/` 폴더 사용 (fallback)

### Q3. Cloud Run에서 리더보드 안 보임

```bash
# 서비스 계정 권한 확인
gcloud run services describe distilled-vision-agent --region us-central1
# Storage Admin 권한 부여 (위 3️⃣ 참고)
```

### Q4. 기존 로컬 데이터 유지하고 싶음

```bash
# 로컬 데이터를 GCS로 업로드
gsutil cp data/leaderboard.json gs://distilled-vision-game-data/leaderboard/
```

---

## 📝 참고

- 버킷 이름: `distilled-vision-game-data`
- 리전: `us-central1` (Cloud Run과 동일)
- 비용: ~$0.02/GB/월 (매우 저렴)
