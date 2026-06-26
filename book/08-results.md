# 8. 결과 요약과 결론

앞 장의 해석법을 실제 측정값(v1.0, qwen-122b)에 적용해 보자. **이건 한 번의 스냅샷**이며, 당신이
직접 돌리면 숫자는 달라질 수 있다.

## ⏩ 결과 한눈 요약 (TL;DR)

| | 통과 레벨 | 속도(L1·L2) | ceiling(L3) | 한 줄 |
|---|---|---|---|---|
| **codex** | L1·L2 (L3 실패) | **더 빠름** (1.5~2배) | ❌ truncate로 빈 패키지 | 쉬운~중간 과제를 빠르게 끝냄, 대형은 끝까지 못 감(이 실행) |
| **openhands** | **L1·L2·L3 전부** | 더 느림 | ✅ 완성(9파일/362줄) | 느리지만 복잡한 과제까지 완성 |

**과제 ladder가 어디서 갈렸나:** L1·L2는 무승부(둘 다 통과), **L3에서 분기** — 가장 복잡한 과제에서
codex의 ceiling이 드러났다. (왜 이 ladder로 분기를 본 건지는 [2장](02-tasks.md) 참고.)

**기대효과 vs 실제(이 스냅샷):**
- L1 "둘 다 통과 기대" → ✅ 맞음.
- L2 "구조화 CLI" → ✅ 둘 다 통과.
- L3 "ceiling 시험, 갈릴 가능성↑" → ✅ 예상대로 갈림(codex 실패 / openhands 통과).

> ⚠️ 단, 이건 **1회 측정**이다. "codex가 L3를 못 한다"가 아니라 "이 실행에서 truncate됐다"이다.
> 확정하려면 반복 측정으로 통과율을 봐야 한다(아래 결론 참고).

## 측정 결과 (예시)

| Tool | Level | Success | Time | Steps (step_method) | Size |
|------|-------|---------|------|---------------------|------|
| codex | L1 fib | ✅ PASS | 26s | 2 (codex: exec blocks) | 1f / 31loc |
| codex | L2 wordstat | ✅ PASS | 98s | 10 (codex: exec blocks) | 4f / 148loc |
| codex | L3 kvstore | ❌ FAIL | 14s | 2 (codex: exec blocks) | 0f / 0loc |
| openhands | L1 fib | ✅ PASS | 49s | 4 (oh: agent messages) | 1f / 31loc |
| openhands | L2 wordstat | ✅ PASS | 145s | 16 (oh: agent messages) | 4f / 222loc |
| openhands | L3 kvstore | ✅ PASS | 147s | 15 (oh: agent messages) | 9f / 362loc |

## 해석 (§7의 순서대로 읽기)

**1) Success 먼저:**
- codex: L1·L2 통과, **L3 실패**.
- openhands: L1·L2·L3 **전부 통과**.

**2) 레벨별 비교:**
- **L1·L2** — 둘 다 성공. 능력은 대등(이 레벨에선).
- **L3(가장 어려움)** — 여기서 갈렸다. openhands는 완성, codex는 실패.

**3) Time:**
- codex가 L1(26 vs 49s)·L2(98 vs 145s)에서 **더 빠르다**(약 1.5~2배).
- 즉 "쉬운~중간 과제는 codex가 빠르게 끝낸다".

**4) Steps (step_method 확인 후, 도구 내부만):**
- codex L1→L2: 2→10 (어려워질수록 작업량↑) — 추세로만 읽는다.
- openhands L1→L2→L3: 4→16→15.
- codex의 10과 openhands의 16을 **직접 비교하지 않는다**(단위가 다름).

**5) 이상치 — codex L3 FAIL 진단:**
- `0 files` + `14초`(매우 짧음) → §7 표의 "일찍 잘림(진짜 실패)" 패턴.
- transcript를 보면 `mkdir kvstore` 만 하고 끊겼다 → codex가 L3에서 **truncate되어 빈 패키지만
  남기고 멈춤**. 격리 누출이 아니라 진짜 실패다.

## 이 스냅샷이 말하는 것 / 말하지 못하는 것

**말할 수 있는 것:**
- 이 실행에서 **codex는 빠르지만 가장 복잡한 과제(L3)를 완성하지 못했고**, **openhands는 더 느리지만
  세 레벨을 모두 완성했다.**
- 작업 규모도 openhands가 L3에서 더 컸다(9파일/362줄 vs codex 0).

**말하지 못하는 것:**
- "openhands가 항상 codex보다 낫다" — ❌. 한 번의 스냅샷이고 L1·L2는 codex가 더 빨랐다.
- "codex는 L3를 못 한다" — ❌. truncation은 실행마다 다를 수 있다. 여러 번 돌려 통과율로 봐야 한다.
- steps로 효율 비교 — ❌. 단위가 다르다.

## 결론 (균형 잡힌 읽기)

> **속도가 중요하고 과제가 단순~중간이면 codex가 유리**할 수 있고, **복잡한 멀티모듈 과제를 끝까지
> 완성하는 안정성이 중요하면 openhands가 유리**할 수 있다 — *이 한 번의 측정 기준으로는.* 확정하려면
> 같은 매트릭스를 여러 번 돌려 통과율·시간 분포를 봐야 한다.

당신의 결과로 직접 이 해석을 해보는 것이 이 책의 목적이다. 막히면 → [9. 막혔을 때](09-troubleshooting.md).
