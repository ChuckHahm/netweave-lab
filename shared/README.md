# shared/

This directory should be a symlink (or copy) of `netweave/data/processed/`.

## Setup

From the `netweave-lab/` directory:

```bash
ln -s ../netweave/data/processed ./shared
```

Or copy manually if symlinks are unavailable:

```bash
cp -r ../netweave/data/processed/. ./shared/
```

## Expected contents

| File | Description |
|------|-------------|
| `nodes.parquet` | Node table. Required columns: `node_id`, `name`, `position`, `employer`, `domain_tags`, `seniority`, `recency_days` |
| `edges.parquet` | Edge table. Required columns: `source`, `target`, `tie_strength`, `role_fit`, `intro_likelihood`, `composite` |

## Important

This directory is **read-only** from the perspective of `netweave-lab`.
Never write output data here. Experiment outputs go to `experiments/EXP00N/`.
