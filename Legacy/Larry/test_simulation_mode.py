#!/usr/bin/env python3
"""
시뮬레이션 모드 테스트 스크립트

사용법:
    python3 test_simulation_mode.py
"""

import sys
import numpy as np
import time
from pathlib import Path

# 프로젝트 경로 추가
sys.path.insert(0, str(Path(__file__).parent))

from modules.cv_module import ComputerVisionModule

def test_simulation_mode():
    """시뮬레이션 모드 테스트"""
    print("=" * 60)
    print("🧪 시뮬레이션 모드 테스트")
    print("=" * 60)
    print()
    
    # 1. 시뮬레이션 모드로 CV 모듈 생성 (모델 경로 없음)
    print("1️⃣ CV 모듈 생성 (시뮬레이션 모드)")
    print("-" * 60)
    cv = ComputerVisionModule(model_path=None)
    print(f"   ✅ 모델 상태: {'로드됨' if cv.model is not None else '시뮬레이션 모드'}")
    print()
    
    # 2. 더미 프레임 생성
    print("2️⃣ 더미 프레임 생성")
    print("-" * 60)
    dummy_frame = np.zeros((720, 960, 3), dtype=np.uint8)
    print(f"   ✅ 프레임 크기: {dummy_frame.shape}")
    print()
    
    # 3. 게임 상태 생성
    print("3️⃣ 게임 상태 생성")
    print("-" * 60)
    game_state = {
        'player': {
            'x': 480,
            'y': 600,
            'size': 50
        },
        'lava': {
            'state': 'active',
            'zone_x': 320,
            'zone_width': 320,
            'height': 120
        },
        'obstacles': [
            {'x': 200, 'y': 100, 'size': 50, 'type': 'meteor'},
            {'x': 600, 'y': 200, 'size': 30, 'type': 'star'}
        ]
    }
    print(f"   ✅ 플레이어: ({game_state['player']['x']}, {game_state['player']['y']})")
    print(f"   ✅ 라바 상태: {game_state['lava']['state']}")
    print(f"   ✅ 장애물 수: {len(game_state['obstacles'])}")
    print()
    
    # 4. 객체 탐지 실행 (시뮬레이션 모드)
    print("4️⃣ 객체 탐지 실행 (시뮬레이션 모드)")
    print("-" * 60)
    
    # 여러 번 실행해서 성능 측정
    num_tests = 10
    times = []
    
    for i in range(num_tests):
        start_time = time.perf_counter()
        detections = cv.detect_objects(dummy_frame, game_state)
        elapsed = (time.perf_counter() - start_time) * 1000
        times.append(elapsed)
    
    avg_time = np.mean(times)
    min_time = np.min(times)
    max_time = np.max(times)
    
    print(f"   ✅ 탐지 결과: {len(detections)}개 객체 발견")
    print(f"   ⏱️  평균 시간: {avg_time:.2f}ms")
    print(f"   ⏱️  최소 시간: {min_time:.2f}ms")
    print(f"   ⏱️  최대 시간: {max_time:.2f}ms")
    print(f"   📊 예상 FPS: {1000/avg_time:.1f}")
    print()
    
    # 5. 탐지 결과 상세 출력
    print("5️⃣ 탐지 결과 상세")
    print("-" * 60)
    for i, det in enumerate(detections, 1):
        print(f"   {i}. {det.class_name} (ID: {det.class_id})")
        print(f"      바운딩 박스: [{det.bbox[0]:.0f}, {det.bbox[1]:.0f}, {det.bbox[2]:.0f}, {det.bbox[3]:.0f}]")
        print(f"      신뢰도: {det.confidence:.2f}")
        print()
    
    # 6. 성능 통계
    print("6️⃣ 성능 통계")
    print("-" * 60)
    stats = cv.get_performance_stats()
    if stats:
        print(f"   평균 추론 시간: {stats.get('avg_inference_time_ms', 0):.2f}ms")
        print(f"   평균 FPS: {stats.get('avg_fps', 0):.1f}")
        print(f"   총 프레임: {stats.get('total_frames', 0)}")
        print(f"   목표 FPS 달성: {'✅' if stats.get('meets_target', False) else '❌'}")
    print()
    
    # 7. YOLO 모드와 비교 (선택적)
    print("7️⃣ YOLO 모드와 비교 (선택적)")
    print("-" * 60)
    project_root = Path(__file__).parent.parent
    yolo_path = project_root / 'AI_model' / 'best_112217.pt'
    
    if yolo_path.exists():
        print(f"   📁 YOLO 모델 발견: {yolo_path}")
        cv_yolo = ComputerVisionModule(model_path=str(yolo_path))
        
        if cv_yolo.model is not None:
            print(f"   ✅ YOLO 모델 로드 성공")
            
            # 게임 상태가 있으면 시뮬레이션 모드 사용
            start = time.perf_counter()
            results_yolo = cv_yolo.detect_objects(dummy_frame, game_state)
            time_yolo = (time.perf_counter() - start) * 1000
            
            print(f"   ⏱️  소요 시간: {time_yolo:.2f}ms")
            print(f"   📊 사용 모드: 시뮬레이션 (게임 상태 있음)")
            print(f"   📊 탐지 결과: {len(results_yolo)}개 객체")
        else:
            print(f"   ⚠️ YOLO 모델 로드 실패")
    else:
        print(f"   ⚠️ YOLO 모델 파일 없음: {yolo_path}")
    print()
    
    print("=" * 60)
    print("✅ 테스트 완료!")
    print("=" * 60)
    print()
    print("💡 시뮬레이션 모드는 게임 상태를 기반으로 객체 탐지 결과를 생성합니다.")
    print("   실제 YOLO 모델을 사용하지 않아 매우 빠릅니다!")
    print()

if __name__ == "__main__":
    test_simulation_mode()

