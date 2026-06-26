# 5. OpenHands 를 qwen-122b 에 연결

이미 openhands 가 로컬 qwen 으로 동작하면 건너뛴다.

## 연결됐는지 확인

```sh
python3 -c "import json,os;print(json.load(open(os.path.expanduser('~/.openhands/agent_settings.json')))['llm']['model'])"
# → openai/qwen-122b 가 나오면 연결됨
```

## 설치

OpenHands CLI는 uv tool 로 설치되어 `~/.local/bin/openhands` 를 제공한다:

```sh
openhands --version          # 이미 있으면 버전 출력 (예: OpenHands CLI 1.16.0)
# 없으면:
uv tool install openhands    # 또는 공식 설치 안내를 따른다
```

## 모델을 qwen-122b 로 지정

`~/.openhands/agent_settings.json` 의 `llm`(그리고 `condenser.llm`)을 로컬 게이트웨이로 맞춘다:

| 키 | 값 |
|----|----|
| `llm.model` | `openai/qwen-122b` |
| `llm.base_url` | `http://localhost:4000/v1` |
| `llm.api_key` | `dummy` |

> codex와 **같은 qwen-122b** 로 맞추는 게 핵심이다 — 그래야 "도구 차이"만 비교된다(모델 변수 제거).
> OpenHands는 내부 컨텍스트 압축기(condenser)도 LLM을 쓰므로 `condenser.llm` 도 같은 모델로 둔다.

설정 후 위 확인 명령으로 `openai/qwen-122b` 가 나오는지 다시 본다.

## OpenHands 의 한 가지 함정 (중요)

OpenHands 를 **손으로 직접 호출하지 말 것.** 특히 프롬프트를 `--file` 로 주면, OpenHands가 그 파일이
있는 디렉터리를 작업 위치로 잡아 **솔루션을 엉뚱한 폴더에 쓰는 격리 누출**이 생긴다(이 벤치마크
v1에서 실제로 발견·수정한 버그).

→ **항상 벤치마크 러너(`run.sh` / `run-matrix.sh`)를 통해서만** 실행한다. 러너는 프롬프트를 인라인
(`--task`)으로 주고 작업 폴더를 `OPENHANDS_WORK_DIR` 로 못박아 이 문제를 막는다.

## 체크리스트

- [ ] `openhands --version` 이 나온다
- [ ] 확인 명령이 `openai/qwen-122b` 를 출력한다

이제 두 도구 모두 같은 모델에 연결됐다 → [6. 벤치마크 수행](06-run.md)으로.
