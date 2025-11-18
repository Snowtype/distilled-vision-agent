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

app = Flask(__name__)
app.config['SECRET_KEY'] = 'game-secret'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# 게임 설정
WIDTH = 960
HEIGHT = 720
PLAYER_SIZE = 50
OBSTACLE_SIZE = 50

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
        self.start_time = time.time()
        self.frame = 0
        self.game_over = False
        
        # 훈련 데이터 수집
        self.collected_states = []  # State-Action-Reward 로그
        self.last_action = "stay"
        
    def update(self):
        """물리 업데이트"""
        if self.game_over:
            return
        
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
        
        # 장애물 이동
        for obs in self.obstacles:
            obs['y'] += 5
        
        # 화면 밖 장애물 제거 + 점수 증가
        before_count = len(self.obstacles)
        self.obstacles = [o for o in self.obstacles if o['y'] < HEIGHT]
        cleared = before_count - len(self.obstacles)
        self.score += cleared
        
        # 충돌 검사
        self.check_collisions()
        
        # 📊 보상 계산
        reward = 1.0  # 생존
        if cleared > 0:
            reward += cleared * 10  # 장애물 회피 보너스
        if self.game_over:
            reward = -100  # 충돌 페널티
        
        # 📊 State-Action-Reward 저장 (클로 훈련용)
        self.collected_states.append({
            'frame': self.frame,
            'state': current_state,
            'action': self.last_action,
            'reward': reward,
            'done': self.game_over
        })
        
        # 새 장애물 생성 (5% 확률)
        if random.random() < 0.05:
            self.obstacles.append({
                'x': random.randint(0, WIDTH - OBSTACLE_SIZE),
                'y': -OBSTACLE_SIZE,
                'size': OBSTACLE_SIZE
            })
        
        self.frame += 1
    
    def check_collisions(self):
        """충돌 검사 (AABB)"""
        for obs in self.obstacles:
            # AABB (Axis-Aligned Bounding Box) 충돌 감지
            if (self.player_x < obs['x'] + obs['size'] and
                self.player_x + PLAYER_SIZE > obs['x'] and
                self.player_y < obs['y'] + obs['size'] and
                self.player_y + PLAYER_SIZE > obs['y']):
                # 충돌!
                self.game_over = True
                self.running = False
                print(f"💥 게임 오버! 점수: {self.score}, 생존 시간: {time.time() - self.start_time:.1f}초")
    
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
            'game_over': self.game_over
        }

def game_loop(sid):
    """게임 루프"""
    game = games.get(sid)
    if not game:
        return
    
    print(f"🎮 게임 루프 시작: {sid}")
    
    while game.running and not game.game_over:
        try:
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
        player_name = f"Player_{sid[:6]}"  # 임시 플레이어 이름
        leaderboard = add_score(player_name, game.score, survival_time, game.mode, sid)
        
        # 클라이언트에 게임 오버 + 랭킹 전송
        socketio.emit('game_over', {
            'score': game.score,
            'time': survival_time,
            'frame': game.frame,
            'player_name': player_name,
            'leaderboard': leaderboard['scores'][:10]  # 상위 10개만
        })
        
        print(f"💾 점수 저장: {player_name} - {game.score}점 ({survival_time:.1f}초)")
    
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
    game.running = True
    
    print(f"🚀 게임 시작: {sid}, 모드: {game.mode}")
    
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
    print("🎮 게임 서버 시작!")
    print("🌐 http://localhost:5002")
    socketio.run(app, host='0.0.0.0', port=5002, debug=True, allow_unsafe_werkzeug=True)

