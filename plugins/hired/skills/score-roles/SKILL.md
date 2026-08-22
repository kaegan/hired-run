---
name: score-roles
description: >
  Score job postings against the user's own rubric and write the score and a short
  summary to their Notion board. Trigger when the user says "score these roles", "score
  this job", "how's the fit", "rate this posting", when a scheduled hired.run scoring run
  fires, or when new records need evaluating.
metadata:
  version: "0.2.1"
---

# Score roles

Score each posting against the rubric the user wrote during setup, write a tier and a
short summary to Notion.

The rubric lives on the **Pipeline Config** page in Notion. It is the only source of
scoring judgment. Do not add dimensions, apply general assumptions about what makes a job
good, or import preferences from anywhere else. If the rubric does not cover something,
say so in the summary and score it neutral. A scorer that quietly substitutes its own
taste is worse than no scorer, because the user cannot tell it happened.

## Step 0 - Load the rubric

Read the Pipeline Config page in full: Profile, Rubric, Field Map, Settings. If it does
not exist, stop and tell the user to run setup.

Pay attention to the calibration examples saved in the rubric. They are anchors. If your
score for a new role would be inconsistent with how those two were scored, your score is
the thing that is wrong.

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
   signals the user gave. Weigh according to what they said matters most.
4. **Company signals** and the tier list, if there is one.
5. **Compensation**, exactly as the rubric says to handle it. If the user said a high
   salary should never raise a score, it never raises a score.

Then pick the tier: **Very High, High, Medium, Low, Very Low**, using the user's own tier
definitions and expected distribution. If most of a batch is landing High, you are not
discriminating and the batch is not that good. Re-read the tier definitions and tighten.

## Step 3 - Write the summary

Two to four sentences on the Notion page body, under a `## Score Summary` heading:

- Lead with the single strongest fit signal, stated specifically. "Ten years of billing
  and subscription work maps directly to the monetization scope here" is useful. "Good
  fit for the role" is noise.
- Name the real gaps. A summary with no gaps in it is not being read carefully.
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

## Scoring a single role on request

When the user pastes a URL or a description and asks how it scores, run the same rubric
and give them the tier, the dimension-by-dimension reasoning, and the summary in chat.
Only write to Notion if a record for it exists or they ask you to create one.

## When the scores feel wrong

If the user pushes back on a score, do not just adjust that one record. Find the rule in
the rubric that produced it and fix the rule, then offer to rescore. A rubric that gets
corrected a handful of times in the first two weeks becomes genuinely useful. One that is
never corrected is being ignored.
