#!/usr/bin/env python3
"""
간단하고 확실하게 작동하는 게임
"""

from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
import time
import random
import threading
import json
from pathlib import Path
from datetime import datetime
import numpy as np

app = Flask(__name__)
app.config['SECRET_KEY'] = 'game-secret'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# 게임 설정
WIDTH = 960
HEIGHT = 720
PLAYER_SIZE = 50
OBSTACLE_SIZE = 50

# RL 모델 플래그 (클로가 나중에 학습시킬 모델)
RL_MODEL_AVAILABLE = False
RL_MODEL = None

try:
    # PyTorch 모델 로드 시도 (아직 없음)
    # import torch
    # RL_MODEL = torch.load('models/rl_agent.pth')
    # RL_MODEL_AVAILABLE = True
    print("⚠️ RL 모델 없음 - 휴리스틱 AI 사용")
except Exception as e:
    print(f"⚠️ RL 모델 로드 실패: {e}")

# 객체 타입 정의
OBJECT_TYPES = {
    'meteor': {
        'color': '#FF4444',
        'size': 50,
        'vy': 5,
        'score': 0,
        'reward': -100
    },
    'star': {
        'color': '#FFD700',
        'size': 30,
        'vy': 3,
        'score': 10,
        'reward': 20
    }
}

# 데이터 저장 경로
DATA_DIR = Path(__file__).parent / 'data'
LEADERBOARD_FILE = DATA_DIR / 'leaderboard.json'
GAMEPLAY_DIR = DATA_DIR / 'gameplay' / 'raw'
COLLECTED_DIR = Path(__file__).parent / 'collected_gameplay'  # 훈련 데이터

# 디렉토리 생성
DATA_DIR.mkdir(exist_ok=True)
GAMEPLAY_DIR.mkdir(parents=True, exist_ok=True)
COLLECTED_DIR.mkdir(exist_ok=True)

# 활성 게임들
games = {}

# 리더보드 로드
def load_leaderboard():
    """리더보드 로드"""
    if LEADERBOARD_FILE.exists():
        with open(LEADERBOARD_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'scores': []}

def save_leaderboard(leaderboard):
    """리더보드 저장"""
    with open(LEADERBOARD_FILE, 'w', encoding='utf-8') as f:
        json.dump(leaderboard, f, indent=2, ensure_ascii=False)

def add_score(player_name, score, survival_time, mode, session_id):
    """점수 추가"""
    leaderboard = load_leaderboard()
    
    leaderboard['scores'].append({
        'player': player_name,
        'score': score,
        'time': round(survival_time, 2),
        'mode': mode,
        'date': datetime.now().isoformat(),
        'session_id': session_id
    })
    
    # 점수순 정렬 (내림차순)
    leaderboard['scores'].sort(key=lambda x: x['score'], reverse=True)
    
    # 상위 100개만 유지
    leaderboard['scores'] = leaderboard['scores'][:100]
    
    save_leaderboard(leaderboard)
    return leaderboard

def save_gameplay_session(game):
    """게임 세션 저장 (팀원들의 훈련 데이터용)"""
    # 1. 메타데이터 저장 (기존)
    session_file = GAMEPLAY_DIR / f"session_{int(time.time())}_{game.sid[:8]}.json"
    
    session_data = {
        'session_id': game.sid,
        'mode': game.mode,
        'score': game.score,
        'survival_time': time.time() - game.start_time,
        'total_frames': game.frame,
        'final_state': {
            'player_x': game.player_x,
            'player_y': game.player_y,
            'obstacles_count': len(game.obstacles)
        },
        'timestamp': datetime.now().isoformat()
    }
    
    with open(session_file, 'w', encoding='utf-8') as f:
        json.dump(session_data, f, indent=2, ensure_ascii=False)
    
    print(f"💾 게임 세션 저장: {session_file.name}")
    
    # 2. 훈련 데이터 저장 (State-Action-Reward)
    if len(game.collected_states) > 0:
        save_training_data(game, session_data)
    
    return str(session_file)

def save_training_data(game, session_metadata):
    """훈련 데이터 저장 (제이 & 클로용)"""
    # 세션별 디렉토리 생성
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    session_dir = COLLECTED_DIR / f"session_{timestamp}_{game.mode}"
    session_dir.mkdir(exist_ok=True)
    
    # 메타데이터 저장
    metadata_file = session_dir / "metadata.json"
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(session_metadata, f, indent=2, ensure_ascii=False)
    
    # State-Action-Reward 저장 (JSONL 포맷 - 클로용)
    states_file = session_dir / "states_actions.jsonl"
    with open(states_file, 'w', encoding='utf-8') as f:
        for state_record in game.collected_states:
            f.write(json.dumps(state_record, ensure_ascii=False) + '\n')
    
    # Bounding Box 라벨 저장 (JSONL 포맷 - 제이용)
    bboxes_file = session_dir / "bboxes.jsonl"
    with open(bboxes_file, 'w', encoding='utf-8') as f:
        for state_record in game.collected_states:
            frame_num = state_record['frame']
            state = state_record['state']
            
            # 게임 상태에서 bbox 추출
            objects = []
            
            # 플레이어 bbox
            objects.append({
                'class': 'player',
                'x': state['player_x'],
                'y': state['player_y'],
                'w': PLAYER_SIZE,
                'h': PLAYER_SIZE
            })
            
            # 장애물 bbox
            for obs in state['obstacles']:
                objects.append({
                    'class': 'obstacle',
                    'x': obs['x'],
                    'y': obs['y'],
                    'w': obs['size'],
                    'h': obs['size']
                })
            
            f.write(json.dumps({'frame': frame_num, 'objects': objects}, ensure_ascii=False) + '\n')
    
    print(f"📊 훈련 데이터 저장:")
    print(f"   - 디렉토리: {session_dir.name}")
    print(f"   - State-Action 로그: {len(game.collected_states)}개")
    print(f"   - Bbox 라벨: {len(game.collected_states)}개")
    
    return str(session_dir)

class Game:
    def __init__(self, sid):
        self.sid = sid
        self.reset()
        
    def reset(self):
        """게임 상태 초기화"""
        self.player_x = WIDTH // 2
        self.player_y = HEIGHT // 2
        self.player_vy = 0
        self.obstacles = []
        self.score = 0
        self.running = False
        self.mode = "human"
        self.player_name = None  # 플레이어 이름
        self.start_time = time.time()
        self.frame = 0
        self.game_over = False
        
        # 훈련 데이터 수집
        self.collected_states = []  # State-Action-Reward 로그
        self.last_action = "stay"
        
        # 이벤트 플래그
        self.star_collected = False  # 별 획득 플래그
        
    def update(self):
        """물리 업데이트"""
        if self.game_over:
            return
        
        # 이벤트 플래그 초기화
        self.star_collected = False
        
        # 📊 현재 상태 저장 (업데이트 전)
        current_state = {
            'player_x': self.player_x,
            'player_y': self.player_y,
            'player_vy': self.player_vy,
            'obstacles': [{'x': o['x'], 'y': o['y'], 'size': o['size']} for o in self.obstacles[:5]]
        }
        
        # 중력
        self.player_vy += 1
        self.player_y += self.player_vy
        
        # 바닥 충돌
        if self.player_y >= HEIGHT - PLAYER_SIZE:
            self.player_y = HEIGHT - PLAYER_SIZE
            self.player_vy = 0
        
        # 장애물 이동 (대각선)
        for obs in self.obstacles:
            obs['x'] += obs.get('vx', 0)  # 좌우 이동
            obs['y'] += obs.get('vy', 5)  # 하강
            
            # 화면 밖으로 나가면 반대편에서 등장 (좌우 wrap)
            if obs['x'] < -obs.get('size', OBSTACLE_SIZE):
                obs['x'] = WIDTH
            elif obs['x'] > WIDTH:
                obs['x'] = -obs.get('size', OBSTACLE_SIZE)
        
        # 화면 밖 장애물 제거 + 점수 증가
        before_count = len(self.obstacles)
        self.obstacles = [o for o in self.obstacles if o['y'] < HEIGHT]
        cleared = before_count - len(self.obstacles)
        self.score += cleared
        
        # 충돌 검사
        self.check_collisions()
        
        # 📊 보상 계산
        reward = 1.0  # 생존 기본 보상
        
        # 화면 밖으로 나간 객체 보상 (회피 성공)
        if cleared > 0:
            reward += cleared * 5
        
        # 게임 오버 (메테오 충돌)
        if self.game_over:
            reward = OBJECT_TYPES['meteor']['reward']  # -100
        
        # 별 획득 보상은 check_collisions()에서 별도 처리
        
        # 📊 State-Action-Reward 저장 (클로 훈련용)
        self.collected_states.append({
            'frame': self.frame,
            'state': current_state,
            'action': self.last_action,
            'reward': reward,
            'done': self.game_over
        })
        
        # 새 객체 생성 (메테오 또는 별)
        if random.random() < 0.05:
            # 10% 확률로 별, 나머지는 메테오
            obj_type = 'star' if random.random() < 0.1 else 'meteor'
            obj_config = OBJECT_TYPES[obj_type]
            
            self.obstacles.append({
                'type': obj_type,
                'x': random.randint(0, WIDTH - obj_config['size']),
                'y': -obj_config['size'],
                'vx': random.randint(-2, 2),  # 대각선 이동
                'vy': obj_config['vy'],
                'size': obj_config['size']
            })
        
        self.frame += 1
    
    def check_collisions(self):
        """충돌 검사 (AABB) - 메테오 vs 별"""
        for obs in self.obstacles[:]:  # 복사본으로 순회 (리스트 수정 가능)
            obj_size = obs.get('size', OBSTACLE_SIZE)
            
            # AABB (Axis-Aligned Bounding Box) 충돌 감지
            if (self.player_x < obs['x'] + obj_size and
                self.player_x + PLAYER_SIZE > obs['x'] and
                self.player_y < obs['y'] + obj_size and
                self.player_y + PLAYER_SIZE > obs['y']):
                
                obj_type = obs.get('type', 'meteor')
                
                if obj_type == 'meteor':
                    # 메테오 충돌: 게임 오버
                    self.game_over = True
                    self.running = False
                    print(f"💥 메테오 충돌! 게임 오버! 점수: {self.score}, 생존 시간: {time.time() - self.start_time:.1f}초")
                    
                elif obj_type == 'star':
                    # 별 획득: 점수 증가
                    star_score = OBJECT_TYPES['star']['score']
                    self.score += star_score
                    self.obstacles.remove(obs)
                    self.star_collected = True  # 별 획득 플래그 설정
                    print(f"⭐ 별 획득! +{star_score}점 (총 {self.score}점)")
    
    def jump(self):
        """점프"""
        if self.player_y >= HEIGHT - PLAYER_SIZE - 5:
            self.player_vy = -18
        self.last_action = "jump"
    
    def move_left(self):
        """왼쪽 이동"""
        self.player_x = max(0, self.player_x - 10)
        self.last_action = "move_left"
    
    def move_right(self):
        """오른쪽 이동"""
        self.player_x = min(WIDTH - PLAYER_SIZE, self.player_x + 10)
        self.last_action = "move_right"
    
    def get_state(self):
        """현재 상태"""
        return {
            'player': {
                'x': self.player_x,
                'y': self.player_y,
                'vy': self.player_vy,
                'size': PLAYER_SIZE
            },
            'obstacles': self.obstacles,
            'score': self.score,
            'time': time.time() - self.start_time,
            'frame': self.frame,
            'mode': self.mode,
            'game_over': self.game_over,
            'star_collected': self.star_collected  # 별 획득 이벤트
        }

def encode_game_state(game):
    """
    게임 상태를 RL 모델 입력으로 인코딩
    
    상태 벡터 (10차원):
    - player_x_normalized (0~1)
    - player_y_normalized (0~1)
    - player_vy_normalized (-1~1)
    - nearest_meteor_dx_normalized (-1~1)
    - nearest_meteor_dy_normalized (0~1)
    - nearest_meteor_distance_normalized (0~1)
    - nearest_star_dx_normalized (-1~1)
    - nearest_star_dy_normalized (0~1)
    - nearest_star_distance_normalized (0~1)
    - on_ground (0 or 1)
    """
    player_x = game.player_x
    player_y = game.player_y
    player_vy = game.player_vy
    player_center_x = player_x + PLAYER_SIZE / 2
    
    # 정규화
    state = np.zeros(10, dtype=np.float32)
    state[0] = player_x / WIDTH
    state[1] = player_y / HEIGHT
    state[2] = np.clip(player_vy / 20.0, -1, 1)
    state[9] = 1.0 if player_y >= HEIGHT - PLAYER_SIZE - 5 else 0.0
    
    # 가장 가까운 메테오 & 별 찾기
    nearest_meteor_dist = 1.0
    nearest_star_dist = 1.0
    
    for obs in game.obstacles:
        obj_type = obs.get('type', 'meteor')
        obs_center_x = obs['x'] + obs.get('size', OBSTACLE_SIZE) / 2
        obs_center_y = obs['y'] + obs.get('size', OBSTACLE_SIZE) / 2
        
        dx = (obs_center_x - player_center_x) / WIDTH
        dy = (obs_center_y - player_y) / HEIGHT
        dist = np.sqrt(dx**2 + dy**2)
        
        if obj_type == 'meteor' and dist < nearest_meteor_dist:
            nearest_meteor_dist = dist
            state[3] = np.clip(dx, -1, 1)
            state[4] = np.clip(dy, 0, 1)
            state[5] = dist
        
        elif obj_type == 'star' and dist < nearest_star_dist:
            nearest_star_dist = dist
            state[6] = np.clip(dx, -1, 1)
            state[7] = np.clip(dy, 0, 1)
            state[8] = dist
    
    return state

def ai_decision(game):
    """
    AI 에이전트의 의사결정 로직
    
    우선순위:
    1. RL 모델 사용 (학습된 모델이 있으면)
    2. 휴리스틱 정책 (기본 전략)
    
    전략:
    1. 가장 가까운 메테오 회피
    2. 가까운 별 수집
    3. 안전 구역 유지
    """
    # RL 모델이 있으면 사용
    if RL_MODEL_AVAILABLE and RL_MODEL is not None:
        try:
            state = encode_game_state(game)
            # import torch
            # with torch.no_grad():
            #     state_tensor = torch.FloatTensor(state).unsqueeze(0)
            #     action_probs = RL_MODEL(state_tensor)
            #     action_idx = torch.argmax(action_probs).item()
            #     actions = ['stay', 'left', 'right', 'jump']
            #     return actions[action_idx] if action_idx > 0 else None
            pass
        except Exception as e:
            print(f"⚠️ RL 모델 추론 오류: {e}")
    
    # 휴리스틱 정책 (기본)
    player_x = game.player_x
    player_y = game.player_y
    player_center_x = player_x + PLAYER_SIZE / 2
    
    # 위협 분석
    nearest_meteor = None
    nearest_meteor_dist = float('inf')
    nearest_star = None
    nearest_star_dist = float('inf')
    
    for obs in game.obstacles:
        obj_type = obs.get('type', 'meteor')
        obs_x = obs['x']
        obs_y = obs['y']
        obs_size = obs.get('size', OBSTACLE_SIZE)
        obs_center_x = obs_x + obs_size / 2
        
        # 충돌 예상 범위 (플레이어와 x축 중첩)
        x_overlap = abs(player_center_x - obs_center_x) < (PLAYER_SIZE + obs_size) / 2 + 50
        
        if obj_type == 'meteor':
            # 메테오가 플레이어 위쪽에 있고 접근 중
            if obs_y < player_y and x_overlap:
                dist = abs(player_center_x - obs_center_x) + (player_y - obs_y) * 0.5
                if dist < nearest_meteor_dist:
                    nearest_meteor_dist = dist
                    nearest_meteor = obs
        
        elif obj_type == 'star':
            # 별이 획득 가능한 범위
            if obs_y < player_y + 200:
                dist = abs(player_center_x - obs_center_x) + abs(player_y - obs_y) * 0.3
                if dist < nearest_star_dist:
                    nearest_star_dist = dist
                    nearest_star = obs
    
    # 의사결정 우선순위
    action = None
    
    # 1. 위급 상황: 메테오 회피
    if nearest_meteor and nearest_meteor_dist < 150:
        meteor_center_x = nearest_meteor['x'] + nearest_meteor.get('size', OBSTACLE_SIZE) / 2
        
        # 메테오가 왼쪽에서 오면 오른쪽으로, 오른쪽에서 오면 왼쪽으로
        if meteor_center_x < player_center_x:
            if player_x + PLAYER_SIZE < WIDTH - 20:
                action = 'right'
        else:
            if player_x > 20:
                action = 'left'
        
        # 긴급 상황: 점프로 회피 시도
        if nearest_meteor_dist < 80 and player_y >= HEIGHT - PLAYER_SIZE - 10:
            action = 'jump'
    
    # 2. 기회 포착: 별 수집
    elif nearest_star and nearest_star_dist < 200:
        star_center_x = nearest_star['x'] + nearest_star.get('size', 30) / 2
        
        # 별 쪽으로 이동
        if star_center_x < player_center_x - 15:
            if player_x > 10:
                action = 'left'
        elif star_center_x > player_center_x + 15:
            if player_x + PLAYER_SIZE < WIDTH - 10:
                action = 'right'
        
        # 별이 위쪽에 있으면 점프
        if nearest_star['y'] < player_y - 50 and player_y >= HEIGHT - PLAYER_SIZE - 10:
            action = 'jump'
    
    # 3. 기본 행동: 중앙 유지 (좌우 이동 범위 확보)
    else:
        center_x = WIDTH / 2
        if player_center_x < center_x - 100:
            if player_x + PLAYER_SIZE < WIDTH - 20:
                action = 'right'
        elif player_center_x > center_x + 100:
            if player_x > 20:
                action = 'left'
    
    return action

def game_loop(sid):
    """게임 루프"""
    game = games.get(sid)
    if not game:
        return
    
    print(f"🎮 게임 루프 시작: {sid} (모드: {game.mode})")
    
    while game.running and not game.game_over:
        try:
            # AI 모드: 자동 의사결정
            if game.mode == 'ai':
                action = ai_decision(game)
                if action == 'jump':
                    game.jump()
                elif action == 'left':
                    game.move_left()
                elif action == 'right':
                    game.move_right()
            
            game.update()
            
            # 상태 전송
            socketio.emit('game_update', {
                'state': game.get_state()
            })
            
            time.sleep(1.0 / 30)  # 30 FPS
            
        except Exception as e:
            print(f"❌ 에러: {e}")
            break
    
    # 게임 오버 처리
    if game.game_over:
        survival_time = time.time() - game.start_time
        
        # 게임 세션 저장 (팀원들의 훈련 데이터용)
        save_gameplay_session(game)
        
        # 리더보드에 점수 추가
        player_name = game.player_name or f"Player-{sid[:6]}"
        leaderboard = add_score(player_name, game.score, survival_time, game.mode, sid)
        
        # 클라이언트에 게임 오버 + 랭킹 전송
        socketio.emit('game_over', {
            'score': game.score,
            'time': survival_time,
            'frame': game.frame,
            'player_name': player_name,
            'mode': game.mode,  # 모드 추가
            'leaderboard': leaderboard['scores'][:10]  # 상위 10개만
        })
        
        print(f"💾 점수 저장: {player_name} ({game.mode}) - {game.score}점 ({survival_time:.1f}초)")
    
    print(f"🛑 게임 루프 종료: {sid}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/leaderboard')
def api_leaderboard():
    """리더보드 API"""
    leaderboard = load_leaderboard()
    return jsonify(leaderboard)

@app.route('/api/leaderboard/top/<int:limit>')
def api_leaderboard_top(limit):
    """상위 N개 점수"""
    leaderboard = load_leaderboard()
    return jsonify({
        'scores': leaderboard['scores'][:limit]
    })

@app.route('/api/stats')
def api_stats():
    """통계 정보"""
    leaderboard = load_leaderboard()
    scores = leaderboard['scores']
    
    if not scores:
        return jsonify({
            'total_games': 0,
            'avg_score': 0,
            'highest_score': 0,
            'total_playtime': 0
        })
    
    return jsonify({
        'total_games': len(scores),
        'avg_score': round(sum(s['score'] for s in scores) / len(scores), 2),
        'highest_score': scores[0]['score'] if scores else 0,
        'total_playtime': round(sum(s['time'] for s in scores), 2),
        'human_games': len([s for s in scores if s['mode'] == 'human']),
        'ai_games': len([s for s in scores if s['mode'] == 'ai'])
    })

@socketio.on('connect')
def on_connect():
    from flask import request
    sid = request.sid
    games[sid] = Game(sid)
    print(f"✅ 연결: {sid}")
    emit('connected', {'config': {'width': WIDTH, 'height': HEIGHT}})

@socketio.on('disconnect')
def on_disconnect():
    from flask import request
    sid = request.sid
    if sid in games:
        games[sid].running = False
        del games[sid]
    print(f"❌ 연결 해제: {sid}")

@socketio.on('start_game')
def on_start_game(data):
    from flask import request
    sid = request.sid
    game = games.get(sid)
    
    if not game:
        print(f"❌ 게임 없음: {sid}")
        return
    
    # 게임 재시작: 상태 초기화
    game.reset()
    game.mode = data.get('mode', 'human')
    game.player_name = data.get('player_name', None)  # 플레이어 이름 저장
    game.running = True
    
    # 플레이어 이름 설정 (AI면 자동 생성)
    if game.mode == 'ai':
        game.player_name = f"AI-Bot-{sid[:6]}"
    elif not game.player_name:
        game.player_name = f"Player-{sid[:6]}"
    
    print(f"🚀 게임 시작: {sid}, 모드: {game.mode}, 플레이어: {game.player_name}")
    
    # 게임 루프 시작
    thread = threading.Thread(target=game_loop, args=(sid,))
    thread.daemon = True
    thread.start()
    
    emit('game_started', {'state': game.get_state()})

@socketio.on('player_action')
def on_action(data):
    from flask import request
    sid = request.sid
    game = games.get(sid)
    
    if not game or not game.running:
        return
    
    action = data.get('action')
    
    if action == 'jump':
        game.jump()
    elif action == 'left':
        game.move_left()
    elif action == 'right':
        game.move_right()

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5002))
    debug = os.environ.get('DEBUG', 'True') == 'True'
    
    print("🎮 게임 서버 시작!")
    print(f"🌐 http://localhost:{port}")
    print(f"🤖 AI 모드: 휴리스틱 기반 (RL 모델 대기 중)")
    
    socketio.run(app, host='0.0.0.0', port=port, debug=debug, allow_unsafe_werkzeug=True)

