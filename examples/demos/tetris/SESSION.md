# 테트리스 생성 세션 — Codex ↔ 로컬 qwen-122b 전체 왕복

이 데모의 `index.html`이 만들어지는 동안, **Codex와 로컬 qwen-122b가 실제로 주고받은 메시지**
전체를 사람이 읽기 좋게 정리한 기록이다. 원본은 Codex가 자동으로 남기는 세션 rollout:

```
~/.codex/sessions/2026/06/24/rollout-2026-06-24T13-48-36-019ef7f5-…71546.jsonl
```

- 세션 id: `019ef7f5-6b66-7e81-90dd-7cf7d9d71546`
- 모델: `qwen-122b-codex` (Codex → LiteLLM:4000 → role-shim:8011 → mlx_lm.server:8001)
- 샌드박스: `workspace-write` · 승인: `never`
- **모델 왕복 횟수: 3회** · 총 토큰: 46,751

> "왕복 1회" = Codex가 모델에 요청 → 모델 응답(텍스트 + 실행할 셸 명령) → Codex가 로컬에서
> 실행 → 그 결과를 다음 요청에 첨부. 이 과정이 3번 반복돼 작업이 끝났다.

---

## 0. 시스템이 모델에게 먼저 주는 컨텍스트 (요청에 항상 포함)

**[developer]** 권한/샌드박스 지시
> `sandbox_mode = workspace-write`: 작업 디렉터리 안에서만 쓰기 허용 … (파일시스템 권한 규칙)

**[user] `<environment_context>`**
> cwd = `…/examples/demos/tetris`, shell = zsh, date = 2026-06-24 …

---

## 1. 사용자 지시 (입력)

**[user]**
> Create one self-contained file named index.html: a playable Tetris game using only HTML,
> CSS, and vanilla JavaScript (no external libraries) … canvas board, 7 tetrominoes with
> colors, arrow keys, hard drop, line clearing+score, level, next-piece preview, pause,
> game-over+restart … After writing the file, run 'grep -c canvas index.html' to confirm.

---

## 2. 왕복 ① — 모델이 게임 전체를 작성

**[assistant]**
> I'll create a self-contained Tetris game in a single HTML file with all the requested features.

**[tool_call] 셸 실행** (모델이 내린 명령)
```bash
cat > index.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head> … (HTML + CSS + 약 11,800자의 vanilla JS: 보드/블록/회전/낙하/줄삭제/점수/프리뷰) …
EOF
```

**[tool_output]** Codex가 로컬에서 실행
```
exited 0   (파일 작성 성공)
```

---

## 3. 왕복 ② — 모델이 결과를 스스로 검증

**[assistant]**
> Now let me verify the file was created and count the canvas elements:

**[tool_call] 셸 실행**
```bash
grep -c canvas index.html
```

**[tool_output]**
```
7
```

---

## 4. 왕복 ③ — 모델이 최종 요약

**[assistant]**
> The `index.html` file has been created with 7 canvas references (2 actual `<canvas>`
> elements plus 5 in comments/strings). The game includes:
> - Canvas board (300×600) + next-piece preview (100×100)
> - 7 tetrominoes (I,O,T,S,Z,J,L) with distinct colors
> - Arrow keys, Space hard drop, line clearing & scoring (100/300/500/800), level system,
>   pause (P), game-over + restart
> - 단일 index.html, 외부 의존성 없음.

**`-- task_complete --`**

---

## 흐름 요약

```
[입력] "테트리스 index.html 만들어"
   │
   ├─ 왕복① 모델: cat > index.html (게임 전체 작성)  → Codex 실행: exit 0
   ├─ 왕복② 모델: grep -c canvas (자가 검증)          → Codex 실행: "7"
   └─ 왕복③ 모델: 최종 요약                           → task_complete
```

이렇게 멀티스텝 작업은 모델이 **작성 → 검증 → 보고**로 여러 번 메시지를 주고받으며,
그 전부가 `~/.codex/sessions/…rollout-*.jsonl`에 자동 기록된다. (직접 보려면:
`cat <rollout.jsonl> | jq -r 'select(.type=="response_item").payload | .role // .type'`)
