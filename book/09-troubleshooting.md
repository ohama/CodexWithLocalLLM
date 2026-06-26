# 9. 막혔을 때 (트러블슈팅)

## 증상별 빠른 진단

| 증상 | 원인 / 조치 |
|------|-------------|
| `gateway DOWN` | 백엔드 스택을 안 띄움 → [3장](03-prerequisites.md) 참고. `lsof -ti tcp:4000` 로 확인, `launchctl kickstart -k gui/$(id -u)/com.ohama.litellm` 로 재시작 |
| codex 가 멈춤(hang), 출력 없음 | `codex exec` 를 stdin 없이 돌림 → 항상 `< /dev/null` 붙이기. (러너는 자동 처리) mlx CPU 0%면 이 증상 |
| openhands 출력이 run 폴더에 없음 (`0 files`) | openhands 를 손으로 `--file` 로 부름 → **반드시 `run.sh`/`run-matrix.sh` 로만** 실행 ([5장](05-connect-openhands.md)) |
| 모델이 qwen-122b 가 아님 | [4](04-connect-codex.md)·[5](05-connect-openhands.md)장 확인 명령 재실행 |
| 매트릭스 중간에 느림/멈춘 듯 | L3는 원래 오래 걸린다(수 분). 백그라운드(`&`)로 돌렸는지 확인 — 직렬로 포그라운드 실행할 것 |
| `FAIL` 인데 진짜인지 모르겠음 | [7장 §이상치 진단](07-interpret.md) — `0 files`면 누출 의심, 채점기 직접 실행해 확인 |

## 채점기 직접 돌려보기

어떤 실행이 왜 실패/성공인지 확인하려면 채점기를 직접 돌린다(LLM 호출 없음, 즉시):

```sh
python3 benchmark/tasks/<level>/test.py <run_dir>
echo "exit=$?"   # 0 = PASS, nonzero = FAIL
# 예: python3 benchmark/tasks/l1-fib/test.py benchmark/.runs/codex-l1-fib-...
```

## 한 칸만 다시 측정

특정 칸만 재실행:
```sh
export LITELLM_API_KEY=dummy
bash benchmark/run.sh openhands l3     # 그 칸만 새 run 폴더에 다시
python3 benchmark/report.py            # 리포트 갱신
```

## 깨끗이 다시 시작

```sh
rm -rf benchmark/.runs/*               # 이전 실행 산출물 비우기 (gitignore라 영향 없음)
bash benchmark/run-matrix.sh           # 전체 재측정
python3 benchmark/report.py
```

## 더 깊은 참고 (저장소 문서)

- 백엔드 배선 구축 전 과정 → `documentation/howto/connect-codex-to-local-qwen122b.md`
- 도구 동작 방식 비교(분석) → `documentation/codex-hermes-openhands-comparison.md`
- codex CLI 운영/권한/트러블슈팅 → `documentation/howto/use-codex-cli.md`

---

## 마무리

여기까지 따라왔다면 — 백엔드 확인 → 두 도구 연결 → 6칸 매트릭스 수행 → 표를 올바르게 해석 —
**codex와 openhands를 직접 비교 검증**한 것이다.

핵심 세 가지만 기억하자:
1. **성공은 독립 채점기가 정한다**(도구 자기보고 불신).
2. **steps는 도구끼리 직접 비교 금지**(단위가 다름 — `step_method` 확인).
3. **결과는 스냅샷**이다(LLM 비결정성 — 확신하려면 반복 측정).
