# Requirements: Agent Benchmark — Codex vs OpenHands

**Defined:** 2026-06-26
**Core Value:** 같은 과제를 두 도구에 동일 조건으로 돌려, 재현·검증 가능한 형태로 능력·시간을 비교 기록한다.

## v1 Requirements

### Tasks (과제 정의)

- [ ] **TASK-01**: 3단계 복잡도 과제가 고정 정의되어 있다 (L1 단일파일 / L2 멀티파일 CLI / L3 다중모듈 서비스)
- [ ] **TASK-02**: 각 과제는 Python stdlib만 쓰며, 합격 기준이 "테스트 통과"로 명확히 정의된다
- [ ] **TASK-03**: 각 과제 프롬프트가 도구와 무관하게 동일한 텍스트로 한 곳에 보관된다

### Runner (동일 조건 실행)

- [ ] **RUN-01**: 한 명령으로 (도구, 레벨)을 지정해 실행할 수 있다
- [ ] **RUN-02**: 각 실행은 격리된 작업 디렉터리에서 일어나 도구 간/실행 간 오염이 없다
- [ ] **RUN-03**: 두 도구 모두 동일 모델(qwen-122b, LiteLLM :4000)로 실행된다
- [ ] **RUN-04**: codex는 `< /dev/null`, openhands는 `--headless` 등 비대화형으로 안정 실행된다
- [ ] **RUN-05**: 단일 백엔드 경합을 피해 순차 실행된다

### Metrics (지표 수집)

- [ ] **MET-01**: 성공 여부를 독립 테스트 재실행으로 판정해 기록한다 (도구 자가보고 신뢰 안 함)
- [ ] **MET-02**: 과제별 wall-clock 소요 시간을 측정·기록한다
- [ ] **MET-03**: 단계/도구호출 수(파일수정·명령실행·자가수정)를 기록한다
- [ ] **MET-04**: 산출 규모(파일 수·코드 줄 수)를 기록한다

### Report (결과 기록)

- [ ] **REP-01**: 결과가 도구 × 레벨 매트릭스(표)로 정리된다
- [ ] **REP-02**: 각 실행의 원본 로그/transcript가 보존되어 과정을 되짚을 수 있다
- [ ] **REP-03**: 레벨별로 두 도구의 차이(시간·과정·산출)가 요약된다

### Reproducibility (재현 가이드)

- [ ] **REPRO-01**: 사용자가 따라 할 수 있는 단계별 가이드가 있고, 매 명령과 효과가 명시된다
- [ ] **REPRO-02**: 사전조건(서비스 기동·모델 설정) 확인 방법이 문서화된다
- [ ] **REPRO-03**: 측정을 처음부터 재실행하는 방법이 한 곳에 정리된다

## v2 Requirements

### Extended

- **EXT-01**: hermes를 비교에 포함 (3자)
- **EXT-02**: 정밀 토큰/비용 회계
- **EXT-03**: 더 큰/모호한 과제 레벨(L4) 추가
- **EXT-04**: 여러 번 반복 실행 후 평균/분산 집계

## Out of Scope

| Feature | Reason |
|---------|--------|
| hermes 비교 | 이번 마일스톤은 codex+openhands만 (기존 비교 문서에 hermes 별도 존재) |
| 클라우드 모델 비교 | 로컬 qwen-122b 단일 백엔드 고정(공정성·비용 0) |
| 멀티 백엔드 동시성/병렬 측정 | 단일 mlx 백엔드 → 직렬이 기준 |
| 외부 의존 과제 | stdlib 한정으로 재현성 확보 |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| TASK-01 | Phase 1 — Fixed Tasks | Complete |
| TASK-02 | Phase 1 — Fixed Tasks | Complete |
| TASK-03 | Phase 1 — Fixed Tasks | Complete |
| RUN-01 | Phase 2 — Equal-Conditions Runner | Complete |
| RUN-02 | Phase 2 — Equal-Conditions Runner | Complete |
| RUN-03 | Phase 2 — Equal-Conditions Runner | Complete |
| RUN-04 | Phase 2 — Equal-Conditions Runner | Complete |
| RUN-05 | Phase 2 — Equal-Conditions Runner | Complete |
| MET-01 | Phase 3 — Metric Collection | Pending |
| MET-02 | Phase 3 — Metric Collection | Pending |
| MET-03 | Phase 3 — Metric Collection | Pending |
| MET-04 | Phase 3 — Metric Collection | Pending |
| REP-01 | Phase 4 — Benchmark Run & Reporting | Pending |
| REP-02 | Phase 4 — Benchmark Run & Reporting | Pending |
| REP-03 | Phase 4 — Benchmark Run & Reporting | Pending |
| REPRO-01 | Phase 5 — Reproducibility Guide | Pending |
| REPRO-02 | Phase 5 — Reproducibility Guide | Pending |
| REPRO-03 | Phase 5 — Reproducibility Guide | Pending |

**Coverage:**
- v1 requirements: 18 total
- Mapped to phases: 18
- Unmapped: 0 ✓

---
*Requirements defined: 2026-06-26*
