# 🛠️ Git 명령어 완벽 가이드

**프로젝트**: Distilled Vision Agent  
**팀**: Prof.Peter.backward()  
**업데이트**: 2025-11-18

---

## 📊 현재 브랜치 상태 (2025-11-18 업데이트)

### ✅ **최신 상태 브랜치**

```bash
main                    020fede  ✅ 최신 (가장 최근)
├── origin/main         020fede  ✅ 동기화됨
├── team/main           020fede  ✅ 동기화됨
├── minsuk-web-deployment 3b77599  ✅ 최신으로 업데이트됨
└── main-update         a2361f4  ✅ 최신으로 업데이트됨
```

### ⚠️ **오래된 브랜치 (병합 필요)**

```bash
team/chloe              e5a47cb  ⏸️ 뒤처짐
team/jeewon             3528d1c  ⏸️ 뒤처짐
team/dev                2714092  ⏸️ 뒤처짐
team/main-update        abb044e  ⏸️ 원격 브랜치 뒤처짐
team/minsuk-web-deployment abb044e  ⏸️ 원격 브랜치 뒤처짐
```

---

## 🚀 일상 작업 명령어

### 1. **작업 시작 전 필수 체크**

```bash
# 현재 브랜치 확인
git branch

# 현재 상태 확인
git status

# 최신 변경사항 가져오기
git pull origin main
```

### 2. **새로운 기능 개발 시작**

```bash
# main 브랜치에서 시작
git checkout main
git pull origin main

# 새 기능 브랜치 생성 (명명 규칙: feature/기능명)
git checkout -b feature/yolo-training

# 또는 버그 수정 (명명 규칙: fix/버그명)
git checkout -b fix/data-collection-bug
```

### 3. **작업 중 저장**

```bash
# 변경된 파일 확인
git status

# 특정 파일만 스테이징
git add web_app/app.py
git add src/models/yolo_detector.py

# 모든 변경사항 스테이징 (주의!)
git add .

# 커밋 (의미 있는 메시지 작성)
git commit -m "✨ Add YOLO detection module"

# 스테이징 + 커밋 동시에 (수정된 파일만)
git commit -am "🐛 Fix data collection bug"
```

### 4. **원격 저장소에 푸시**

```bash
# 현재 브랜치를 origin에 푸시
git push origin feature/yolo-training

# 최초 푸시 시 (upstream 설정)
git push -u origin feature/yolo-training

# 이후부터는 간단하게
git push
```

---

## 🔄 브랜치 관리 명령어

### 1. **브랜치 조회**

```bash
# 로컬 브랜치 목록
git branch

# 원격 브랜치 포함 전체 목록
git branch -a

# 각 브랜치의 최신 커밋 정보
git branch -v

# 원격 추적 정보까지 상세히
git branch -a -vv
```

### 2. **브랜치 전환**

```bash
# 기존 브랜치로 전환
git checkout main

# 새 브랜치 생성하면서 전환
git checkout -b new-feature

# 최신 버전 (git 2.23+)
git switch main
git switch -c new-feature
```

### 3. **브랜치 업데이트**

```bash
# main의 최신 변경사항을 현재 브랜치에 병합
git checkout feature/my-work
git merge main

# 또는 rebase (커밋 히스토리를 깔끔하게)
git rebase main
```

### 4. **브랜치 삭제**

```bash
# 로컬 브랜치 삭제 (병합된 경우)
git branch -d old-feature

# 강제 삭제 (병합 안 된 경우도)
git branch -D old-feature

# 원격 브랜치 삭제
git push origin --delete old-feature
```

---

## 🔍 히스토리 & 비교 명령어

### 1. **커밋 히스토리 보기**

```bash
# 기본 로그
git log

# 한 줄로 간단하게
git log --oneline

# 그래프로 시각화 (추천!)
git log --oneline --graph --all --decorate

# 최근 10개만
git log --oneline -10

# 특정 파일의 히스토리
git log -- web_app/app.py

# 작성자별 필터링
git log --author="Minsuk"
```

### 2. **변경사항 비교**

```bash
# 작업 디렉토리 vs 스테이징
git diff

# 스테이징 vs 최근 커밋
git diff --staged

# 두 브랜치 비교
git diff main..feature/yolo

# 두 커밋 비교
git diff 020fede..91aebe3

# 특정 파일만 비교
git diff main -- web_app/app.py
```

### 3. **커밋 정보 상세히 보기**

```bash
# 특정 커밋의 상세 정보
git show 020fede

# 최근 커밋 상세 정보
git show HEAD

# 이전 커밋 (HEAD~1 = HEAD의 1개 이전)
git show HEAD~1
```

---

## ⚙️ 고급 명령어

### 1. **스태시 (임시 저장)**

```bash
# 현재 변경사항 임시 저장
git stash

# 설명과 함께 저장
git stash save "작업 중인 YOLO 코드"

# 저장된 스태시 목록
git stash list

# 가장 최근 스태시 복원
git stash pop

# 특정 스태시 복원
git stash apply stash@{0}

# 스태시 삭제
git stash drop stash@{0}
```

### 2. **커밋 수정**

```bash
# 최근 커밋 메시지 수정
git commit --amend -m "새로운 커밋 메시지"

# 최근 커밋에 파일 추가 (메시지 유지)
git add forgotten_file.py
git commit --amend --no-edit

# 최근 커밋 취소 (변경사항은 유지)
git reset --soft HEAD~1

# 최근 커밋 완전 취소 (변경사항도 삭제, 주의!)
git reset --hard HEAD~1
```

### 3. **충돌 해결**

```bash
# 병합 중 충돌 발생 시
git status  # 충돌 파일 확인

# 우리 버전 사용 (현재 브랜치)
git checkout --ours conflicted_file.py

# 그들 버전 사용 (병합하려는 브랜치)
git checkout --theirs conflicted_file.py

# 수동 해결 후
git add conflicted_file.py
git commit

# 병합 취소
git merge --abort
```

### 4. **원격 저장소 관리**

```bash
# 원격 저장소 목록
git remote -v

# 새 원격 저장소 추가
git remote add team https://github.com/gitgutgit/YOLO-You-Only-Live-Once.git

# 원격 저장소에서 최신 정보 가져오기 (병합 X)
git fetch origin
git fetch team

# 원격 브랜치 최신화
git fetch --all

# 원격 브랜치 삭제된 것 로컬에 반영
git fetch --prune
```

---

## 🎯 프로젝트 맞춤 워크플로우

### **Minsuk (인프라 & 웹)**

```bash
# 1. 웹 앱 개발 시작
git checkout main
git pull origin main
git checkout -b minsuk/web-feature

# 2. 작업 후 커밋
git add web_app/
git commit -m "🌐 Add new web feature"

# 3. 정기적으로 main 최신화
git fetch origin
git merge origin/main

# 4. 완료 후 푸시
git push origin minsuk/web-feature

# 5. GitHub에서 Pull Request 생성
```

### **Jeewon (YOLO & CV)**

```bash
# 1. YOLO 개발 시작
git checkout main
git pull origin main
git checkout -b jeewon/yolo-training

# 2. 작업
git add src/models/yolo_detector.py
git commit -m "👁️ Add YOLO detection logic"

# 3. 푸시
git push origin jeewon/yolo-training
```

### **Chloe (RL & AI)**

```bash
# 1. RL 개발 시작
git checkout main
git pull origin main
git checkout -b chloe/rl-training

# 2. 작업
git add src/training/ppo_trainer.py
git commit -m "🤖 Add PPO training loop"

# 3. 푸시
git push origin chloe/rl-training
```

---

## 🚨 응급 상황 대처

### 1. **잘못된 브랜치에 커밋한 경우**

```bash
# 커밋 취소 (변경사항은 유지)
git reset --soft HEAD~1

# 올바른 브랜치로 전환
git checkout correct-branch

# 다시 커밋
git commit -m "올바른 커밋"
```

### 2. **작업 중인데 다른 브랜치로 가야 할 때**

```bash
# 현재 작업 임시 저장
git stash

# 다른 브랜치로 전환
git checkout other-branch

# 작업 후 다시 돌아와서
git checkout original-branch
git stash pop
```

### 3. **원격과 로컬이 꼬였을 때**

```bash
# 원격 상태 확인
git fetch origin

# 원격 브랜치로 완전히 리셋 (주의: 로컬 변경사항 삭제!)
git reset --hard origin/main

# 또는 새로 시작
git checkout -b backup-branch  # 백업 생성
git checkout main
git reset --hard origin/main
```

### 4. **큰 파일을 실수로 커밋한 경우**

```bash
# 최근 커밋에서 파일 제거
git rm --cached large_file.zip
git commit --amend -m "Remove large file"

# 이미 푸시한 경우 (협업자와 조율 필요)
git push origin main --force
```

---

## 📋 체크리스트 & 베스트 프랙티스

### ✅ **커밋 전 체크리스트**

- [ ] `git status`로 변경사항 확인
- [ ] 불필요한 파일 제외 (`.pyc`, `__pycache__`, `venv/` 등)
- [ ] 의미 있는 커밋 메시지 작성
- [ ] 너무 많은 변경사항을 한 커밋에 포함하지 않기

### ✅ **푸시 전 체크리스트**

- [ ] 로컬에서 테스트 완료
- [ ] `git pull origin main`으로 최신화
- [ ] 충돌 해결 완료
- [ ] 커밋 히스토리 확인 (`git log`)

### ✅ **병합 전 체크리스트**

- [ ] 모든 테스트 통과
- [ ] 팀원 코드 리뷰 완료
- [ ] README 및 문서 업데이트
- [ ] 충돌 없음 확인

---

## 🎨 커밋 메시지 이모지 가이드

| 이모지 | 코드                 | 의미                |
| ------ | -------------------- | ------------------- |
| ✨     | `:sparkles:`         | 새로운 기능 추가    |
| 🐛     | `:bug:`              | 버그 수정           |
| 🔥     | `:fire:`             | 코드/파일 삭제      |
| 📝     | `:memo:`             | 문서 작성/수정      |
| 🎨     | `:art:`              | 코드 구조/형식 개선 |
| ⚡️    | `:zap:`              | 성능 개선           |
| 🚀     | `:rocket:`           | 배포 관련           |
| 🔧     | `:wrench:`           | 설정 파일 수정      |
| ♻️     | `:recycle:`          | 코드 리팩토링       |
| 🚧     | `:construction:`     | 작업 진행 중        |
| 💄     | `:lipstick:`         | UI/스타일 개선      |
| 🔒     | `:lock:`             | 보안 이슈 수정      |
| ⬆️     | `:arrow_up:`         | 의존성 업그레이드   |
| ⬇️     | `:arrow_down:`       | 의존성 다운그레이드 |
| ➕     | `:heavy_plus_sign:`  | 의존성 추가         |
| ➖     | `:heavy_minus_sign:` | 의존성 제거         |

### 예시

```bash
git commit -m "✨ Add YOLO object detection"
git commit -m "🐛 Fix data collection memory leak"
git commit -m "📝 Update README with new architecture"
git commit -m "⚡️ Optimize inference speed to 60 FPS"
git commit -m "🚀 Deploy to GCP Cloud Run"
```

---

## 🔗 유용한 Git 별칭 (Alias)

프로젝트 루트에서 실행:

```bash
# 자주 쓰는 명령어 단축키 설정
git config alias.st status
git config alias.co checkout
git config alias.br branch
git config alias.ci commit
git config alias.unstage 'reset HEAD --'
git config alias.last 'log -1 HEAD'
git config alias.lg "log --oneline --graph --all --decorate"

# 사용 예시
git st         # git status
git co main    # git checkout main
git br         # git branch
git lg         # 예쁜 로그
```

---

## 📞 도움말 & 추가 리소스

### **Git 명령어 도움말**

```bash
# 특정 명령어 도움말
git help commit
git help merge
git help rebase

# 간단한 도움말
git commit -h
git merge -h
```

### **유용한 리소스**

- **공식 문서**: https://git-scm.com/doc
- **Git 치트시트**: https://education.github.com/git-cheat-sheet-education.pdf
- **Interactive Git 학습**: https://learngitbranching.js.org/

---

**작성자**: Minsuk Kim (mk4434)  
**팀**: Prof.Peter.backward()  
**최종 업데이트**: 2025-11-18
