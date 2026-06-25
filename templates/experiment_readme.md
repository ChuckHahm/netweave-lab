# EXP00N — [Short Title]

**Status:** planned  
**Date started:** YYYY-MM-DD  
**Author:** Chuck Wiley

## Question

[One sentence — the design decision being tested]

## Hypothesis

[What you expect to find and why]

## Success criterion

[Specific measurable threshold that would validate the hypothesis]

## Variants tested

| Variant | Key parameters |
|---------|----------------|
| variant_A | param=value |
| variant_B | param=value |

## Results

| Variant | NDCG@10 | Notes |
|---------|---------|-------|
| variant_A | N.NN | ... |
| variant_B | N.NN | ... |

## Decision

**Winner:** [variant name]  
**Margin over baseline:** [+N.NN]  
**Decision:** [VALIDATED | INCONCLUSIVE | REJECTED]  
**MLflow run ID:** [run-id-here]  
**Date of decision:** YYYY-MM-DD

## Production change (if VALIDATED)

File: `netweave/src/[filename].py`  
Function: `[function_name]`  
Change: [one sentence description of what changes]  
Citation: `# Validated in EXP00N — see netweave-lab/experiments/EXP00N/`
