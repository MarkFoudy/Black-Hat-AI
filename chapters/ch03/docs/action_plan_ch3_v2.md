# Chapter 3 v2 Action Plan
## Code Alignment with Updated Chapter Content

**Date:** 2026-01-24
**Status:** Planning Phase - DO NOT CODE YET
**Source:** chapters/ch03/docs/ch3_v2.docx

---

## Executive Summary

The chapter has been significantly restructured with new narrative flow, updated code examples, and additional concepts. This document identifies what code needs to be **removed** (no longer relevant) and what needs to be **added** (new requirements from v2).

---

## Part A: Code to Remove or Deprecate

### 1. **Outdated Listing References**
**Files Affected:** Multiple source files in `src/`

**Issue:** Current code files reference old listing numbers that no longer match the updated chapter structure.

**Action:**
- Update all docstring references to listing numbers (e.g., "From Listing 3.4" may now be different)
- Review `docs/listings_reference.md` and update the mapping table
- Ensure consistency between code comments and chapter listings

**Priority:** Medium (documentation accuracy)

---

### 2. **README.md Listing Table**
**File:** `chapters/ch03/README.md` (lines 83-101)

**Issue:** The listing reference table maps old listing numbers to files. The new chapter has renumbered listings:
- Old Listing 3.1 (WAF branching) - may be removed or moved
- Listings 3.1-3.5 in new version are: exponential backoff, checkpointing, error count hook, trace, mermaid

**Action:**
- Completely rebuild the listing reference table based on ch3_v2.docx
- Cross-reference each listing number with actual code files
- Remove references to listings that no longer exist

**Priority:** High (affects reader navigation)

---

### 3. **LangChain Adapter Code**
**Files:** `src/adapters/langchain/agent.py`

**Issue:** The new chapter doesn't mention LangChain integration in the main narrative. While the adapter exists and works, it may be better suited as optional/supplementary material.

**Action:**
- **Option A:** Keep as-is but mark as "Advanced/Optional" in README
- **Option B:** Move to a separate "extensions" or "integrations" directory
- **Option C:** Remove entirely if not covered in chapter

**Recommendation:** Keep but clearly mark as optional extension

**Priority:** Low (doesn't break functionality)

---

### 4. **Overly Complex Example Code**
**Files:** Example scripts may have complexity not reflected in chapter

**Issue:** If chapter simplifies examples, code should match the pedagogical level

**Action:**
- Review each example script against chapter narrative
- Simplify if chapter focuses on core concepts over feature completeness
- Remove "bonus" features not mentioned in text

**Priority:** Medium (pedagogical alignment)

---

## Part B: Code to Add

### 1. **ReconNormalizeAgent** ⭐ CRITICAL
**Reference:** Section 3.9.2, Listing 3.6

**Current State:** Does NOT exist

**Description:** The chapter introduces a dedicated normalization agent that sits between raw recon input and the triage agent. This is architecturally significant.

**Requirements:**
```python
class ReconNormalizeAgent:
    """
    Normalizes raw reconnaissance data into a predictable schema.

    Does NOT score, prioritize, or recommend actions.
    Sole responsibility: convert raw recon -> structured artifact.
    """

    def run(self, raw_records):
        for r in raw_records:
            yield {
                "host": r["host"],
                "path": r.get("path", "/"),
                "status": r["status"],
                "title": r.get("title", ""),
                "signals": infer_signals(r),  # Derived signals
                "ts": now()
            }
```

**Location:** Create new file `src/agents/recon_normalize.py`

**Integration Points:**
- Update `src/agents/__init__.py` to export
- Add to capstone example (example_07_capstone.py)
- Create test file `tests/test_agents/test_recon_normalize.py`
- Update orchestrator examples to show Recon → Normalize → Triage flow

**Rationale:** This separates concerns between data collection (ReconAgent) and data normalization (ReconNormalizeAgent), which is a key architectural pattern in the updated chapter.

**Priority:** CRITICAL (new agent type)

---

### 2. **Enhanced Artifact Schema Validation**
**Reference:** Section 3.10.1 "Silent artifact drift"

**Current State:** Basic artifact structure exists but no validation

**Description:** Chapter emphasizes treating artifacts as contracts with schema versioning and explicit validation.

**Requirements:**
- Add `schema_version` field to `PipelineArtifact` class
- Implement `validate_schema()` method that fails loudly on mismatches
- Add schema metadata to artifacts
- Create artifact validator utility

**Location:**
- Enhance `src/core/artifact.py`
- Create `src/core/schema_validator.py` (new file)

**Example:**
```python
class PipelineArtifact:
    schema_version: str = "1.0.0"

    def validate_against(self, expected_schema: dict) -> bool:
        """Validate artifact structure matches expected schema."""
        # Implementation
        pass
```

**Priority:** HIGH (addresses major failure mode)

---

### 3. **Error Classification Table Implementation**
**Reference:** Section 3.8.3, Table 3.1 "Failure patterns and mitigations"

**Current State:** Retry logic exists but no error classification

**Description:** Chapter provides detailed error taxonomy with specific mitigation strategies.

**Requirements:**
Create `src/resilience/error_classifier.py`:
```python
class ErrorClass(Enum):
    TRANSIENT_NETWORK = "transient_network"
    MODEL_FAILURE = "model_failure"
    POLICY_VIOLATION = "policy_violation"
    TOOL_CRASH = "tool_crash"
    OUTPUT_ANOMALY = "output_anomaly"
    ETHICAL_VIOLATION = "ethical_violation"
    MEMORY_OVERFLOW = "memory_overflow"

class ErrorClassifier:
    def classify(self, exception: Exception) -> ErrorClass:
        """Classify exception into error category."""

    def get_mitigation(self, error_class: ErrorClass) -> str:
        """Return recommended mitigation strategy."""
```

**Integration:**
- Update retry logic to use classification
- Add to orchestrator error handling
- Create example showing different error paths

**Priority:** MEDIUM (improves resilience)

---

### 4. **Monitoring and Metrics Hooks**
**Reference:** Section 3.8.4 "Monitoring, metrics, and alerts"

**Current State:** Basic alert hook exists in `src/resilience/alerts.py`

**Description:** Chapter emphasizes four monitoring areas: errors, cost, quality, performance

**Requirements:**
Create `src/resilience/metrics.py`:
```python
class MetricsCollector:
    """Track pipeline health metrics."""

    def track_error(self, error_type: str, stage: str):
        """Count errors by type and stage."""

    def track_cost(self, tokens: int, cost: float, agent: str):
        """Track token usage and API costs."""

    def track_quality(self, metric: str, value: float):
        """Track agent quality metrics (hallucination rate, etc)."""

    def track_performance(self, stage: str, duration: float):
        """Track timing and throughput."""
```

**Integration:**
- Add hooks to orchestrator
- Create dashboard example (optional)
- Add to capstone example

**Priority:** MEDIUM (production readiness)

---

### 5. **Failure Mode Examples**
**Reference:** Section 3.10 "Failure modes in multi-agent systems"

**Current State:** No explicit failure mode demonstrations

**Description:** Chapter dedicates entire section to common failures and how architecture prevents them.

**Requirements:**
Create new example script `scripts/example_08_failure_modes.py`:
- Demonstrate silent artifact drift (schema mismatch)
- Show orchestration leak (agent decides execution order)
- Illustrate safety gate bypass
- Memory accumulation without correction
- Overloaded agent

Each should show:
1. The failure
2. How it manifests
3. The architectural fix

**Priority:** MEDIUM (pedagogical value)

---

### 6. **Memory and State Management**
**Reference:** Section 3.7 "Shared state and memory boundaries"

**Current State:** Not implemented

**Description:** Chapter discusses memory as organized/indexed artifacts for reuse across stages.

**Requirements:**
Create `src/core/memory.py`:
```python
class SharedMemory:
    """
    Memory layer that organizes and indexes artifacts for reuse.

    Memory is built on top of artifacts, not replacing them.
    """

    def summarize_artifact(self, artifact: PipelineArtifact) -> dict:
        """Create summary for downstream reuse."""

    def index_artifacts(self, run_dir: str) -> dict:
        """Build searchable index of past artifacts."""

    def retrieve_context(self, query: str) -> List[PipelineArtifact]:
        """Retrieve relevant past artifacts."""
```

**Priority:** LOW (advanced feature, may defer to Chapter 4)

---

### 7. **Updated Code Listings in Chapter**
**Reference:** Throughout chapter

**Current State:** Listings exist but may not match new format exactly

**Listings to Review and Update:**
- ✅ Listing 3.1: Exponential backoff (exists in retry.py) - **VERIFY MATCH**
- ✅ Listing 3.2: Checkpointing (exists in checkpoint.py) - **VERIFY MATCH**
- ❌ Listing 3.3: Error count hook (check if matches alerts.py) - **UPDATE IF NEEDED**
- ✅ Listing 3.4: Trace summarization (exists in trace.py) - **VERIFY MATCH**
- ✅ Listing 3.5: Mermaid flowchart (exists in mermaid.py) - **VERIFY MATCH**
- ❌ Listing 3.6: ReconNormalizeAgent - **CREATE NEW**
- 🔄 Listing 3.7: TriageAgent - **VERIFY MATCH**
- 🔄 Listing 3.8: ReportAgent - **VERIFY MATCH**

**Action:**
- Create `docs/code_listing_verification.md` document
- Compare each listing in chapter with actual code
- Update code to match chapter examples exactly
- Note any intentional deviations

**Priority:** HIGH (chapter-code alignment)

---

### 8. **Exercise 3.1 Support Code**
**Reference:** Section 3.9.5 (after capstone)

**Current State:** Exercise mentioned but no starter code

**Description:** Chapter includes exercise to "extend pipeline to identify login pages"

**Requirements:**
Create `scripts/exercise_31_login_detection.py` (starter template):
```python
"""
Exercise 3.1: Extend the multi-agent pipeline to identify login pages.

TODO:
- [ ] Add a new agent that analyzes HTTP titles for potential login pages
- [ ] Update orchestrator to include it
- [ ] Rerun the pipeline
- [ ] Visualize the new stage in Mermaid graph
- [ ] Compare artifact sizes before/after
"""

class LoginDetectionAgent(BaseStage):
    """TODO: Implement login page detection logic."""
    pass
```

**Priority:** LOW (student exercise, not core)

---

### 9. **Enhanced Documentation**
**Reference:** Throughout chapter

**New Documentation Needed:**
1. **Architecture Decision Records (ADR):**
   - Why artifacts over direct calls
   - Why external orchestration
   - Why explicit gates

2. **Failure Mode Runbook:**
   - How to diagnose each failure type from Section 3.10
   - Recovery procedures

3. **Production Deployment Guide:**
   - Monitoring setup
   - Alert configuration
   - Compliance evidence collection

**Location:** Create `docs/architecture/` directory

**Priority:** MEDIUM (production readiness)

---

## Part C: Structural Changes

### 1. **Pipeline Topology Examples**
**Reference:** Section 3.2 mentions sequential, parallel, branching, event-driven

**Current State:** Only sequential examples exist

**Action:**
- Add example showing parallel execution (multiple recon sources)
- Add example showing branching (WAF detection → route to different agents)
- Add example showing event-driven (continuous monitoring)

**Priority:** MEDIUM (demonstrates flexibility)

---

### 2. **Test Coverage for New Concepts**
**Files:** `tests/` directory

**Required New Tests:**
- `tests/test_agents/test_recon_normalize.py`
- `tests/test_core/test_schema_validator.py`
- `tests/test_resilience/test_error_classifier.py`
- `tests/test_resilience/test_metrics.py`
- `tests/test_core/test_memory.py`

**Priority:** MEDIUM (quality assurance)

---

### 3. **Data Directory Updates**
**Files:** `data/` directory

**Current State:** Has scope.json and targets.py

**New Requirements:**
- Add sample raw recon data for ReconNormalizeAgent testing
- Add example malformed artifacts for schema validation testing
- Add sample error scenarios for classifier testing

**Priority:** LOW (testing support)

---

## Implementation Priority Matrix

| Priority | Items | Estimated Effort |
|----------|-------|------------------|
| CRITICAL | ReconNormalizeAgent | 4-6 hours |
| HIGH | Artifact schema validation | 3-4 hours |
| HIGH | Listing verification & updates | 4-6 hours |
| HIGH | README listing table rebuild | 1-2 hours |
| MEDIUM | Error classification | 3-4 hours |
| MEDIUM | Metrics & monitoring | 4-5 hours |
| MEDIUM | Failure mode examples | 3-4 hours |
| MEDIUM | Test coverage | 6-8 hours |
| MEDIUM | Enhanced documentation | 4-6 hours |
| LOW | Memory layer | 6-8 hours |
| LOW | Exercise templates | 1-2 hours |
| LOW | Data samples | 1-2 hours |

**Total Estimated Effort:** 40-57 hours

---

## Phased Rollout Recommendation

### Phase 1: Critical Alignment (8-12 hours)
- Add ReconNormalizeAgent
- Verify and update all code listings
- Rebuild README listing table
- Update docstring references

**Deliverable:** Code matches chapter examples exactly

---

### Phase 2: Robustness (10-13 hours)
- Add artifact schema validation
- Implement error classification
- Add metrics collection
- Create failure mode examples

**Deliverable:** Production-grade resilience patterns

---

### Phase 3: Completeness (12-16 hours)
- Full test coverage
- Enhanced documentation
- Pipeline topology examples
- Exercise templates

**Deliverable:** Complete teaching package

---

### Phase 4: Advanced Features (Optional, 8-10 hours)
- Memory layer implementation
- Advanced monitoring dashboard
- Additional integrations

**Deliverable:** Extended capabilities beyond chapter scope

---

## Risk Assessment

### High Risk Items
1. **ReconNormalizeAgent architecture change** - Affects capstone pipeline flow
2. **Listing renumbering** - Could confuse readers if misaligned
3. **Schema validation** - Could break existing artifacts if too strict

### Mitigation Strategies
1. Implement ReconNormalizeAgent with backward compatibility flag
2. Create clear mapping document from old → new listings
3. Make schema validation opt-in initially, with clear migration path

---

## Open Questions for Author/Editor

1. **ReconAgent vs ReconNormalizeAgent:** Should the current `ReconAgent` be:
   - Renamed to `ReconNormalizeAgent` (breaking change)
   - Kept as-is, with new agent added (recon_raw + recon_normalize)
   - Split into two agents (ReconCollector + ReconNormalizer)

2. **LangChain integration:** Should this remain in core or move to extensions?

3. **Exercise 3.1:** Provide starter code or leave entirely to reader?

4. **Memory layer (Section 3.7):** Implement now or defer to later chapter?

5. **Listing code style:** Should code listings be:
   - Minimal (teaching-focused, stripped down)
   - Production-ready (full implementations)
   - Hybrid (simple examples + full impl in repo)

---

## Next Steps

**Before coding:**
1. ✅ Review this action plan
2. ⬜ Resolve open questions
3. ⬜ Prioritize phases based on publication timeline
4. ⬜ Get stakeholder approval on scope

**During implementation:**
1. Follow priority matrix (Critical → High → Medium → Low)
2. Update this document as decisions are made
3. Track actual effort vs. estimates
4. Document any deviations from plan

---

## Document Version

- **Version:** 1.0
- **Author:** Claude Code Analysis
- **Review Status:** Awaiting human review
- **Last Updated:** 2026-01-24

---

## Appendix: Quick Reference Checklist

**Code to Remove/Update:**
- [ ] Update all listing number references in docstrings
- [ ] Rebuild README listing table (lines 83-101)
- [ ] Decide on LangChain adapter location
- [ ] Simplify examples if needed for pedagogy

**Code to Add:**
- [ ] ReconNormalizeAgent (CRITICAL)
- [ ] Schema validation for artifacts
- [ ] Error classification system
- [ ] Metrics collection hooks
- [ ] Failure mode demonstration examples
- [ ] Memory layer (optional)
- [ ] Exercise 3.1 template (optional)

**Documentation to Update:**
- [ ] README.md listing table
- [ ] docs/listings_reference.md
- [ ] Add architecture decision records
- [ ] Add failure mode runbook
- [ ] Add production deployment guide

**Tests to Add:**
- [ ] test_recon_normalize.py
- [ ] test_schema_validator.py
- [ ] test_error_classifier.py
- [ ] test_metrics.py
- [ ] test_memory.py (if implemented)
