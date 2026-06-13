Metrics Definition (use the data from the last 120 days)

Category 1: Quantity:

1. Code line changes:
Definition: Total number of lines written by a contributor across all commits, excluding any merge commits. Sum of all lines added and lines deleted across all non-merge commits authored by the contributor in the measurement window

Interpretation: Shows how productive a contributor is by raw output volume. Higher values indicate more code authored, but don't reflect 

2. Issues Opened:
Definition: Number of issues (bug reports, feature requests, discussions) opened by a contributor

Interpretation: Measures initiative and engagement in identifying problems or proposing improvements. Contributors who open more issues drive discussion and help shape the project roadmap, even if they don't implement the solutions.

	
3. PRs Created:
Definition: Total number of pull requests (open, merged) created by the contributor.
	
Interpretation: Tracks active contribution to the codebase. More PRs show consistent participation


Category 2: Quality:

1. Reverted commits
Definition: How often a contributor’s code is rolled back. Number of commits authored by the contributor that were later reverted via an explicit revert commit

Interpretation: Lower is better; fewer reverts mean code is more stable and well-tested before merge. Frequent reverts may signal rushed work, insufficient testing, or misalignment with project standards, requiring code review attention.

2. Effective Code Line Changes:
Definition: Percentage of lines added by the contributor in the given time window, that are still present in HEAD without being deleted or overwritten later (still present in the codebase at HEAD)

Interpretation: Indicates code longevity and fit. High retention means contributions have lasting impact; low retention may indicate quick fixes, temporary workarounds, or code that needed rework by others.

3. Issue rate:
Definition: Number of bug issues opened that reference or are linked to a contributor's merged PRs, divided by the contributor's total merged PRs.

Interpretation: Ratio of bugs introduced per PR merged. Lower is better, higher ratios indicate potential issues with code review depth or testing rigor, and may warrant pair-review or extended testing.

4. PR acceptance rate:
Definition: Percentage of a contributor’s merged PRs that were accepted without needing any corrections.

Interpretation: Reflects code quality at review time. Higher rates show PRs align with standards on first pass; lower rates suggest improvements needed in pre-submission testing, code style, or requirement clarity opportunities for coaching.

Category 3: Collaboration:

1. Code Reviews:
Definition: Count of code reviews (approvals, comments, change requests) given by the contributor on other people's PRs.

Interpretation: Measures mentorship and knowledge sharing. More reviews show active engagement in team growth and quality gates; low review counts may indicate siloed work or missed mentorship opportunities.
	
2. Issues closed:
Definition: Number of issues closed via PRs authored by the contributor, or issues directly assigned/resolved by the contributor.

Interpretation: Shows impact on project velocity and problem-solving. Closing issues (yours or others') demonstrates follow-through and commitment to unblocking the team, not just shipping new features.

3. Engagement in PR discussions and peer comments
Definition: Number of comments left by the contributor on other people's PRs and issues, plus response time to pull requests.

Interpretation: Indicates active participation in peer feedback loops and responsiveness to code review. Frequent, timely comments build team cohesion and catch issues early; silence may signal disengagement or bottlenecks in review cycles.
