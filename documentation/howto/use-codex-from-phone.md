---
created: 2026-06-24
description: 로컬 qwen-122b에 연결된 Codex를 휴대폰에서 쓰는 법 — Tailscale + SSH + tmux 원격 터미널 방식
---

# 휴대폰에서 Codex 사용하기

로컬 qwen-122b에 연결된 Codex를 외출 중에 휴대폰으로 구동하는 법. 핵심은
**"폰은 Mac에 접속하는 원격 터미널일 뿐"**이라는 것.

## The Insight

65GB짜리 모델과 Codex CLI는 **Mac에서** 돌아간다. 휴대폰은 그걸 로컬에서 실행할 수 없다.
따라서 폰은 화면·키보드 역할만 하고, 실제 작업은 SSH 너머 Mac에서 일어난다.

```
폰(Tailscale + SSH 앱) ──SSH──▶ Mac ──▶ tmux ──▶ codex ──▶ LiteLLM:4000 → role-shim:8011 → mlx:8001
```

OpenAI의 "Codex 모바일 앱"은 클라우드 GPT를 쓰는 **별개 제품**이다. 로컬 qwen-122b를 폰에서
쓰려면 아래 SSH 방식이 맞다.

## Why This Matters

- 모델을 폰에 옮길 수 없으니(용량·연산), 원격 접속이 유일한 현실적 방법.
- 집 wifi 밖(LTE)에서도 닿으려면 단순 LAN IP가 아니라 **Tailscale**(또는 VPN)이 필요하다.
- SSH는 끊기기 쉬우므로 **tmux**로 세션을 Mac에 살려둬야 작업이 날아가지 않는다.

## Recognition Pattern

"집/사무실 Mac에서 돌리는 로컬 LLM 에이전트를 이동 중에 쓰고 싶다" → 이 패턴.
웹소켓/SSE 노출이 아니라 **터미널 원격화**가 정답.

## The Approach

세 조각을 끼운다: ① 네트워크 도달(Tailscale) ② 원격 셸(SSH) ③ 세션 영속(tmux).

### Step 1: 폰에 Tailscale 설치

App Store / Play Store에서 **Tailscale** 설치 → Mac과 **같은 계정**으로 로그인.
폰이 tailnet에 들어오면 외부망에서도 Mac에 직접 닿는다.

> 이 Mac은 tailnet 이름 `ohama-2`, Tailscale IP `100.118.140.2`
> (DNS `ohama-2.tail318f12.ts.net`). 같은 계정의 iOS 기기는 이미 tailnet에 등록돼 있다.

### Step 2: 폰에 SSH 터미널 앱 설치

| OS | 추천 앱 |
|----|---------|
| iOS | **Termius**(가장 쉬움), Blink Shell, a-Shell |
| Android | **Termius**, Termux |

### Step 3: SSH 접속

```bash
ssh ohama@100.118.140.2
# 또는 이름으로
ssh ohama@ohama-2.tail318f12.ts.net
```

### Step 4: tmux 안에서 Codex 실행 (끊겨도 유지)

```bash
tmux new -A -s codex      # 'codex' 세션 진입/재진입 (없으면 생성)
cd ~/내프로젝트
codex                      # 또는: codex exec "..."
```

폰 화면이 꺼지거나 SSH가 끊겨도 작업은 Mac에서 계속 돌아간다. 다시 접속해
`tmux new -A -s codex`를 치면 진행 중이던 화면이 그대로 복원된다.

**tmux 최소 조작 (터치 키보드 기준):**
- 분리(작업 유지한 채 나가기): `Ctrl-b` 그다음 `d`
- 스크롤 모드: `Ctrl-b` 그다음 `[` (방향키로 스크롤, `q`로 종료)

## (선택) Tailscale SSH — 키 설정 없이 접속

SSH 키를 폰에 등록하기 번거로우면, tailnet 신원으로 인증하게 한다. Mac에서 한 번:

```bash
sudo tailscale up --ssh
```

이후 폰 Termius에서 호스트 `ohama-2`, 사용자 `ohama`로 바로 접속(비번·키 불필요).

## 주의: Mac이 잠들면 다 끊긴다

폰에서 쓰는 동안 Mac이 sleep 되면 모델·SSH가 모두 끊긴다. 장시간 작업 시:

```bash
caffeinate -s     # 이 명령이 떠 있는 동안 Mac이 잠들지 않음
```

또는 시스템 설정 > 배터리/전원에서 "디스플레이가 꺼져도 자동으로 잠자기 방지" 활성화.

## Example — 외출 중 버그 수정 흐름

```bash
# 폰 Termius에서
ssh ohama@ohama-2.tail318f12.ts.net
tmux new -A -s codex
cd ~/projs/myapp
codex exec --sandbox workspace-write \
  "fix the failing test in test_api.py and run the tests"
# 결과 확인 후 Ctrl-b d 로 분리, 앱 닫아도 됨
```

## 트러블슈팅

| 증상 | 원인 / 조치 |
|------|-------------|
| SSH 타임아웃 | 폰 Tailscale ON 확인 / `tailscale status`에 폰·Mac 둘 다 보이는지 |
| 접속은 되는데 codex 응답 없음 | Mac이 sleep → `caffeinate -s` / 서비스 포트(:4000/:8011/:8001) UP 확인 |
| 재접속하니 화면 사라짐 | tmux를 안 썼을 때. 항상 `tmux new -A -s codex` 안에서 실행 |
| `ohama-2`로 접속 안 됨 | IP로 시도(`100.118.140.2`) / Tailscale MagicDNS 켜짐 확인 |

## 체크리스트

- [ ] 폰에 Tailscale 설치 + Mac과 같은 계정 로그인
- [ ] 폰에 SSH 앱(Termius 등) 설치
- [ ] `ssh ohama@100.118.140.2` 접속 성공
- [ ] `tmux new -A -s codex` 안에서 codex 실행
- [ ] 장시간이면 Mac `caffeinate -s` 또는 잠자기 방지
- [ ] (선택) `sudo tailscale up --ssh`로 키 없는 접속

## 관련 문서

- `use-codex-cli.md` — Codex CLI 일상 사용법 (실행 모드·권한·운영)
- `connect-codex-to-local-qwen122b.md` — 로컬 배선 구축 과정
