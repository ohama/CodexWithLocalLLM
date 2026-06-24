---
created: 2026-06-24
description: 로컬 qwen-122b에 연결된 Codex CLI 일상 사용법 — 실행 모드, 권한/샌드박스, 프로파일, 운영·트러블슈팅
---

# Codex CLI 사용법 (로컬 qwen-122b)

이미 배선이 끝난 Codex CLI를 매일 쓰는 법. 배선 자체(설치·shim·브릿지)는
`connect-codex-to-local-qwen122b.md` 참고. 이 문서는 **"이제 어떻게 쓰나"**에 집중한다.

전제: `~/.codex/config.toml`이 `qwen-122b-codex`(LiteLLM :4000)로 설정되어 있고,
`LITELLM_API_KEY=dummy`가 셸에 있다. 비용 0, 데이터 로컬.

---

## The Insight

Codex CLI는 두 가지 모드가 전부다.
- **대화형(`codex`)** — 사람이 보면서 단계마다 개입. 탐색·디버깅·반복 작업.
- **비대화형(`codex exec "..."`)** — 한 방에 시키고 결과만 받음. 스크립트·자동화·CI.

나머지는 전부 "에이전트에게 **얼마나 권한을 줄 것인가**"(샌드박스 + 승인 모드)의 조절이다.

---

## 빠른 시작

```bash
cd ~/my-project        # 작업할 디렉터리에서
codex                  # 대화형 시작 (모델: qwen-122b-codex 기본)
```

대화형 안에서 그냥 자연어로 지시:
```
> add a --json flag to wordstat.py that prints the stats as JSON
```

한 방에 시키려면:
```bash
codex exec "fix the failing test in test_wordstat.py and run it"
```

---

## 실행 모드

### 대화형 — `codex`
- 모델이 제안한 명령/패치를 **눈으로 보고 승인**하며 진행.
- 세션 중 추가 지시, 방향 전환 가능.
- 종료: `Ctrl-C` 또는 `/quit`.

### 비대화형 — `codex exec "프롬프트"`
- 끝까지 자율 실행 후 최종 요약만 출력. 파이프라인·반복에 적합.
- git 리포 밖에서 돌릴 땐 `--skip-git-repo-check` 필요.

```bash
codex exec --skip-git-repo-check "create hello.py that prints hi"
```

---

## 권한: 샌드박스 + 승인 모드

에이전트가 파일을 쓰고 명령을 실행하므로, **권한을 처음엔 좁게** 주고 신뢰가 쌓이면 넓힌다.

### 샌드박스 (`--sandbox`)
| 값 | 의미 | 쓰는 때 |
|----|------|---------|
| `read-only` | 읽기만. 파일 수정·명령 실행 불가 (기본) | 코드 설명·분석·리뷰 |
| `workspace-write` | 현재 작업트리 안에서 쓰기/실행 허용 | **일반 코딩** (대부분 이걸로) |
| `danger-full-access` | 시스템 전체 접근 | 거의 쓰지 말 것 |

```bash
codex exec --sandbox workspace-write "refactor utils.py into smaller functions"
```

### 승인 모드 (`--ask-for-approval`)
| 값 | 의미 |
|----|------|
| `untrusted` | 위험한 작업마다 승인 요청 (가장 안전) |
| `on-failure` | 실패했을 때만 사람에게 물음 |
| `on-request` | 모델이 필요하다고 판단할 때만 |
| `never` | 묻지 않고 끝까지 자율 (exec 자동화용) |

> 권장 출발점: 대화형 = `workspace-write` + `untrusted`(또는 on-failure).
> 자동화 = `workspace-write` + `never`. 절대 신뢰 못 할 입력엔 `read-only`.

조합 단축: `codex --full-auto` ≈ `workspace-write` + 자동 승인(빠른 반복용, 결과는 검토할 것).

---

## 모델 프로파일

`~/.codex/config.toml`의 프로파일로 모델/엔드포인트를 전환.

```bash
codex                    # 기본: qwen-122b-codex (품질)
codex --profile fast     # 보조 프로파일 (예: 35B, 속도) — 정의돼 있을 때
```

35B용 빠른 프로파일을 추가하려면, LiteLLM에 `qwen-35b-codex` 브릿지 항목을 만들고
config.toml에 프로파일을 추가하면 된다(`connect-...` 문서의 Step 4 패턴 동일).

---

## 자주 쓰는 패턴

```bash
# 코드 설명만 (안전, 읽기 전용)
codex exec --sandbox read-only "explain what server.py does"

# 버그 수정 + 검증까지 자율로
codex exec --sandbox workspace-write --ask-for-approval never \
  "find and fix the bug making test_auth.py fail, then run the tests"

# 새 기능 추가 (대화형으로 보면서)
codex
> add pagination to the /users endpoint and write a test for it

# 파이프 입력
echo "summarize the TODOs in this repo" | codex exec --skip-git-repo-check -
```

---

## 운영 / 트러블슈팅

배선이 launchd로 영구화되어 있다. 문제가 생기면 아래 순서로 점검.

### 서비스 상태 확인
```bash
for s in com.ohama.litellm com.ohama.role-shim com.ohama.qwen122b; do
  echo "$s -> pid $(launchctl list | awk -v s=$s '$3==s{print $1}')"
done
# 포트: :4000 게이트웨이, :8011 role-shim, :8001 mlx 모델서버
```

### 경로별 헬스체크
```bash
# 1) 게이트웨이가 모델을 노출하나
curl -s localhost:4000/v1/models -H "Authorization: Bearer dummy"

# 2) responses 브릿지가 도나
curl -s localhost:4000/v1/responses -H "Authorization: Bearer dummy" \
  -H "Content-Type: application/json" \
  -d '{"model":"qwen-122b-codex","input":"say OK"}'

# 3) shim이 developer role을 받나
curl -s localhost:8011/v1/chat/completions -H "Content-Type: application/json" \
  -d '{"model":"/Users/ohama/llm-system/models/qwen122b","messages":[{"role":"developer","content":"x"},{"role":"user","content":"hi"}],"max_tokens":5}'
```

### 재시작
```bash
# 게이트웨이만 (기존 클라이언트 ~3초 끊김, 모델 재로딩 없음)
launchctl kickstart -k gui/$(id -u)/com.ohama.litellm

# shim만
launchctl kickstart -k gui/$(id -u)/com.ohama.role-shim

# mlx 모델서버 (주의: 65GB 재로딩, 수십 초~분. 꼭 필요할 때만)
launchctl kickstart -k gui/$(id -u)/com.ohama.qwen122b
```

### 증상 → 원인
| 증상 | 원인 / 조치 |
|------|-------------|
| `wire_api = "chat" is no longer supported` | config.toml에 `wire_api = "responses"` 확인 |
| `Unexpected message role.` | role-shim이 죽었거나 api_base가 shim(:8011)이 아님 |
| `404 ... /responses` | LiteLLM 모델 id에 `openai/chat_completions/` prefix 누락 |
| `429 Too Many Requests` 반복 | 한 번 실패 후 라우터 cooldown — 백엔드/ shim 로그 확인 후 재시도 |
| `Model metadata for ... not found` (경고) | 무시해도 됨 (성능 영향 없음) |

### 로그 위치
- LiteLLM: `/Users/ohama/agent-stack/litellm/litellm.log`, `litellm.err.log`
- role-shim: `/Users/ohama/llm-system/services/logs/role-shim.log`

---

## 팁

- **작업 디렉터리에서 실행** — Codex는 현재 디렉터리를 작업트리로 본다. 프로젝트 루트에서 열 것.
- **권한은 점진적으로** — 처음 보는 작업은 `read-only`로 한 번 보고, 괜찮으면 `workspace-write`.
- **로컬이라 마음껏** — 토큰 비용이 없으니 큰 컨텍스트(256K)·반복 시도에 부담이 없다.
- **품질 vs 속도** — 복잡한 작업은 기본(122B), 간단·대량은 `--profile fast`(35B, 설정 시).
- **결과는 검토** — `never`/`--full-auto`로 돌린 자율 작업도 diff/테스트는 사람이 확인.

## 체크리스트

- [ ] 작업할 프로젝트 디렉터리에서 `codex` 실행
- [ ] 처음 작업은 `--sandbox read-only`로 탐색
- [ ] 코딩은 `--sandbox workspace-write`
- [ ] 자동화는 `--ask-for-approval never` + 결과 검토
- [ ] 문제 시 3경로 헬스체크(:4000 → :8011 → :8001) 순서로 점검

## 관련 문서

- `connect-codex-to-local-qwen122b.md` — 배선 구축 과정 (설치·shim·브릿지)
- 시스템 메모리 `codex-qwen122b-wiring.md` — 배선 요약 + 운영 명령
