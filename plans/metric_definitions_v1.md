Metrics Definition (use the data from the last 120 days)

All metrics are designed for **GitHub API-only ingestion** (batched REST/GraphQL → Postgres → compute). Avoid per-commit API calls.

Category 1: Quantity:

1. Merged PR lines changed:
Definition: Sum of `additions + deletions` across merged pull requests authored by the contributor in the measurement window.

Interpretation: Shows shipping volume through work that landed on the default branch. Higher values indicate more code delivered via merged PRs; does not reflect unmerged WIP or non-PR commits. Replaces commit-level line counts to avoid expensive per-commit API fetches.

2. Issues Opened:
Definition: Number of issues (bug reports, feature requests, discussions) opened by a contributor

Interpretation: Measures initiative and engagement in identifying problems or proposing improvements. Contributors who open more issues drive discussion and help shape the project roadmap, even if they don't implement the solutions.

3. PRs Created:
Definition: Total number of pull requests (open, merged) created by the contributor.

Interpretation: Tracks active contribution to the codebase. More PRs show consistent participation


Category 2: Quality:

1. Reverted merged PR rate:
Definition: Number of the contributor's merged PRs that were later undone by a merged PR matching GitHub's revert pattern (e.g. title `Revert "…" (#12345)` referencing the original PR), divided by the contributor's total merged PRs in the window.

Interpretation: Lower is better. Measures how often shipped work was explicitly rolled back. Frequent reverts may signal rushed work, insufficient testing, or misalignment with project standards. Misses silent rollbacks without a revert PR.

2. PR durability rate:
Definition: Percentage of the contributor's merged PRs that had **no** other merged PR (by any author) within **14 days** touching any of the same files (`filename` overlap from PR file lists).

Interpretation: Indicates whether shipped changes stuck or were quickly reworked in the same areas. High durability suggests lasting impact; low durability may indicate quick fixes, temporary workarounds, or code that needed immediate follow-up. Replaces commit-level retention metrics; uses one PR files fetch per merged PR during ingest.

3. Post-merge bug issue rate:
Definition: Number of bug-labeled issues opened after merge that reference or link to the contributor's merged PRs, divided by the contributor's total merged PRs.

Interpretation: Ratio of regressions or follow-up bugs tied to shipped PRs. Lower is better; higher ratios indicate potential issues with code review depth or testing rigor, and may warrant pair-review or extended testing. Computed from batched issue + PR linking ingest (GraphQL timeline / cross-references).

4. PR acceptance rate:
Definition: Percentage of a contributor's merged PRs that were accepted without any `CHANGES_REQUESTED` review before merge.

Interpretation: Reflects code quality at review time. Higher rates show PRs align with standards on first pass; lower rates suggest improvements needed in pre-submission testing, code style, or requirement clarity. Fetch reviews via batched GraphQL alongside merged PR ingest.


Category 3: Collaboration:

1. Code Reviews:
Definition: Count of code reviews (approvals, comments, change requests) given by the contributor on other people's PRs.

Interpretation: Measures mentorship and knowledge sharing. More reviews show active engagement in team growth and quality gates; low review counts may indicate siloed work or missed mentorship opportunities.

2. Issues closed:
Definition: Number of issues closed via PRs authored by the contributor, or issues directly assigned/resolved by the contributor.

Interpretation: Shows impact on project velocity and problem-solving. Closing issues (yours or others') demonstrates follow-through and commitment to unblocking the team, not just shipping new features.

3. Peer comment volume:
Definition: Number of comments left by the contributor on other people's PRs and issues in the measurement window.

Interpretation: Indicates active participation in peer feedback loops. Frequent comments build team cohesion and catch issues early; low volume may signal disengagement. Replaces response-time tracking to avoid costly per-PR timeline fetches.

4. Review responsiveness:
Definition: Median time (hours) from the first review comment or `CHANGES_REQUESTED` on a contributor's open PR to the contributor's next comment on that same PR.

Interpretation: Measures responsiveness to code review on the contributor's own PRs only (a bounded subset of timeline data). Lower median is better; long delays may signal bottlenecks in the author's review loop.
