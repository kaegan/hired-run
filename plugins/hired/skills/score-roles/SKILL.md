---
name: score-roles
description: >
  Score job postings against the user's own rubric and write the score and a short
  summary to their Notion board. Trigger when the user says "score these roles", "score
  this job", "how's the fit", "rate this posting", when a scheduled hired.run scoring run
  fires, or when new records need evaluating.
metadata:
  version: "0.3.0"
---

# Score roles

Score each posting against the rubric the user wrote during setup, write a tier and a
short summary to Notion.

The rubric lives on the **Pipeline Config** page in Notion. It is the only source of
scoring judgment. Do not add dimensions, apply general assumptions about what makes a job
good, or import preferences from anywhere else. If the rubric does not cover something,
say so in the summary and score it neutral. A scorer that quietly substitutes its own
taste is worse than no scorer, because the user cannot tell it happened.

## Step 0 - Load the rubric and the experience profile

Read the Pipeline Config page in full: Profile, Rubric, Field Map, Settings. If it does
not exist, stop and tell the user to run setup.

Pay attention to the calibration examples saved in the rubric. They are anchors. If your
score for a new role would be inconsistent with how those two were scored, your score is
the thing that is wrong.

Then read the **Experience** child page, if it exists. It holds what the load-experience
skill extracted from the user's resume and cover letters: their roles, scope, proof
points, domains, and gaps. If there is no Experience page, use the proof points on the
Profile instead and score exactly as you otherwise would. A missing profile is not a
penalty and is not worth a line in the report.

**The rubric decides what matters. The experience profile only says what is true about
the user.** Keeping those two apart is what makes a resume safe to feed into scoring:

- Experience changes how strongly a role matches a dimension the rubric already names. It
  never adds a dimension, never creates or relaxes a hard filter, never edits the tier
  definitions or the expected distribution, and never overrides standout logic.
- Never read a preference out of a resume. It records where someone has been, not where
  they want to go. Four fintech roles is not a stated interest in fintech; only the rubric
  states interests.
- A cover letter's enthusiasm for one company is not a company signal for the tier list.
- Where the rubric and the profile disagree about a fact - the rubric assumes eight years
  of experience and the resume shows five - apply the rubric's rules to the resume's
  facts, and say so in the summary. Do not quietly pick one and move on.

## Step 1 - Build the queue

Query the board for records with a job description and no `fit_score`, using the data
source ID from the field map. Cap at the configured batch size (default 20).

If a record has no job description, skip it and note it. Run the fetch-jd skill first if
the user wants those filled in. Scoring from an alert email teaser is guessing.

## Step 2 - Score

Score the whole batch before writing anything. Batch scoring lets you calibrate roles
against each other, which is most of what makes a set of scores useful. A score is a
ranking signal, not an absolute measurement.

For each role, work through the rubric in this order:

1. **Hard filters.** If a role fails one, apply the cap the rubric specifies and stop
   evaluating the rest. Say which filter it failed in the summary. Do not soften a hard
   filter because the role is otherwise attractive. That is the entire point of a filter.
2. **Standout logic**, if the rubric has any. Determine which standout dimensions the role
   hits and apply the floor or boost the rubric specifies. Name the dimensions it hit in
   the summary.
3. **Dimensions.** Evaluate each one described in the rubric, using the strong and weak
   signals the user gave, and the evidence pass below. Weigh according to what they said
   matters most.
4. **Company signals** and the tier list, if there is one.
5. **Compensation**, exactly as the rubric says to handle it. If the user said a high
   salary should never raise a score, it never raises a score.

### The evidence pass

For each dimension the rubric names, find the strongest thing in the experience profile
that the user could actually say out loud in an interview about this posting, and the
requirements in this posting that nothing in the profile supports. Both halves matter: a
dimension the user clears easily and a dimension they clear on paper only are not the
same role, and only the evidence pass can tell them apart.

Rules that keep this from going wrong:

- **Match on substance, not vocabulary.** A posting asking for marketplace liquidity
  experience is answered by someone who ran supply acquisition for a two-sided market,
  whatever words their resume used. This is not keyword matching, and a scorer that
  rewards shared jargon will rank the postings written in the user's dialect above the
  jobs they should actually take.
- **Deep beats adjacent beats thin.** The profile separates domains it has real shipping
  history in from ones it touched once. Respect that separation: one project is evidence
  of exposure, not of depth, and scoring it as depth is how a Medium becomes a false High.
- **A gap only moves the score where the rubric named that dimension.** A posting can want
  something the user has never done, and if the rubric never said it cared, it is context
  for the summary and nothing more. The rubric decides what counts as a miss.
- **Seniority and scope come from the profile, not the summary line.** If the rubric has a
  seniority or scope dimension, the roles and team sizes on the Experience page are the
  answer, not what the user called themselves during setup.
- **Never infer a new filter from a gap.** No experience in an industry is not a hard
  filter against that industry. Only the rubric writes filters.

If there is no Experience page, run this pass against the Profile proof points. It is a
shorter pass with the same rules.

Then pick the tier: **Very High, High, Medium, Low, Very Low**, using the user's own tier
definitions and expected distribution. If most of a batch is landing High, you are not
discriminating and the batch is not that good. Re-read the tier definitions and tighten.

## Step 3 - Write the summary

Two to four sentences on the Notion page body, under a `## Score Summary` heading:

- Lead with the single strongest fit signal, stated specifically, and where there is an
  experience profile, cite the evidence behind it. "Ten years of billing and subscription
  work maps directly to the monetization scope here" is useful. "Good fit for the role" is
  noise, and so is "strong experience match" with nothing named.
- Name the real gaps: the one or two things this posting asks for that nothing in their
  background supports. A summary with no gaps in it is not being read carefully.
- Never cite evidence that is not on the Experience page or the Profile. A summary that
  credits the user with work they have not done is worse than a wrong tier, because they
  will find out in the interview rather than on the board.
- Note location, salary, or seniority context worth knowing at a glance.
- If the rubric has standout logic, name which dimensions the role hit.
- End with the action the tier implies, in the user's own vocabulary from the rubric
  (tailor a full application, send a generic one, watch, ignore).

Write the summary so the user can decide without opening the posting. That is the job.

## Step 4 - Write to Notion

Per record:

1. Set `fit_score` to the tier, using the exact option spelling from the field map.
2. Set the page icon by tier, if the board uses icons:
   Very High `document_purple.svg`, High `document_green.svg`, Medium
   `document_yellow.svg`, Low `document_orange.svg`, Very Low `document_red.svg`, all
   under `https://www.notion.so/icons/`.
3. Append the Score Summary to the page body. Do not overwrite existing body content.

If a field in the map is marked absent, skip it rather than creating it.

## Step 5 - Report

List every role scored with company, title, tier, and a one-line reason. Group by tier,
highest first. Then note anything skipped for a missing description, anything left in the
queue past the cap, and any errors.

If the batch produced no High or Very High roles, say that plainly in one line. It is a
real result, and padding it obscures the signal on the days when there is one.

## Step 6 - Post to Slack

If the Pipeline Config `## Slack` section says `enabled: true`, call the notify-slack
skill with the roles from this batch whose tier is in the configured `post_tiers`, plus
any errors from this run and from the fetch-jd run that fed it (fetch-jd has no Slack post
of its own - its failures ride along on this one). If Slack is not enabled, skip this step
silently.

A failed or skipped Slack post never changes the chat report above.

## Scoring a single role on request

When the user pastes a URL or a description and asks how it scores, run the same rubric
and the same evidence pass, and give them the tier, the dimension-by-dimension reasoning,
the evidence behind each one, and the summary in chat.
Only write to Notion if a record for it exists or they ask you to create one.

## When the scores feel wrong

If the user pushes back on a score, do not just adjust that one record. Find what
produced it and fix that, then offer to rescore. Two different things can be wrong:

- **A judgment is wrong** - the score weighed something they do not care about, or missed
  something they do. That is the rubric. Fix the rule.
- **A fact is wrong** - the score credited them with scope they never had, or missed
  experience they do have. That is the Experience page. Correct it there, or re-run
  load-experience if the resume has moved on since it was loaded.

Getting this distinction right matters more than either fix. Editing the rubric to work
around a stale fact leaves a rule that misfires on every future role. A rubric that gets
corrected a handful of times in the first two weeks becomes genuinely useful. One that is
never corrected is being ignored.
