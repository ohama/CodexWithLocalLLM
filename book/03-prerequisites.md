# 3. 사전 준비 — 백엔드 확인

두 도구 모두 **로컬 LiteLLM 게이트웨이(`:4000`)** 를 통해 같은 qwen-122b를 쓴다. 비교를 시작하기
전에 이 백엔드가 살아 있는지부터 확인한다.

## 환경변수 (게이트웨이 키)

LiteLLM은 아무 키나 받는다. 셸에 더미 키를 넣는다:

```sh
export LITELLM_API_KEY=dummy
```
- **효과:** codex/openhands/채점 스크립트가 게이트웨이에 붙을 때 쓰는 키. 값은 아무거나 OK.

## 게이트웨이가 떠 있나 (주 점검)

```sh
curl -sf localhost:4000/v1/models -H "Authorization: Bearer dummy" >/dev/null && echo "gateway OK" || echo "gateway DOWN"
```
- **효과:** `gateway OK` 면 백엔드 준비 완료 → 다음 장으로.
- `gateway DOWN` 이면 백엔드 스택을 먼저 띄워야 한다(아래).

## 백엔드 스택의 구성 (DOWN일 때)

이 시스템의 로컬 LLM 스택은 3개 층이다:

```
도구 ──▶ LiteLLM :4000 (게이트웨이) ──▶ role-shim :8011 ──▶ mlx_lm.server :8001 (qwen-122b)
```

각 층이 떠 있는지 확인:
```sh
lsof -ti tcp:4000 >/dev/null && echo ":4000 LiteLLM UP"   || echo ":4000 DOWN"
lsof -ti tcp:8011 >/dev/null && echo ":8011 role-shim UP" || echo ":8011 DOWN"
lsof -ti tcp:8001 >/dev/null && echo ":8001 mlx UP"       || echo ":8001 DOWN"
```

- 이 시스템에선 이 셋이 **launchd 서비스**로 항상 떠 있다:
  `com.ohama.litellm`, `com.ohama.role-shim`, `com.ohama.qwen122b`.
- 내려갔다면 재시작:
  ```sh
  launchctl kickstart -k gui/$(id -u)/com.ohama.litellm
  ```
- 스택을 처음부터 구축하는 방법(설치·shim·브릿지)은 별도 문서
  `documentation/howto/connect-codex-to-local-qwen122b.md` 에 있다.

## 필요한 도구가 설치돼 있나

```sh
codex --version       # 예: codex-cli 0.142.0
openhands --version   # 예: OpenHands CLI 1.16.0
```
- 둘 다 버전이 나오면 설치 완료. 안 나오면 다음 두 장(Codex/OpenHands 연결)에서 설치한다.

## 체크리스트

- [ ] `export LITELLM_API_KEY=dummy` 했다
- [ ] `gateway OK` 가 나온다
- [ ] `codex --version` / `openhands --version` 둘 다 버전이 나온다

다 됐으면 [4. Codex 연결](04-connect-codex.md)로.
