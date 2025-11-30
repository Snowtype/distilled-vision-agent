# 🤖 **강화학습 에이전트 훈련 가이드**

> **담당**: Chloe Lee (cl4490)  
> **목표**: 휴리스틱 AI를 넘어서는 학습된 RL 에이전트 개발

---

## 📋 **현재 상태**

### **1. AI 모드 구현 완료 ✅**

- 휴리스틱 기반 AI 에이전트 동작
- 메테오 회피 & 별 수집 로직
- 중앙 유지 전략

### **2. RL 준비 완료 ✅**

- 상태 인코딩 함수: `encode_game_state()` (10차원 벡터)
- 액션 공간: `['stay', 'left', 'right', 'jump']`
- 보상 시스템: 생존(+1), 별 획득(+20), 메테오 충돌(-100)

### **3. 데이터 수집 완료 ✅**

- `web_app/data/gameplay_sessions/`: Human & AI 플레이 데이터
- `web_app/collected_gameplay/`: State-Action-Reward 로그 (JSONL)

---

## 🎯 **RL 훈련 목표**

### **Phase 1: Imitation Learning (Policy Distillation)**

현재 휴리스틱 AI의 행동을 모방하는 정책 네트워크 훈련

### **Phase 2: Reinforcement Learning (PPO/DQN)**

자기 경기를 통해 휴리스틱 AI를 뛰어넘는 성능 달성

---

## 🏗️ **RL 에이전트 아키텍처**

### **상태 공간 (State Space)**

`encode_game_state(game)` 함수가 반환하는 **10차원 벡터**:

```python
state = [
    player_x_normalized,          # [0, 1]
    player_y_normalized,          # [0, 1]
    player_vy_normalized,         # [-1, 1]
    nearest_meteor_dx,            # [-1, 1] (상대 x 거리)
    nearest_meteor_dy,            # [0, 1] (상대 y 거리)
    nearest_meteor_distance,      # [0, 1] (유클리드 거리)
    nearest_star_dx,              # [-1, 1]
    nearest_star_dy,              # [0, 1]
    nearest_star_distance,        # [0, 1]
    on_ground                     # {0, 1} (바닥 접촉 여부)
]
```

### **액션 공간 (Action Space)**

4가지 이산 액션:

```python
actions = ['stay', 'left', 'right', 'jump']
# stay: 아무 행동도 하지 않음
# left: 왼쪽 이동 (-10 pixels)
# right: 오른쪽 이동 (+10 pixels)
# jump: 점프 (vy = -18)
```

### **보상 함수 (Reward Function)**

```python
# 기본 보상
reward = 1.0  # 매 프레임 생존

# 이벤트 보상
if cleared_obstacles > 0:
    reward += cleared_obstacles * 5  # 장애물 회피 성공

if star_collected:
    reward += 20  # 별 획득 (OBJECT_TYPES['star']['reward'])

if game_over:
    reward = -100  # 메테오 충돌 (OBJECT_TYPES['meteor']['reward'])
```

---

## 🚀 **구현 단계**

### **Step 1: 데이터 준비**

#### **훈련 데이터 로드**

```python
import json
from pathlib import Path

def load_training_data():
    """수집된 gameplay 데이터 로드"""
    data_dir = Path("web_app/collected_gameplay")
    episodes = []

    for session_dir in data_dir.iterdir():
        if session_dir.is_dir():
            states_file = session_dir / "states_actions.jsonl"

            episode = []
            with open(states_file, 'r') as f:
                for line in f:
                    record = json.loads(line)
                    episode.append({
                        'state': record['state'],
                        'action': record['action'],
                        'reward': record['reward'],
                        'done': record['done']
                    })

            episodes.append(episode)

    return episodes
```

### **Step 2: 정책 네트워크 정의**

```python
import torch
import torch.nn as nn

class PolicyNetwork(nn.Module):
    """정책 네트워크 (MLP)"""
    def __init__(self, state_dim=10, hidden_dim=128, action_dim=4):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, action_dim),
            nn.Softmax(dim=-1)
        )

    def forward(self, state):
        return self.network(state)
```

### **Step 3: Imitation Learning (지도학습)**

```python
def train_imitation(model, episodes, epochs=100):
    """휴리스틱 AI 모방 학습"""
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)
    criterion = nn.CrossEntropyLoss()

    action_map = {'stay': 0, 'move_left': 1, 'move_right': 2, 'jump': 3}

    for epoch in range(epochs):
        total_loss = 0

        for episode in episodes:
            for step in episode:
                # 상태 인코딩
                state = encode_state_from_record(step['state'])
                state_tensor = torch.FloatTensor(state).unsqueeze(0)

                # 액션 레이블
                action = step['action']
                action_idx = action_map.get(action, 0)
                action_tensor = torch.LongTensor([action_idx])

                # 순전파
                action_probs = model(state_tensor)
                loss = criterion(action_probs, action_tensor)

                # 역전파
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()

                total_loss += loss.item()

        print(f"Epoch {epoch+1}/{epochs}, Loss: {total_loss:.4f}")

    return model
```

### **Step 4: PPO 강화학습**

```python
from torch.distributions import Categorical

class PPOAgent:
    """PPO 에이전트"""
    def __init__(self, state_dim=10, action_dim=4, lr=3e-4):
        self.policy = PolicyNetwork(state_dim, 128, action_dim)
        self.value_net = ValueNetwork(state_dim, 128)
        self.optimizer = torch.optim.Adam(
            list(self.policy.parameters()) + list(self.value_net.parameters()),
            lr=lr
        )

    def select_action(self, state):
        """액션 선택 (확률적)"""
        state_tensor = torch.FloatTensor(state).unsqueeze(0)
        action_probs = self.policy(state_tensor)
        dist = Categorical(action_probs)
        action = dist.sample()
        return action.item(), dist.log_prob(action)

    def update(self, trajectories, clip_epsilon=0.2, epochs=10):
        """PPO 업데이트"""
        for _ in range(epochs):
            for traj in trajectories:
                states = torch.FloatTensor(traj['states'])
                actions = torch.LongTensor(traj['actions'])
                old_log_probs = torch.FloatTensor(traj['log_probs'])
                returns = torch.FloatTensor(traj['returns'])

                # 현재 정책의 log prob
                action_probs = self.policy(states)
                dist = Categorical(action_probs)
                new_log_probs = dist.log_prob(actions)

                # Importance sampling ratio
                ratio = torch.exp(new_log_probs - old_log_probs)

                # Clipped surrogate objective
                advantages = returns - self.value_net(states).squeeze()
                surr1 = ratio * advantages
                surr2 = torch.clamp(ratio, 1-clip_epsilon, 1+clip_epsilon) * advantages
                loss = -torch.min(surr1, surr2).mean()

                # 업데이트
                self.optimizer.zero_grad()
                loss.backward()
                self.optimizer.step()
```

### **Step 5: 모델 통합**

```python
# 모델 저장
torch.save(model.state_dict(), 'web_app/models/rl_agent.pth')

# app.py에서 로드
import torch
from models.policy_network import PolicyNetwork

RL_MODEL = PolicyNetwork(state_dim=10, action_dim=4)
RL_MODEL.load_state_dict(torch.load('models/rl_agent.pth'))
RL_MODEL.eval()
RL_MODEL_AVAILABLE = True
```

---

## 📊 **평가 지표**

### **성공 기준 (프로젝트 제안서 기준)**

1. **Imitation Accuracy**: ≥75% action agreement (휴리스틱 AI 모방)
2. **Self-Play Performance Gain**: +20% 생존 시간 향상
3. **Real-Time Inference**: ≤16.7 ms/frame (60 FPS)
4. **Absolute Benchmark**: 평균 생존 시간 119초

### **측정 방법**

```python
def evaluate_agent(model, num_episodes=100):
    """에이전트 성능 평가"""
    survival_times = []
    scores = []

    for _ in range(num_episodes):
        # 게임 실행 (웹 API 호출 or 로컬 시뮬레이션)
        result = play_game_with_agent(model)
        survival_times.append(result['time'])
        scores.append(result['score'])

    return {
        'avg_survival': np.mean(survival_times),
        'avg_score': np.mean(scores),
        'max_survival': np.max(survival_times),
        'std_survival': np.std(survival_times)
    }
```

---

## 🛠️ **디버깅 & 시각화**

### **TensorBoard 로깅**

```python
from torch.utils.tensorboard import SummaryWriter

writer = SummaryWriter('runs/rl_training')

for episode in range(num_episodes):
    # 훈련...
    writer.add_scalar('Loss/policy', policy_loss, episode)
    writer.add_scalar('Reward/episode', total_reward, episode)
    writer.add_scalar('Survival/time', survival_time, episode)

writer.close()
```

### **학습 곡선 시각화**

```python
import matplotlib.pyplot as plt

plt.figure(figsize=(12, 4))

plt.subplot(1, 3, 1)
plt.plot(episode_rewards)
plt.title('Episode Reward')
plt.xlabel('Episode')
plt.ylabel('Total Reward')

plt.subplot(1, 3, 2)
plt.plot(survival_times)
plt.title('Survival Time')
plt.xlabel('Episode')
plt.ylabel('Time (s)')

plt.subplot(1, 3, 3)
plt.plot(losses)
plt.title('Training Loss')
plt.xlabel('Iteration')
plt.ylabel('Loss')

plt.tight_layout()
plt.savefig('training_progress.png')
```

---

## 🔗 **참고 자료**

### **논문**

- [Proximal Policy Optimization (Schulman et al., 2017)](https://arxiv.org/abs/1707.06347)
- [Deep Q-Network (Mnih et al., 2015)](https://www.nature.com/articles/nature14236)

### **코드 예제**

- [OpenAI Spinning Up: PPO](https://spinningup.openai.com/en/latest/algorithms/ppo.html)
- [Stable-Baselines3](https://stable-baselines3.readthedocs.io/)

### **프로젝트 내 참고 파일**

- `src/utils/rl_instrumentation.py`: RL 계측 유틸리티 (래리 작성)
- `web_app/app.py`: 게임 환경 & 보상 함수
- `DATA_STRATEGY.md`: 데이터 저장 전략

---

## 🎓 **클로에게 전달사항**

### **현재 준비된 것**

1. ✅ **게임 환경**: Flask-SocketIO 기반, 완전히 동작
2. ✅ **상태 인코딩**: `encode_game_state()` 함수 (10차원)
3. ✅ **보상 함수**: 생존(+1), 별(+20), 충돌(-100)
4. ✅ **데이터 수집**: 수백 개의 gameplay 세션 (Human + AI)
5. ✅ **휴리스틱 AI**: 베이스라인 성능 (모방 학습 타겟)

### **클로가 할 일**

1. **Imitation Learning**: 휴리스틱 AI 모방 (≥75% 정확도)
2. **PPO/DQN 훈련**: 자기 경기로 성능 향상 (+20% 생존 시간)
3. **모델 최적화**: ONNX 변환 후 래리가 배포
4. **실험 추적**: TensorBoard/W&B로 학습 곡선 기록

### **다음 미팅 전까지**

- [ ] 기본 정책 네트워크 구현 (PyTorch)
- [ ] Imitation Learning 파이프라인 구축
- [ ] 첫 번째 학습 실험 실행 & 결과 공유

---

**📝 작성자**: Minsuk Kim (mk4434)  
**📅 최종 수정**: 2025-11-18  
**🔗 관련 문서**: `IMPLEMENTATION_ROADMAP.md`, `TEAM_BRIEFING.md`
