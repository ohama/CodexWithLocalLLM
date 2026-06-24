# Codex 테스트 예제 (레벨별)

로컬 qwen-122b에 연결된 Codex를 **난이도 레벨별로 점검**하는 실행 가능한 예제 모음.
배선이 제대로 됐는지 확인하는 스모크 테스트부터, 멀티스텝 코딩·자가수정·멀티파일까지
**capability ladder** 형태로 구성했다. 그대로 복사해 자기 작업에 응용할 수 있는 **예제**이기도 하다.

## 무엇을 검증하나

| 레벨 | 스크립트 | 검증 내용 | 샌드박스 | 통과 신호 |
|------|----------|-----------|----------|-----------|
| **1** | `levels/01-smoke.sh` | 배선 생존 + 모델 응답 | read-only | 출력에 `CODEX_OK` |
| **2** | `levels/02-shell-tool.sh` | 셸 명령 실행 후 결과 보고 (도구 사용) | read-only | 실제 `python3 --version` 보고 |
| **3** | `levels/03-single-file.sh` | 단일 파일 코딩 + 테스트 + 실행 | workspace-write | `fib.py` 생성, 테스트 통과 |
| **4** | `levels/04-multi-step.sh` | 멀티스텝 프로젝트(도구+샘플+테스트) | workspace-write | `wordstat.py` 동작, 테스트 통과 |
| **5** | `levels/05-self-repair.sh` | 실패 테스트만 보고 버그 자가수정 | workspace-write | 수정 후 `All tests passed!` |
| **6** | `levels/06-multi-file.sh` | 멀티파일 패키지 생성 + unittest | workspace-write | `mathpkg/` + 테스트 통과 |

레벨이 올라갈수록 **자율성·도구 사용·검증 능력**을 더 깊게 요구한다.

## 사전 준비

- 배선이 끝나 있어야 함 → [`../../documentation/howto/connect-codex-to-local-qwen122b.md`](../../documentation/howto/connect-codex-to-local-qwen122b.md)
- LiteLLM 게이트웨이(:4000) UP (각 스크립트가 자동 확인)
- `codex`, `python3` 설치

## 실행

```bash
cd examples/codex-tests

./run.sh            # 전 레벨 순서대로
./run.sh 01         # 특정 레벨만 (번호 prefix)
./run.sh 03 05      # 여러 개
bash levels/05-self-repair.sh   # 스크립트 직접 실행도 가능
```

각 실행은 격리된 작업 디렉터리 `.runs/<레벨>-<타임스탬프>/` 에서 일어난다(git 무시).
Codex가 만든 파일은 거기 남으므로 결과를 들여다볼 수 있다.

## 실제 실행 샘플 (qwen-122b로 검증됨)

**Level 1 — smoke**
```
user> Reply with exactly: CODEX_OK and nothing else.
codex> CODEX_OK
```

**Level 2 — shell tool**
```
codex> The command `python3 --version` outputs: Python 3.14.6
```
→ 모델이 추측이 아니라 **실제로 명령을 실행**해서 보고.

**Level 3 — single-file**
```
fib(0)=0 ✓  fib(1)=1 ✓  fib(10)=55 ✓   (iterative 구현, 테스트 통과)
결과 파일: fib.py
```

**Level 5 — self-repair** (버그 위치 미고지)
```
진단: mean이 정수나눗셈(//), median이 짝수 길이에서 두 중앙값 평균 누락
수정: // → / , 짝수일 때 (s[mid-1]+s[mid])/2
독립 재검증: All tests passed!
```
→ 실행→실패확인→소스읽기→수정→재검증 순서를 스스로 밟고, **테스트 파일은 건드리지 않음**.

## 자가수정 픽스처

Level 5는 일부러 버그를 심은 코드를 사용한다.

- `fixtures/self-repair/stats.py` — `mean`(정수나눗셈), `median`(짝수 길이 미처리) 버그 2개
- `fixtures/self-repair/test_stats.py` — 올바른(=현재 실패하는) 테스트

스크립트가 이 둘을 작업 디렉터리로 복사한 뒤 Codex에게 "테스트만 보고 고쳐라"고 시킨다.

## 응용 (예제로 쓰기)

- 새 시나리오 추가: `levels/NN-내테스트.sh`를 만들고 `source ../common.sh` 후
  `codex exec "${CODEX_FLAGS[@]}" --sandbox <모드> "프롬프트"` 패턴을 복사.
- 권한 조절: 읽기 전용 점검은 `read-only`, 코드 생성·수정은 `workspace-write`.
- 비용 0: 로컬 모델이라 토큰 부담 없이 반복 실행 가능.

## 참고

- 일상 사용법 → [`../../documentation/howto/use-codex-cli.md`](../../documentation/howto/use-codex-cli.md)
- 각 레벨은 동시에 **로컬 모델의 에이전트 능력 회귀 테스트**로도 쓸 수 있다
  (모델/양자화/설정을 바꾼 뒤 같은 레벨을 돌려 품질 비교).
