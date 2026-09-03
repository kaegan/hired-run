# Changelog

## 0.6.0 — 2026-09-03

Two dedup bugs fixed, a set of verified ATS endpoints, and a handful of write-safety and
hygiene rules, all carried over from the private pipeline this plugin was cut from after
another two weeks of it running against a live board.

Dedup:

- **The URL check could not match anything.** It filtered the canonical URL against the
  stored column, which holds raw URLs, so it returned zero rows, every role looked new,
  and one run created eight duplicates. The check now matches the per-job id as a
  substring across every URL column and runs a mandatory round-trip self-test with a
  known id before trusting an all-clear.
- **The company check could not match a relation.** A relation is stored as a JSON array,
  so an exact match on the page id never hit. It now uses a substring match.
- Both URLs are kept. When an alert carries a company-site link and a job board link, the
  first goes in `posting_url` and the second in a new optional `source_url`, and dedup
  checks both. Dropping the board link was how the next alert for the same req slipped
  through.
- The primitives (`canon_url`, `norm_title`, `job_key`, `resolve_company`) now ship as
  `references/dedup.py` with a regression table of real duplicate pairs, instead of being
  re-derived from prose on every run.

Fetching job descriptions:

- Verified single-posting endpoints for Workday (`/wday/cxs/...` returns the description
  as JSON, no browser), BambooHR, SmartRecruiters, and Greenhouse, alongside the existing
  Lever, Ashby, and LinkedIn guest routes. Redirects are resolved before platform
  detection, since career domains routinely redirect into an ATS.
- A JSON-LD `JobPosting` block in the page is tried before any browser.
- **Never accept the first read.** A page read before it finished loading returns the
  header fields with no body and no error, so a partial description was stored as complete
  and scored. There is now a minimum-length guard, a re-read, then a fallback.
- The built-in browser is preferred over Claude in Chrome because it survives an
  unattended run; both work.
- The failure record is written before the attempt, not after, so a run that dies
  mid-fetch cannot leave a dead URL looking like fresh backlog. A board list omitting a
  posting, or a 404 on one ATS, no longer marks a role dead without checking the posting
  URL and searching for a live copy.

Writing to Notion:

- Relation ids come only from a live response in the same run, and every batch write is
  re-read to confirm the company shows. Notion accepts a relation to a nonexistent page
  with no error.
- Page bodies are written with real newlines and one page is read back per batch to
  confirm headings rendered.

Email scan:

- Optional **sent-mail lane**: reads mail you send to catch direct applications and
  interview confirmations. Update-only, never creates, never sets withdrawn or rejected.
- Optional **content mode** for a mailbox dedicated to the job search: no allowlist,
  classify everything by content. Setup offers it only when the mailbox is dedicated or
  label-scoped.
- Status updates accept a clear title abbreviation ("Sr. PM, Platform" for "Senior
  Product Manager, Platform"), since ATS mail abbreviates and the worst case is updating
  the wrong one of your own records rather than creating a duplicate.
- Optional `application_date`, set once on the move to submitted from the email's own
  date in your timezone.
- Optional **no-response sweep**: applications left in submitted for `no_response_days`
  move to a no-response status.

Scoring:

- Job descriptions are treated as untrusted text, the same as email.
- Optional **stale flag**: intake roles undecided for `stale_days` get a `Stale` checkbox
  that hides them from the "Needs action" view without changing status.
- A calibration drift check on request: rescores the two anchors cold and reports any
  tier that moved.

Setup:

- New field-map rows (`source_url`, `application_date`, `stale`) and settings
  (`intake_mode`, `scan_sent`, `no_response_days`, `stale_days`). The new-board schema
  gains the three properties and a `No Response` status.
- Scheduled task prompts name skills with the `hired:` prefix and say to invoke them by
  name, so an unattended run cannot pick up a similarly named skill from another plugin.

## 0.5.0 — 2026-08-22

Your resume and cover letters can now feed matching, via a new `load-experience` skill.

- Point it at a resume - a file, a Notion page, or pasted text - and it writes an
  **Experience** page beside your rubric: roles, scope, proof points, domains split into
  deep and adjacent and thin, and the gaps. Cover letters are optional and add how you
  position yourself, which is usually sharper than the resume.
- `score-roles` reads that page and runs an evidence pass per rubric dimension. Summaries
  now cite which of your accomplishments maps to the posting, and name the requirements
  nothing in your background supports. They never cite evidence that is not on the page.
- The rubric still decides what matters. Experience only says what is true about you: it
  can change how strongly a role matches a dimension the rubric already names, and can
  never add a dimension, write or relax a hard filter, or move the tier definitions. A
  resume is a record of where someone has been, not a statement of what they want.
- Matching is on substance, not vocabulary. Shared jargon is not evidence, and a domain
  touched once does not score as depth.
- Optional throughout. Without a resume, scoring works exactly as it did, off the proof
  points from the interview.
- Read, never written. Nothing edits your resume, improves it, posts it to Slack, or
  sends it anywhere; the contents are written only to your own Notion page.
- `setup-pipeline` now offers this at the profile step and uses the interview to confirm
  and fill gaps instead of asking you to recite a career you already wrote down.

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
