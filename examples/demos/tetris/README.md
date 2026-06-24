# 테트리스 데모 (Codex × 로컬 qwen-122b 생성)

유튜브 영상("Codex 무료 사용법")에서 Codex로 테트리스를 만드는 장면을, 우리 환경의
**로컬 qwen-122b**로 직접 재현한 결과물.

- `index.html` — **단일 파일** 테트리스 (HTML + CSS + vanilla JS, 외부 라이브러리 0)
- 약 502줄 / 16KB, JS 문법 검증 통과(`node --check`)

## 실행 방법

브라우저로 `index.html`을 열면 끝.
```bash
open index.html        # macOS
```

## 조작

| 키 | 동작 |
|----|------|
| ← / → | 좌우 이동 |
| ↑ | 회전 |
| ↓ | 소프트 드롭 |
| Space | 하드 드롭 |
| P | 일시정지 |

## 기능

- 캔버스 보드(300×600) + 다음 블록 프리뷰(100×100)
- 7가지 표준 테트로미노(I·O·T·S·Z·J·L), 각기 다른 색
- 줄 삭제 점수(1/2/3/4줄 = 100/300/500/800), 레벨업(10줄마다 속도 증가)
- 점수·레벨 표시, 게임오버 화면 + 재시작

## 어떻게 만들었나

명령 한 줄(비대화형):
```bash
codex exec --sandbox workspace-write \
  "Create one self-contained index.html: a playable Tetris game (HTML+CSS+vanilla JS,
   no libs): canvas board, 7 tetrominoes with colors, arrow keys, hard drop, line
   clearing+score, level, next-piece preview, pause, game-over+restart."
```

Codex가 로컬 qwen-122b와 **3번 메시지를 주고받아**(작성 → grep 검증 → 요약) 완성했다.
그 전체 왕복 기록은 → **[SESSION.md](SESSION.md)**.

> 참고: 이 작업은 122B로 단일 HTML을 한 번에 생성하느라 무겁다(실제 생성 ~10분대).
> 빠르게 만들려면 더 작은 모델(qwen-35b)을 Codex용으로 라우팅하는 편이 낫다.
