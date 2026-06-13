"""Metric definitions sourced from plans/metric_definitions_v1.md."""

from dataclasses import dataclass


@dataclass(frozen=True)
class MetricDefinition:
    key: str
    name: str
    definition: str
    interpretation: str
    category: str
    higher_is_better: bool


METRIC_DEFINITIONS: list[MetricDefinition] = [
    MetricDefinition(
        key="merged_pr_lines_changed",
        name="Merged PR lines changed",
        definition="Sum of additions + deletions across merged pull requests authored by the contributor in the measurement window.",
        interpretation="Shows shipping volume through work that landed on the default branch. Higher values indicate more code delivered via merged PRs.",
        category="quantity",
        higher_is_better=True,
    ),
    MetricDefinition(
        key="issues_opened",
        name="Issues opened",
        definition="Number of issues opened by a contributor in the measurement window.",
        interpretation="Measures initiative and engagement in identifying problems or proposing improvements.",
        category="quantity",
        higher_is_better=True,
    ),
    MetricDefinition(
        key="prs_created",
        name="PRs created",
        definition="Total number of pull requests created by the contributor in the measurement window.",
        interpretation="Tracks active contribution to the codebase. More PRs show consistent participation.",
        category="quantity",
        higher_is_better=True,
    ),
    MetricDefinition(
        key="reverted_merged_pr_rate",
        name="Reverted merged PR rate",
        definition="Share of the contributor's merged PRs later undone by a merged revert PR referencing the original PR number.",
        interpretation="Lower is better. Measures how often shipped work was explicitly rolled back.",
        category="quality",
        higher_is_better=False,
    ),
    MetricDefinition(
        key="pr_durability_rate",
        name="PR durability rate",
        definition="Percentage of merged PRs with no other merged PR within 14 days touching any of the same files.",
        interpretation="High durability suggests lasting impact; low durability may indicate quick follow-up rework.",
        category="quality",
        higher_is_better=True,
    ),
    MetricDefinition(
        key="post_merge_bug_issue_rate",
        name="Post-merge bug issue rate",
        definition="Bug-labeled issues opened after merge that reference the contributor's merged PRs, divided by total merged PRs.",
        interpretation="Lower is better. Ratio of regressions tied to shipped PRs.",
        category="quality",
        higher_is_better=False,
    ),
    MetricDefinition(
        key="pr_acceptance_rate",
        name="PR acceptance rate",
        definition="Percentage of merged PRs accepted without any CHANGES_REQUESTED review before merge.",
        interpretation="Higher rates show PRs align with standards on first pass.",
        category="quality",
        higher_is_better=True,
    ),
    MetricDefinition(
        key="code_reviews",
        name="Code reviews",
        definition="Count of code reviews given by the contributor on other people's PRs.",
        interpretation="Measures mentorship and knowledge sharing through review participation.",
        category="collaboration",
        higher_is_better=True,
    ),
    MetricDefinition(
        key="issues_closed",
        name="Issues closed",
        definition="Issues closed via the contributor's merged PRs or directly resolved by the contributor.",
        interpretation="Shows follow-through and commitment to unblocking the team.",
        category="collaboration",
        higher_is_better=True,
    ),
    MetricDefinition(
        key="peer_comment_volume",
        name="Peer comment volume",
        definition="Comments left by the contributor on other people's PRs and issues.",
        interpretation="Indicates active participation in peer feedback loops.",
        category="collaboration",
        higher_is_better=True,
    ),
    MetricDefinition(
        key="review_responsiveness",
        name="Review responsiveness",
        definition="Median hours from first review feedback on the contributor's PR to their next comment on that PR.",
        interpretation="Lower is better. Measures responsiveness to code review on own PRs.",
        category="collaboration",
        higher_is_better=False,
    ),
]

CATEGORY_DEFINITIONS = {
    "quantity": {
        "name": "Quantity",
        "definition": "Volume of code shipped, issues raised, and pull requests created.",
        "interpretation": "Higher scores reflect greater output and participation in the measurement window.",
    },
    "quality": {
        "name": "Quality",
        "definition": "Stability and durability of merged work, bug follow-ups, and review acceptance.",
        "interpretation": "Higher scores reflect durable, low-revert, low-bug work accepted on first pass.",
    },
    "collaboration": {
        "name": "Collaboration",
        "definition": "Reviews, issue resolution, peer comments, and review responsiveness.",
        "interpretation": "Higher scores reflect active mentorship, follow-through, and timely review loops.",
    },
    "overall": {
        "name": "Overall",
        "definition": "Equal-weighted combination of normalized Quantity, Quality, and Collaboration scores.",
        "interpretation": "Composite impact score where 50 represents an average contributor across all categories.",
    },
}

METRICS_BY_KEY = {m.key: m for m in METRIC_DEFINITIONS}
