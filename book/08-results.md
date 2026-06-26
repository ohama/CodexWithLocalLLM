# 8. 결과 요약과 결론

앞 장의 해석법을 **실제 12셀 측정값**(2 도구 × 6 레벨, qwen-122b)에 적용해 보자. **이건 한 번의
스냅샷**이며, 당신이 직접 돌리면 숫자는 달라질 수 있다.

## ⏩ 결과 한눈 요약 (TL;DR)

| | 통과 | 실패 | 속도 | 한 줄 |
|---|---|---|---|---|
| **codex** | L1·L2·**L4·L5·L6** (5/6) | **L3** | 통과 셀에서 대체로 **더 빠름** | 빠르고 폭넓게 통과, 단 L3(KV 서비스)만 truncate로 실패 |
| **openhands** | **L1~L6 전부 (6/6)** | 없음 | 더 느림(약 1.3~2배) | 느리지만 6종 모두 완성 |

**어디서 갈렸나:** 새로 추가한 L4·L5·L6에서는 **둘 다 통과** — 분별의 분기점은 여전히 **L3 한 곳**
(codex만 실패). 즉 codex의 약점은 "멀티모듈 + 상태영속 서비스(L3)를 끝까지 완성"하는 특정 지점이고,
*알고리즘(L4)·서브커맨드 상태(L5)·데이터처리(L6)* 는 codex도 문제없이 해냈다.

**기대효과 vs 실제:**
- L1 기본기 / L2 구조화 CLI → ✅ 둘 다 통과(예상대로).
- L3 멀티모듈+영속 "ceiling 시험" → ✅ 예상대로 갈림(codex 실패 / openhands 통과).
- L4 알고리즘·L5 상태·L6 데이터 → 둘 다 통과. **이 스냅샷에선 분별이 안 됨**(둘 다 능력 있음) —
  더 벌리려면 난이도를 더 높이거나 반복 측정이 필요(아래 결론).

> ⚠️ 1회 측정이다. "codex가 L3를 못 한다"가 아니라 "이 실행에서 truncate됐다"이다(이전 실행에서도
> 같은 14초 truncation이 재현된 점은 주목할 만하다).

## 측정 결과 (12셀)

| Tool | Level | Success | Time | Steps (step_method) | Size |
|------|-------|---------|------|---------------------|------|
| codex | L1 fib | ✅ PASS | 23s | 2 (codex: exec) | 1f / 25loc |
| codex | L2 wordstat | ✅ PASS | 83s | 6 (codex: exec) | 4f / 191loc |
| codex | L3 kvstore | ❌ FAIL | 14s | 2 (codex: exec) | 0f / 0loc |
| codex | L4 calc | ✅ PASS | 88s | — (codex: exec) | 1f / 187loc |
| codex | L5 todo | ✅ PASS | 101s | — (codex: exec) | 8f / 341loc |
| codex | L6 csvstat | ✅ PASS | 142s | — (codex: exec) | 5f / 490loc |
| openhands | L1 fib | ✅ PASS | 47s | 4 (oh: msgs) | 1f / 31loc |
| openhands | L2 wordstat | ✅ PASS | 165s | 17 (oh: msgs) | 4f / 305loc |
| openhands | L3 kvstore | ✅ PASS | 134s | 12 (oh: msgs) | 9f / 360loc |
| openhands | L4 calc | ✅ PASS | 120s | — (oh: msgs) | 1f / 200loc |
| openhands | L5 todo | ✅ PASS | 159s | — (oh: msgs) | 3f / 341loc |
| openhands | L6 csvstat | ✅ PASS | 173s | — (oh: msgs) | 5f / 345loc |

(정확한 steps·transcript 발췌는 `benchmark/RESULTS.md` 참고. steps는 도구별 단위가 달라 직접 비교 금지.)

## 해석 (§7의 순서대로 읽기)

**1) Success:** codex 5/6 (L3만 실패), openhands 6/6.
**2) 레벨별:** L1·L2·L4·L5·L6은 둘 다 통과 → 능력 대등. **L3에서만 분기**(codex 실패).
**3) Time:** 통과한 셀들에서 codex가 대체로 더 빠르다(L1 23 vs 47, L4 88 vs 120, L6 142 vs 173).
openhands는 안정적으로 통과하지만 느린 편.
**4) Steps:** 도구 내부 추세로만 — codex/openhands 단위가 달라 raw 비교 금지(§7).
**5) 이상치 — codex L3:** `0 files` + `14초` → 진짜 truncation(빈 `kvstore/`만 만들고 끊김). 격리
누출 아님(tasks/ 정규 유지 확인). 두 번째 실행에서도 동일 재현.

## 이 스냅샷이 말하는 것 / 말하지 못하는 것

**말할 수 있는 것:**
- codex는 **6종 중 5종을 빠르게 통과**하되 **L3(멀티모듈 KV 서비스)에서 반복적으로 truncate**되어 실패.
- openhands는 **6종 전부 완성**(더 느림).
- 새 과제(L4 알고리즘 / L5 상태 / L6 데이터)는 **둘 다 통과** → 이 난이도에선 분별 못 함.

**말하지 못하는 것:**
- "openhands가 항상 낫다" — ❌. 통과 셀에선 codex가 더 빨랐다.
- "codex는 L3를 영영 못 한다" — ⚠️ 두 번 재현됐지만 여전히 1구성의 결과. 반복 통과율로 확정 필요.
- steps로 효율 비교 — ❌. 단위가 다르다.
- "L4~L6은 변별력이 없다" — ❌. 이 난이도/모델에선 안 갈렸을 뿐. 더 어려운 변형이나 반복 측정이 필요.

## 결론 (균형 잡힌 읽기)

> **속도가 중요하고 과제가 단순~중간이면 codex가 유리**할 수 있고, **복잡한 멀티모듈 과제를 끝까지
> 완성하는 안정성이 중요하면 openhands가 유리**할 수 있다 — *이 한 번의 측정 기준으로는.* 확정하려면
> 같은 매트릭스를 여러 번 돌려 통과율·시간 분포를 봐야 한다.

당신의 결과로 직접 이 해석을 해보는 것이 이 책의 목적이다. 막히면 → [9. 막혔을 때](09-troubleshooting.md).
