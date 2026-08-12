---
name: setup-pipeline
description: >
  First-run setup for the hired-exe job search pipeline. Trigger when the user says
  "set up my job search pipeline", "set up hired-exe", "initialize the job pipeline",
  "configure my job search", or on first install. Interviews the user to build their
  profile and their own scoring rubric, connects to an existing Notion board or creates
  a new one, and schedules the recurring scans.
metadata:
  version: "0.2.1"
---

# Setup Pipeline

Run this once. It produces a **Pipeline Config** page in Notion that every other skill in
this plugin reads at the start of each run. Nothing else in the plugin works until this
page exists.

Do the steps in order. Confirm each one with the user before moving on. Use
AskUserQuestion for anything with a small set of sensible answers, and plain questions
for open-ended ones.

## Step 0 - Check connectors

1. **Notion** - required. Try a `notion-search` call. If it fails, tell the user to add
   the Notion connector in their Claude settings and stop here.
2. **Gmail** - required for email scanning. Try listing labels or a one-message search.
   If it fails, tell them to add the Gmail connector and stop here.
3. **Chrome browser tools** - optional. If unavailable, the pipeline still works: JD
   fetching falls back to public ATS APIs and to whatever the alert email contained.

Do not invent a workaround for a missing required connector. Stop and say what is missing.

## Step 1 - Profile interview

Ask, in this order. Keep it conversational, one group at a time.

**Identity and logistics**

- Name.
- Where they live (city, country) and timezone.
- Location rules: remote only, hybrid OK, in-person OK, willing to relocate and where.
  Ask whether location is a **hard filter** (a role that fails it is dead regardless of
  how good it is) or a soft preference. Most people say hard. Record which.
- Work authorization constraints, if any (e.g. "can only work for Canadian entities").

**Target roles**

- Job titles they are going after. Get 3 to 6, including the ones they would take a
  title step down for.
- Titles or levels that are an automatic no.
- Years of relevant experience and the scope they have carried (team size, budget, org).

**Domains**

- Industries or product categories they know well enough to be credible in.
- Categories they are curious about but have no track record in. These score differently
  from the first list, so keep them separate.
- Categories they actively do not want, and why. The why matters, because it usually
  reveals a rule rather than a single exclusion.

**Proof points**

- 4 to 6 of their strongest, most specific accomplishments. Push for numbers. "Grew
  activation 25% by rebuilding onboarding" is usable; "improved the product" is not.
  These are what the scorer compares a job description against.

**Deal breakers**

- Anything that should force the lowest score no matter what else is true. Common ones:
  relocation requirements, on-site five days, salary below a floor, specific companies or
  industries, security clearance requirements.

**Compensation**

- Floor, target, and currency. Ask explicitly whether a high salary should ever raise a
  score, or only whether a low one should lower it. Most people want the second. Record
  the answer, because the scorer needs it.

Do not fill in any of these from assumption or from another user's setup. If they skip a
question, write "not specified" and let the scorer treat that dimension as neutral.

## Step 2 - Rubric interview

This is the part that makes scoring useful, so do not rush it. Work through
`references/rubric-interview.md`, which contains the full question set and explains what
each answer changes.

**Start by asking for real postings.** Before the questions, ask them to paste 3 to 5 job
postings, URLs or text, that represent what they are actually going after. Then ask for
one or two they looked at and passed on. Read all of them.

Do this first because what people describe and what they apply to are different, and the
postings are the more reliable signal. Named patterns can be confirmed against evidence
instead of taken on faith. Use the postings to:

- pull out the dimensions that actually vary across them, and raise anything they did not
  mention ("all five of these are Series B or earlier, does company stage matter to you?")
- test claimed preferences against the evidence, and ask about the mismatch when a stated
  must-have is missing from every example
- work out what separates the ones they liked from the ones they passed on, which is
  usually the sharpest input to the rubric
- seed the calibration anchors in step 6 of the interview

If they cannot produce examples, the questions alone still work. Say that the rubric will
need more correction in the first two weeks, and move on.

The output is a filled-in rubric with these parts:

1. **Dimensions** the user cares about, each with a short description of what pushes a
   role up and what pushes it down on that dimension.
2. **Hard filters** that cap a score regardless of everything else.
3. **Standout logic**, if they have any: the combination of things that makes them an
   unusual candidate rather than a merely qualified one, and how much a role hitting that
   combination should be boosted. Many people have this and have never written it down.
   Ask about interests, side projects, and unusual background, not just work history.
4. **Company signals** they care about (stage, size, funding, remote culture, glassdoor
   patterns, whatever they name) and any tier list they want to maintain.
5. **Tier definitions**: what Very High, High, Medium, Low, and Very Low each mean in
   their words, plus roughly what share of roles they expect in each. Calibration matters
   more than the words. If everything scores High, the score is useless.

Read the filled rubric back to them before saving. Then run a calibration check: ask them
for two roles they have seen recently, one they would definitely apply to and one they
would definitely skip, score both against the draft rubric, and show your reasoning. If
the scores do not match their gut, fix the rubric, not the scores. Repeat once if needed.

## Step 3 - Notion: existing board or new one

Ask directly: **"Do you already have a Notion board or database you track applications
in, or should I create one?"**

### Branch A - they have one

1. Ask them to paste the URL of the database.
2. Fetch it and read its schema: every property, its exact name, and its type. Property
   names are case and punctuation sensitive, and a Status property is not the same type
   as a Select property. Get this exactly right.
3. Build a **field map** from the canonical names the plugin uses to their property
   names. Canonical fields:

   | Canonical | Type needed | Required | Used by |
   |---|---|---|---|
   | `job_title` | Title | yes | all |
   | `company` | Relation, or Text if they have no companies DB | yes | all |
   | `status` | Status or Select | yes | email-scan |
   | `posting_url` | URL | yes | dedup, fetch-jd |
   | `fit_score` | Select | yes | score-roles |
   | `location` | Text | no | scoring |
   | `flexibility` | Select | no | scoring |
   | `salary_range` | Text | no | scoring |
   | `source` | Select | no | reporting |
   | `date_added` | Date | no | reporting |
   | `last_seen` | Date | recommended | repost detection |
   | `times_seen` | Number | recommended | repost detection |

4. For anything missing, ask whether to add it. Explain the cost of skipping: without
   `last_seen` and `times_seen` the pipeline cannot tell a still-open posting from a
   genuine repost, so it will either create duplicates or skip real reopenings. Without
   `fit_score` there is nowhere to write the score. Add the properties they approve, and
   record the rest as absent so the other skills degrade instead of erroring.
5. For `status` and `fit_score`, read their existing option values and map the pipeline's
   states onto them rather than adding new ones. The pipeline needs an intake state (a
   new unreviewed role), plus states meaning submitted, screening, interviewing,
   rejected, and offer. If their board uses different words, use their words everywhere.
   Never add an option to a Status property without asking.
6. Ask whether they have a separate Companies database. If yes, capture its ID and its
   title property. If no, set `company` to a text field and skip company dedup.

**Never rename, retype, or delete an existing property.** Their board is their board. The
plugin adapts to it, not the other way around.

### Branch B - create one

Create a top level page called **Job Search**, then build the databases under it exactly
as specified in `references/notion-schema.md`. Order matters: create Companies first,
capture its data source ID, then create Applications with the Company relation pointing
at it. Then create the views listed in the schema file.

Confirm the created structure with links before continuing.

## Step 4 - Inbox settings

Tell the user up front, in plain terms, what the pipeline will and will not do with their
mail. Do not bury this:

> It only reads. It never sends, replies to, forwards, deletes, archives, or labels
> anything. If an email needs an answer, it shows up in the report and you answer it.

Then set the scope. There are two lanes and they are configured separately.

**Lane 1, new roles.** Only an allowlist of senders can create records. Ask which job
alert emails they actually get. LinkedIn is the usual answer and is often the only one.
Others worth naming: Indeed, Wellfound, Glassdoor, Otta, Hacker News hiring digests,
industry-specific boards, and any company career page alerts they have subscribed to.
Save as `alert_senders` in the config.

Say clearly what the tradeoff is: nothing outside this list will ever create a record, and
a missing source produces no error. Then tell them the scan reports unfamiliar
alert-looking senders every run so they can add them, and that adding one is a one line
edit to the config page.

**Lane 2, status updates.** Explain that this lane is deliberately wider, because
rejections and interview invitations arrive from whatever system the employer uses and the
sending domains are unpredictable. It is safe to be wide here because a status email can
only ever update a record already on their board. It cannot create anything.

Ask whether they want to add any specific recruiters or agencies they are working with.

**Which mailbox.** Confirm the address. If it is their main personal inbox, that is fine
under this design, since both lanes are scoped queries rather than a full inbox read. If
they would rather it never touched their personal mail at all, suggest routing job alerts
to a dedicated address or Gmail label and setting `gmail_query` to that label.

Record in the config: `alert_senders`, any extra recruiter senders, `gmail_query` if they
want one, and the scan window (default 2 days, which tolerates a missed run).

## Step 5 - Save the config

Create a page called **Pipeline Config** as a child of the Job Search page (Branch B) or
alongside their existing board (Branch A). Write these sections, in this order:

- `## Profile` - everything from Step 1, as prose and bullets. Readable, not YAML.
- `## Rubric` - the full rubric from Step 2, including tier definitions and calibration
  notes.
- `## Field Map` - a table of canonical name, their property name, property type, and
  present/absent. Include the database and **data source** IDs, and the Companies DB ID
  if there is one.
- `## Settings` - `alert_senders` (the lane 1 allowlist), any extra recruiter senders for
  lane 2, `gmail_query` if set, scan window, batch caps (default: 20 roles scored per run,
  15 JD fetches per run), and the status and fit score option values in their exact
  spelling.

Also write a one line note at the top of Settings: **Gmail access is read only. This
pipeline never sends, replies, deletes, or labels mail.** It belongs in the config where
they will see it again, not just in a setup conversation they will forget.

Tell the user this page is the single source of truth: editing the rubric there changes
scoring on the next run, with no need to touch the plugin. Also tell them where it is,
because they will want to tune it in week two.

If they want a local copy as well, offer to save the same content as a markdown file in a
folder they choose. The Notion page is what the skills read.

## Step 6 - Schedule the runs

Use the scheduled task tools (`create_trigger`), not local cron. Create two tasks:

**Task 1: hired-exe scan**
```
Name: hired-exe scan
Schedule: every 2 hours, or daily at a time they pick
Prompt: Run the hired-exe email scan. Use the email-scan skill. Read the Pipeline Config
page in Notion first for the field map, inbox settings, and status values.
```

**Task 2: hired-exe score**
```
Name: hired-exe score
Schedule: daily, an hour after the scan they care most about
Prompt: Run hired-exe scoring. Use the fetch-jd skill to fill in missing job descriptions,
then the score-roles skill to score everything unscored. Read the Pipeline Config page in
Notion first. Report what you scored and anything you could not fetch.
```

Ask about frequency rather than assuming. Someone actively searching wants the scan every
couple of hours; someone passively watching wants it daily. Mention that each run costs
tokens, so hourly on a quiet inbox is mostly waste.

## Step 7 - Prove it works

Do not end setup on a promise. Run the scan once, live, in front of them:

1. Run `email-scan` over the last 7 days.
2. Run `fetch-jd` and `score-roles` on whatever it found.
3. Show the results: what was created, what scored where, what failed.

Then ask whether the scores match their judgment. If they do not, go back to the rubric.
This first calibration pass is the highest value part of setup.

Close with: the Notion links, what got scheduled and when it next runs, how to trigger a
scan manually ("check my email for new roles"), how to score a single URL ("score this
role: <url>"), and where to edit the rubric.
