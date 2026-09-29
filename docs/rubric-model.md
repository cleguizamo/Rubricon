# Rubric Model — Design Notes

- **Status:** draft
- **Owner:** Cristian Leguizamo
- **Last updated:** 2026-09-29

## Context

Rubricon scores customer support conversations against a versioned rubric. A
rubric is a set of criteria; an evaluation is the result of applying one rubric
version to one conversation. This document defines what those concepts mean
before any of them is encoded as types, so the code follows the reasoning and
not the other way around.

The model serves two uses with different needs:

- **Compliance:** did the agent do what policy requires? Needs objective,
  auditable verdicts.
- **Coaching:** where can the agent improve? Needs enough signal to rank and
  prioritize.

## 1. Criterion

A criterion is one observable aspect of the agent's behavior that can be judged
against the conversation.

In v1, every criterion is **binary** (pass / fail). Scaled criteria were
rejected. When two reviewers score the same conversation a 6 and a 7, the
disagreement cannot be interpreted: it is impossible to tell whether one of
them is wrong or whether the scale itself is ambiguous. A binary verdict
removes those grey areas. This matters because the core metric of this system
is judge–human agreement, and an ambiguous scale would add noise to the very
instrument used to measure it.

The trade-off is less nuance for coaching. It is accepted in v1 because
compliance, the primary use case, is binary by nature: the agent either
verified the customer's identity or did not.

## 2. Weights and aggregation

Each criterion carries a weight. Weights of the applicable criteria are
normalized to sum to 1, and the final score is the weighted sum of the
criterion scores.

Criteria have a **severity** that determines what a failure does:

- **Critical:** criteria that protect the security, privacy or accessibility of
  personal or corporate data. A failure **voids the evaluation**: the final
  score is 0 and the evaluation is flagged separately. A weighted average must
  never report 85% for a conversation that contains a data-protection
  violation.
- **Non-critical:** criteria such as empathy or honesty. A failure lowers the
  score and raises a flag, but does not void the evaluation.

When an evaluation is voided, **every individual criterion verdict is still
stored**, together with the context of the failure. The score becomes 0; the
detail is never discarded, because voided evaluations are the ones that most
need to be understood later.

## 3. Evidence

Every verdict carries evidence, and evidence is a **turn range**: the index of
the first and last turn of the conversation that support the verdict. A single
turn is the range `[n, n]`. Ranges are preferred over single indices because
they carry more context for the decision, and some criteria (for example, tone
sustained across a resolution) cannot be judged from one turn. One
representation also keeps the model and the code simpler.

Evidence also stores the **verbatim quote** the judge relied on. This is
redundant on purpose: it anchors what the judge actually read, independently of
how the conversation payload is later reprocessed.

Evidence is **validated** before it is accepted. A range that falls outside the
conversation, or a quote that does not appear in the cited turns, is
hallucinated evidence. When that happens the verdict is sent to human review,
and the case is recorded as a judge failure so it counts against the judge in
calibration.

## 4. Not applicable

A criterion that does not apply to a conversation is **excluded**, not failed.
It is removed from the calculation and its weight is redistributed across the
remaining applicable criteria, so conversations with different numbers of
applicable criteria remain comparable.

Applicability is decided by **deterministic rules in code**, evaluated before
the judge is called. The judge only receives the criteria that apply; it never
decides applicability.

The **not-applicable rate per criterion** is tracked as a health metric. A
criterion excluded in most conversations is badly defined.

## 5. Versioning

Rubric versions are **immutable**. Changing a rubric creates a new version; an
existing version is never edited in place.

Every evaluation stores the identifier of the rubric version that produced it.
Evaluations are also immutable: re-scoring a conversation with a newer rubric
version creates a **new evaluation**, and the previous one is kept unchanged.

## 6. Confidence

Every criterion verdict carries its own confidence score. After scoring, only
the verdicts below the confidence threshold are sent to human review, so a
reviewer checks a single criterion instead of re-reading the whole
conversation. This lowers the cost of human review, not the cost of judging.

A single confidence per evaluation was rejected. A low overall score does not
say which verdict is doubtful, so the reviewer has to read the entire
conversation again. Per-criterion confidence also reveals where the judge is
reliable and where it is not: over time, some criteria can be trusted above a
given threshold while others always need a human.

Confidence does not depend on severity. Critical and non-critical criteria are
measured the same way.

The confidence the judge reports about itself is not trusted as-is: LLM
self-reported confidence is poorly calibrated. It is calibrated against human
labels to find the threshold above which the judge's verdict can be accepted
without review.

Whichever option is chosen, the confidence the judge reports about itself is not
trusted as-is: LLM self-reported confidence is poorly calibrated. It is
calibrated against human labels to find the threshold above which the judge's
verdict can be accepted without review.
