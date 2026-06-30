---
created: 2026-06-29
description: qclaude(Claude Code → 로컬 qwen-122b)가 정말 로컬 LLM으로 도는지 따라하며 검증하는 가이드 — 양성/음성 테스트 + 로그 증거
---

# qclaude가 로컬 LLM으로 도는지 확인하기 (따라하기)

`qclaude`가 **진짜 로컬 qwen-122b로 도는지**(= 몰래 클라우드 Claude로 새지 않는지)를 네 손으로 증명하는
문서. 각 단계에 **명령 / 예상 결과 / 📋 체크**가 있다. 배선 자체는
[`connect-claude-code-to-local-qwen122b.md`](connect-claude-code-to-local-qwen122b.md) 참고.

> **핵심 아이디어:** "응답이 온다"는 로컬 증거가 못 된다(클라우드여도 응답은 온다). 진짜 증거는
> **① 모든 요청이 로컬 프록시 로그에 찍힌다(양성)** + **② 로컬 스택을 끊으면 qclaude가 실패한다(음성)**.

검증 대상 경로:
```
qclaude ──anthropic──▶ claude-proxy :8082 ──chat──▶ LiteLLM :4000 (qwen-122b-claude)
        ──▶ role-shim :8011 ──▶ mlx :8001 (qwen-122b)
```

---

## 0. 30초 빠른 확인 (한 줄)

```bash
qclaude -p "Reply with exactly: LOCAL_OK"; echo "---"; tail -2 /Users/ohama/agent-stack/claude-code-proxy/proxy.log
```
**예상:** 응답 `LOCAL_OK` + 바로 아래 proxy.log에 방금 `POST /v1/messages`(200)가 찍힘.
→ 둘 다 보이면 사실상 끝. 자세한 증명은 아래.

📋 체크: 응답 `____` / 로그에 POST 찍힘? `____`

---

## 1. 인프라 체인 헬스 (4단 + launchd)

```bash
for p in 8082 4000 8011 8001; do
  curl -s -o/dev/null -w "port $p -> %{http_code}\n" \
    "http://localhost:$p/$([ $p = 8082 ] && echo health || echo v1/models)" \
    -H "Authorization: Bearer dummy"
done
launchctl list | grep -E "claude-proxy|litellm|role-shim|qwen122b" | awk '{print "  PID",$1,$3}'
```
**예상 결과:**
```
port 8082 -> 200      # claude-proxy
port 4000 -> 200      # litellm
port 8011 -> 200      # role-shim
port 8001 -> 200      # mlx
  PID <n> com.ohama.qwen122b
  PID <n> com.ohama.litellm
  PID <n> com.ohama.claude-proxy
  PID <n> com.ohama.role-shim
```
하나라도 200이 아니거나 PID가 없으면 → 9장 문제해결.

📋 체크: 4포트 모두 200? `____` / launchd 4개 다 있음? `____`

---

## 2. alias가 로드됐나

```bash
alias qclaude
zsh -ic 'qclaude --version'    # 진짜 바이너리로 가는지(tmux 래퍼로 안 새는지) 확인
```
**예상:**
```
qclaude='ANTHROPIC_BASE_URL=http://localhost:8082 ANTHROPIC_AUTH_TOKEN=dummy /opt/homebrew/bin/claude'
2.1.195 (Claude Code)
```

> ⚠️ **풀패스가 중요하다.** alias가 `... dummy claude`(풀패스 없이)면, `which claude`가 `myclaude`(tmux
> 래퍼) alias인 환경에서 zsh가 `claude`를 재확장해 엉뚱하게 샌다. 그 증상은 `qclaude --version`에
> `open terminal failed: not a terminal`. 반드시 `/opt/homebrew/bin/claude` 풀패스를 써야 한다.

📋 체크: alias가 풀패스? `____` / `--version`이 2.1.195로 뜸(tmux 안 샘)? `____`

---

## 3. 1턴 대화

```bash
qclaude -p "What is 17 * 23? Answer with only the number."
```
**예상:** `391` (느리게, 수 초~수십 초 — 로컬 추론이라 클라우드보다 느린 게 정상).

> ⚠️ 무해한 경고 `claude.ai connectors are disabled ...`는 `ANTHROPIC_AUTH_TOKEN`을 줘서 뜨는 정상 메시지.

📋 체크: 정답 나옴? `____`

---

## 4. ★ 진짜 로컬로 갔다는 증명 (핵심)

### 4a. 양성 — 프록시 로그에 요청이 찍힌다

터미널 둘로 나눠서 한쪽에 로그를 띄워 두고 보면 확실하다.

```bash
# 터미널 A: 실시간 로그
tail -f /Users/ohama/agent-stack/claude-code-proxy/proxy.log
# 터미널 B: 요청
qclaude -p "Reply with exactly: PROOF"
```
**예상(터미널 A에 새로 찍힘):**
```
[hh:mm:ss] 200 -   <시간> POST /v1/messages
[hh:mm:ss] [REQ] http://localhost:4000/v1 model=qwen-122b-claude in=<n> out=<n> tok/s=<n>
```
- `POST /v1/messages` = Claude Code가 **로컬 프록시로** 보냈다는 증거.
- `model=qwen-122b-claude` = 백엔드가 **로컬 LiteLLM의 qwen** 이라는 증거.
- 클라우드로 갔다면 **여기에 아무것도 안 찍힌다.**

📋 체크: 요청할 때마다 위 두 줄이 새로 찍힘? `____`

### 4b. 음성 — 로컬을 끊으면 qclaude가 실패해야 한다 (클라우드로 안 샘)

**(i) 빠른 음성 테스트 — 잘못된 포트로 쏘기(서비스 안 건드림):**
```bash
ANTHROPIC_BASE_URL=http://localhost:9999 ANTHROPIC_AUTH_TOKEN=dummy claude -p "hi"
```
**예상:** 연결 실패/에러(`Connection refused` 류). → qclaude가 **프록시에 의존**하며 클라우드로 조용히
폴백하지 **않는다**는 증거.

**(ii) 진짜 스택 내리고 확인(선택, 확실하지만 서비스 잠깐 중단):**
```bash
launchctl bootout gui/$(id -u)/com.ohama.claude-proxy      # 프록시 완전 정지(KeepAlive 무력화)
qclaude -p "hi"                                            # → 실패해야 정상(로컬이 죽었으니)
# 복구:
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.ohama.claude-proxy.plist
curl -s -o/dev/null -w "복구 %{http_code}\n" http://localhost:8082/health   # 200
```
> 단순 `kill`은 KeepAlive가 즉시 되살리므로 음성 테스트엔 `bootout`을 써야 한다.

📋 체크: 잘못된 포트 → 에러? `____` / (선택) bootout 후 실패 & 복구 후 200? `____`

### 4c. ⚠️ 모델에게 "너 누구냐" 묻는 건 증거가 아니다

`qclaude -p "Are you Claude or Qwen?"` 같은 질문은 **신뢰하지 마라.** 로컬 모델이 시스템 프롬프트 영향으로
"나는 Claude"라고 답할 수 있다(환각). 신원은 **로그(4a)와 음성 테스트(4b)** 로만 판단한다.

### 4d. 속도 특성 (보조 신호)

```bash
time qclaude -p "Reply with exactly: ok"
```
**예상:** 수 초~수십 초 (클라우드 Claude보다 확연히 느림). proxy.log의 `tok/s` 값으로 로컬 처리량 확인 가능.
빠르고 즉답이면 오히려 로컬이 아닐 수 있으니 4a 로그를 재확인.

📋 체크: 체감 지연 있음(로컬다움)? `____`

---

## 5. 툴콜 end-to-end (에이전트로 진짜 작동하나)

```bash
rm -rf /tmp/qc-verify && mkdir -p /tmp/qc-verify && cd /tmp/qc-verify
qclaude -p "Create hello.py that prints 'hi from local qwen', then show me the file." --permission-mode acceptEdits
ls -la; cat hello.py 2>/dev/null
```
**예상:** `hello.py` 생성됨(Write 툴 동작) + 내용 출력. 동시에 proxy.log에 여러 `POST /v1/messages`가 찍힘.

> `--permission-mode acceptEdits`는 파일편집만 자동승인(=bash 실행은 별도 승인). 완전 자율은
> `--permission-mode bypassPermissions`(주의).

📋 체크: 파일 생성됨? `____` / 로그에 멀티 요청? `____`

---

## 6. 클라우드 claude와 분리됐는지

```bash
type qclaude    # alias (로컬)
type claude     # 원래 바이너리/네 tmux 래퍼 (클라우드)
```
**예상:** `qclaude`는 위 alias, `claude`는 그대로(클라우드 로그인 계정). 즉 **둘이 독립** — `qclaude`는
로컬, `claude`는 클라우드. (`claude`는 `ANTHROPIC_BASE_URL`을 안 거니 평소대로 동작.)

📋 체크: 둘이 분리돼 있음? `____`

---

## 7. 한 방 스모크 스크립트 (복붙용)

```bash
echo "== chain =="; for p in 8082 4000 8011 8001; do
  curl -s -o/dev/null -w "  $p -> %{http_code}\n" \
    "http://localhost:$p/$([ $p = 8082 ] && echo health || echo v1/models)" -H "Authorization: Bearer dummy"; done
echo "== launchd =="; launchctl list | grep -c claude-proxy | xargs echo "  claude-proxy entries:"
echo "== before =="; before=$(wc -l < /Users/ohama/agent-stack/claude-code-proxy/proxy.log)
echo "== ask =="; qclaude -p "Reply with exactly: SMOKE_OK"
echo "== proxy log delta (이만큼 새 요청이 로컬로 감) =="
after=$(wc -l < /Users/ohama/agent-stack/claude-code-proxy/proxy.log); echo "  +$((after-before)) lines"
tail -3 /Users/ohama/agent-stack/claude-code-proxy/proxy.log
```
**판정:** 응답 `SMOKE_OK` + proxy.log가 늘어났으면(POST /v1/messages 포함) **로컬 동작 확정.**

📋 체크: SMOKE_OK & 로그 증가? `____`

---

## 8. 빠른 판정표

| 관찰 | 의미 |
|------|------|
| 응답 옴 + proxy.log에 `POST /v1/messages` 찍힘 | ✅ 로컬로 감 (확정) |
| 응답은 오는데 proxy.log에 안 찍힘 | ⚠️ 클라우드로 새는 중 — `alias qclaude` / `ANTHROPIC_BASE_URL` 확인 |
| 잘못된 포트(:9999)로도 응답이 옴 | ⚠️ 어딘가 클라우드 폴백 — env 점검 |
| `[REQ] ... model=qwen-122b-claude` | ✅ role-shim 경유 로컬 백엔드 |
| 매우 빠른 즉답 | 🔍 로컬 아닐 수 있음 → 4a 로그 재확인 |

---

## 9. 문제해결

| 증상 | 원인 / 조치 |
|------|-------------|
| `qclaude: command not found` | alias 미로드 → `source ~/.zshrc` 또는 새 터미널 |
| `Connection refused` (:8082) | 프록시 죽음 → `launchctl kickstart -k gui/$(id -u)/com.ohama.claude-proxy` |
| `System message must be at the beginning.` | 프록시가 role-shim 경유 모델(`qwen-122b-claude`)을 안 씀 → `~/.claude/proxy.env`의 `ANTHROPIC_DEFAULT_*_MODEL` 확인 |
| `OpenAIException - Not Found` (responses) | `ANTHROPIC_BASE_URL`이 LiteLLM(:4000)을 직접 가리킴 → 반드시 프록시(:8082)를 가리켜야 함 |
| 포트 8082는 사는데 응답 없음/타임아웃 | 하위 체인 확인: role-shim :8011, mlx :8001 헬스 (1장) |
| 로그가 안 쌓임 | 서비스 로그 경로: `/Users/ohama/agent-stack/claude-code-proxy/proxy.log` / `proxy.err.log` |

---

## 관련 문서 / 운영 명령

- 배선: [`connect-claude-code-to-local-qwen122b.md`](connect-claude-code-to-local-qwen122b.md)
- 운영:
  ```bash
  launchctl list | grep claude-proxy                              # 상태/PID
  launchctl kickstart -k gui/$(id -u)/com.ohama.claude-proxy      # 재시작
  tail -f /Users/ohama/agent-stack/claude-code-proxy/proxy.log    # 요청 로그
  ```
- 메모리: `claude-code-qwen122b-wiring.md`
