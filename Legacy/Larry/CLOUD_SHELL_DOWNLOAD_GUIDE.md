# 📥 Cloud Shell에서 로컬로 파일 다운로드 가이드

## ⚠️ 중요: Cloud Shell은 웹 기반 터미널입니다

Cloud Shell에서 `gsutil cp`로 다운로드한 파일은 **Cloud Shell의 임시 스토리지**에 저장됩니다.
**로컬 컴퓨터로 자동 다운로드되지 않습니다!**

---

## 🔍 방법 1: Cloud Shell 웹 UI에서 다운로드 (가장 쉬움)

### 1. Cloud Shell에서 파일 확인

```bash
# 현재 디렉토리 확인
pwd
# 출력: /home/dataengineboost

# 다운로드한 파일 확인
ls -lh WXdq3EBe/
```

### 2. Cloud Shell 웹 UI에서 다운로드

1. **Cloud Shell 창 오른쪽 상단**에 **"⋮" (점 3개) 메뉴** 클릭
2. **"Download file"** 선택
3. 파일 경로 입력: `WXdq3EBe/frame_00010.png` (또는 폴더 전체)
4. 다운로드 시작

### 3. 폴더 전체 다운로드 (zip으로 압축)

```bash
# zip으로 압축
zip -r WXdq3EBe.zip WXdq3EBe/

# 그 다음 Cloud Shell 웹 UI에서 "Download file"로 WXdq3EBe.zip 다운로드
```

---

## 🔍 방법 2: 로컬에서 직접 gsutil 사용 (추천!)

### 로컬 Mac에서 직접 다운로드

```bash
# 1. gcloud CLI 설치 확인 (이미 설치되어 있어야 함)
gcloud --version

# 2. 프로젝트 설정
gcloud config set project vision-final-478501

# 3. 인증 (처음 한 번만)
gcloud auth login

# 4. Cloud Storage에서 직접 다운로드
cd ~/Downloads  # 또는 원하는 폴더
gsutil -m cp -r \
  "gs://distilled-vision-game-data/gameplay/frames/2025-11-20/WXdq3EBe" \
  .

# 5. 확인
ls -lh WXdq3EBe/
```

**장점**: Cloud Shell을 거치지 않고 바로 로컬에 다운로드!

---

## 🔍 방법 3: Cloud Shell에서 로컬로 파일 전송 (고급)

### scp 사용 (SSH 필요)

```bash
# Cloud Shell에서 로컬로 전송
# 주의: Cloud Shell의 SSH 접근이 필요함
scp -r WXdq3EBe/ user@your-local-ip:/path/to/destination/
```

---

## 📋 현재 상황 정리

### Cloud Shell에서 다운로드한 파일 위치

```
/home/dataengineboost/WXdq3EBe/
├── frame_00010.png
├── frame_00020.png
├── frame_00030.png
...
└── frame_00130.png
```

### 이 파일들을 로컬로 가져오는 방법

1. **가장 쉬움**: Cloud Shell 웹 UI → "Download file"
2. **가장 빠름**: 로컬에서 직접 `gsutil` 사용
3. **대용량**: zip으로 압축 후 다운로드

---

## 🎯 추천 방법

**로컬 Mac에서 직접 다운로드** (방법 2)를 추천합니다:

```bash
# 로컬 터미널에서 실행
cd ~/Downloads
gsutil -m cp -r \
  "gs://distilled-vision-game-data/gameplay/frames/2025-11-20/WXdq3EBe" \
  .
```

이렇게 하면:

- ✅ Cloud Shell을 거치지 않음
- ✅ 빠른 다운로드
- ✅ 로컬에 바로 저장

---

## 📝 참고: Cloud Shell 파일 시스템

- **홈 디렉토리**: `/home/dataengineboost/` (또는 사용자명)
- **임시 스토리지**: 5GB (무료)
- **영구 저장**: `~/cloudshell-home/` (재접속해도 유지)
- **자동 삭제**: 120일 비활성 시 삭제

---

## 🆘 문제 해결

### Q1. "gsutil: command not found" (로컬에서)

```bash
# gcloud CLI 설치
# macOS
brew install google-cloud-sdk

# 또는 공식 설치 스크립트
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

### Q2. "Access Denied" 오류

```bash
# 인증 확인
gcloud auth list

# 재인증
gcloud auth login
```

### Q3. Cloud Shell에서 파일이 안 보임

```bash
# 현재 디렉토리 확인
pwd

# 파일 찾기
find ~ -name "WXdq3EBe" -type d
```

---

## 📊 다운로드 속도 비교

| 방법           | 속도 | 편의성     | 추천      |
| -------------- | ---- | ---------- | --------- |
| Cloud Shell UI | 보통 | ⭐⭐⭐     | 대용량 시 |
| 로컬 gsutil    | 빠름 | ⭐⭐⭐⭐⭐ | **추천**  |
| scp            | 느림 | ⭐⭐       | 비추천    |
