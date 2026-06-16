# Engineering Impact Dashboard

An interactive dashboard that identifies the most impactful engineers on the [PostHog](https://github.com/PostHog/posthog) open-source repository. Built for engineering leaders who need to understand contributor impact at a glance — not through raw lines of code or commit counts alone.

---

## Tech Stack

### Backend
| Tool | Purpose |
|------|---------|
| **Python 3.14** | Runtime |
| **FastAPI + Uvicorn** | REST API (`GET /api/metrics`) |
| **SQLAlchemy (async) + asyncpg** | ORM and Postgres driver |
| **PostgreSQL 16** | Persistent store for ingested GitHub data |
| **Alembic** | Database migrations |
| **httpx** | Async GitHub REST/GraphQL client |
| **Pydantic Settings** | Configuration via environment variables |
| **Railway** | Deployment target (also runs locally via Docker) |

### Frontend
| Tool | Purpose |
|------|---------|
| **React 19** | UI framework |
| **TypeScript** | Type safety |
| **Vite** | Build tool and dev server |
| **TanStack Query** | Server state, loading and error handling |
| **Tailwind CSS v4** | Styling |
| **shadcn/ui** | UI components |

---

## Metrics

### Overview

Impact is measured across **three categories**, each capturing a different dimension of engineering contribution. Category scores are equal-weighted combinations of their sub-metrics. An **Overall** score combines all three categories equally.

| Category | What it measures | Significance |
|----------|-----------------|--------------|
| **Quantity** | Volume of shipped work | How much a contributor delivers — merged PR lines, issues opened, PRs created |
| **Quality** | Stability and durability of shipped work | Whether code sticks, gets reverted, introduces bugs, or needs rework |
| **Collaboration** | Team engagement and follow-through | Reviews given, issues closed, peer comments, review responsiveness |

**Scoring:**
- Category and Overall leaderboards use **normalized scores on a 0–100 scale**.
- Sub-metric breakdowns show **raw actual values** (counts, rates, hours) so leaders can validate findings.
- Lower-is-better metrics (revert rate, bug rate, review responsiveness) are inverted before normalization.

For full definitions and interpretations of each sub-metric, see [`plans/metric_definitions_v1.md`](plans/metric_definitions_v1.md).

Note: The original metric definitions created are present in [`plans/metric_definitions_v0.md`](plans/metric_definitions_v0.md). The metric definitions were changed to make them more feasible and cheap for fetching via Github API.

### Approach

The pipeline has three independent stages:

```
GitHub API  →  [Ingest]  →  Postgres  →  [Compute]  →  metrics.json  →  [API]  →  Frontend
```

#### Stage 1 — Ingest (`python -m app.ingest.cli`)

Fetches raw GitHub data for the PostHog repo (`main` branch, last 90 days) via batched GraphQL and REST calls, then upserts into Postgres.

| Table | Source | Used for |
|-------|--------|----------|
| `pull_requests` | GraphQL (merged, open, closed) | PR counts, line changes, acceptance rate |
| `pr_files` | GraphQL | PR durability (file overlap) |
| `pr_reviews` | GraphQL | Acceptance rate, code reviews |
| `pr_review_comments` | REST (paginated) | Peer comments, review responsiveness |
| `issues` | GraphQL | Issues opened/closed, bug issue rate |
| `issue_comments` | REST (paginated) | Peer comment volume |

Ingestion respects GitHub rate limits (tracks `X-RateLimit-Remaining`, retries with exponential backoff on 403/429). No per-commit API calls are made.

#### Stage 2 — Compute (`python -m app.metrics.cli`)

Reads all raw entities from Postgres and computes per-contributor metric values:

1. **Raw values** — calculated per contributor for all 11 sub-metrics (e.g. sum of PR lines, revert rate, median response hours).
2. **Normalization** — each sub-metric is normalized in 0-100 scale. Lower-is-better metrics are inverted first.
3. **Category scores** — equal-weighted average of normalized sub-metric scores within each category.
4. **Overall score** — equal-weighted average of the three category scores.
5. **Leaderboards** — top 5 contributors + average row built for each view.

Output is written to `backend/data/metrics.json`.

#### Stage 3 — Serve (`uvicorn main:app`)

The FastAPI server reads `metrics.json` and serves it at `GET /api/metrics`. No database queries happen at request time — dashboard loads are instant.

---

## Workflow

```
┌─────────────────────────────────────────────────────────┐
│                    Engineering Leader                    │
└────────────────────────┬────────────────────────────────┘
                           │ opens dashboard
                           ▼
┌─────────────────────────────────────────────────────────┐
│  Frontend (React SPA)                                    │
│  · TanStack Query fetches GET /api/metrics               │
│  · Loading screen while fetching                         │
│  · Error message if backend unavailable                  │
│  · 4 tabs: Overall · Quantity · Quality · Collaboration  │
│  · Each tab: description + top-5 leaderboard + breakdown │
└────────────────────────┬────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│  Backend API (FastAPI)                                   │
│  · Serves pre-computed metrics.json                      │
└─────────────────────────────────────────────────────────┘
```

**Tab structure (per [`plans/UX_workflow.md`](plans/UX_workflow.md)):**

- **Overall** — composite 0–100 score + breakdown of Quantity, Quality, Collaboration category scores
- **Quantity / Quality / Collaboration** — category 0–100 score + sub-metric breakdowns with raw values

Each leaderboard shows the **top 5 contributors** plus an **Average** row at the bottom.

---

## Design Choices

### What we chose and why

| Choice | Rationale |
|--------|-----------|
| **Three-stage pipeline** (ingest → compute → serve) | Decouples slow GitHub fetching from fast dashboard loads; re-compute scores without re-fetching |
| **Pre-computed JSON file** | Guarantees `<10s` dashboard load; no live GitHub calls on page view |
| **PR/issue-based metrics (not commit-based)** | Avoids expensive per-commit API calls; PostHog uses squash merges so PRs are the meaningful unit of work |
| **Composite scoring over raw counts** | A single LOC or commit count does not define impact; multi-dimensional view is more meaningful |
| **Normalized 0–100 scale** | Makes scores interpretable at a glance for a busy engineering leader |
| **Raw values in sub-metric breakdowns** | Allows validation — leaders can see *why* someone ranked highly, not just a number |
| **Equal weights** | Simple, transparent, no hidden assumptions about category importance |
| **GraphQL-first ingest** | Batches PR metadata, files, and reviews in minimal queries |

### Limitations

- **Branch filter** — only PRs targeting `main` are included; work on feature branches not yet merged is excluded.
- **90-day window** — configurable via `MEASUREMENT_DAYS`; does not capture long-tenure historical impact.
- **Revert detection** — relies on GitHub's `Revert "…" (#N)` title pattern; silent rollbacks without a revert PR are missed.
- **PR durability** — uses 14-day file overlap as a proxy for code longevity; misses slow erosion over months.
- **Bug issue rate** — depends on bug labels and PR references in issue bodies; unlabeled regressions are missed.
- **Review responsiveness** — contributors with no review feedback receive a neutral score (50), not penalized or rewarded.
- **GraphQL caps** — PRs with >100 changed files or >50 reviews may have incomplete data for durability and acceptance metrics.
- **No bot filtering** — dependabot and other bot accounts appear as contributors unless filtered manually.
- **Issue comments pagination** — GitHub REST limits page-based pagination to 100 pages; time-based `since` continuation is used but very high comment volume repos may still truncate.

---

## Execution

### Local

**Prerequisites:** Docker, Python 3.14+, Node.js 20+

**1. Start Postgres**
```bash
cd backend
docker compose up -d
```

**2. Configure environment**
```bash
cp .env.example .env
# Set GITHUB_TOKEN in .env
```

**3. Backend setup**
```bash
python3 -m venv ../weave-env
source ../weave-env/bin/activate
pip install -r requirements.txt
alembic upgrade head
```

**4. Ingest GitHub data** (one-time, takes several minutes)
```bash
python -m app.ingest.cli
```

**5. Compute metrics**
```bash
python -m app.metrics.cli
```

**6. Start API**
```bash
python -m uvicorn main:app --reload
# → http://localhost:8000
```

**7. Start frontend**
```bash
cd ../frontend
npm install
npm run dev
# → http://localhost:5173
```

**Verify:** open `http://localhost:5173` — dashboard should load with contributor leaderboards. API docs at `http://localhost:8000/docs`.

To refresh data after the initial ingest:
```bash
python -m app.ingest.cli      # re-fetch from GitHub
python -m app.metrics.cli     # re-compute scores
```

---

### Public

**Dashboard URL:** https://engg-dashboard.vercel.app/
