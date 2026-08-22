# Changelog

## 0.4.0 — 2026-08-22

Added optional Slack notifications, via a new `notify-slack` skill.

- Off by default. Turn it on during setup and pick a channel, which of your own rubric
  tiers should post, whether status changes post, and whether to be @mentioned (offers
  and interview invitations only, by default).
- Outbound only. It never reads a channel, never replies, and never treats anything
  written in Slack as an instruction back to the pipeline.
- Silent on a quiet run - nothing posts unless a run actually produced a high-fit role, a
  status change, or something needing a reply. A run with only errors and nothing else
  posts one line, not a full incident report.
- `email-scan` and `score-roles` each gained a final step that hands their results to
  `notify-slack` when it is configured. Their own chat report is unchanged either way.

## 0.3.0 — 2026-08-21

Renamed. The plugin is now `hired` and the marketplace is `hired-run`, matching the site
at [hired.run](https://hired.run). Previously `hired-exe@get-hired-run`. GitHub redirects
the old repo URL; existing installs should remove the old marketplace and re-add
`kaegan/hired-run`.

Dedup rewrite, based on a month of the pipeline running against a real board:

- A specific posting URL now matches decisively on its own. Requiring the title to also
  match split one req into two records whenever an employer renamed a live posting.
- ATS host aliases fold to one canonical form (`boards.greenhouse.io` =
  `job-boards.greenhouse.io`, `hire.lever.co` = `jobs.lever.co`), and job-id query
  parameters like `gh_jid` are kept only when the path carries no job id of its own.
- Title matching is now exact equality after normalization, with the normalization rules
  spelled out. "Minor rename" fuzzy matching guessed wrong too often; a near match now
  creates the record and flags it for review instead.
- The repost matrix is retired. A company-plus-title match now suppresses unconditionally,
  with every suppression reported — split into resurfaced terminal hits and live
  duplicates — instead of silently branching on status and recency. A different URL is not
  evidence of a reopening; cross-posts and reposted reqs carry fresh URLs every time.
- A scan never reopens a record. Only a human moves a record back to intake.

## 0.2.1 — 2026-08-12

First release under the marketplace. Rework of the original plugin:

- Configuration moved out of YAML files into a Pipeline Config page in Notion. Editing the
  rubric there changes scoring on the next run; nothing to configure by hand.
- The rubric is now built entirely through the setup interview — starting from 3 to 5 real
  postings you want plus 1 or 2 you passed on — instead of a fixed set of scoring
  dimensions with a custom bolt-on.
- Job descriptions are fetched API-first through public ATS JSON endpoints (Greenhouse,
  Lever, Ashby, SmartRecruiters, LinkedIn guest), with `curl` and then a browser as
  fallbacks. The browser is now optional.
- Skills reorganized to `setup-pipeline`, `email-scan`, `fetch-jd`, `score-roles`.

## 0.2.0 — 2026-06-22

Initial open-source packaging of the personal pipeline, as `hired-exe`: four skills
(`setup-pipeline`, `ingest-from-email`, `ingest-role`, `score-role`), YAML configuration,
browser-first JD fetching.
