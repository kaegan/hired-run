---
name: load-experience
description: >
  Read the user's resume and cover letters and turn them into an experience profile the
  scorer can cite as evidence. Trigger when the user says "use my resume", "here is my
  resume", "add my cover letter", "load my experience", "update my resume", or when setup
  reaches the profile step and the user has a resume to hand.
metadata:
  version: "0.1.0"
---

# Load experience

Read a resume and any cover letters the user points at, and write what they establish to
an **Experience** page in Notion, as a child of Pipeline Config. The score-roles skill
reads that page and cites it when it explains a fit.

Run this during setup, or any time afterwards when the resume changes. It is optional.
Without it the pipeline scores off the proof points from the setup interview, which works;
it is just thinner.

## The one rule

**A resume is evidence, not criteria.**

The rubric says what the user wants. The resume says what is true about them. These are
different things and the pipeline breaks the moment they get mixed up.

So: this skill records what the user has done, at what scope, in what domains, in their
own words. It does not infer a single preference from it. Someone who spent eight years
at agencies has not told you they want another agency. Someone whose resume is all
fintech has not told you they want fintech next - people leave, and the resume is the
record of where they were, not where they are going.

If reading the documents suggests a preference the rubric does not name, raise it as a
question for the user in Step 4. Never write it into the rubric yourself.

## What this skill will not do with the documents

State this to the user the first time you run, in one line, before you read anything:

> Your resume is **read, never written**. This skill never edits, rewrites, scores, or
> improves it, never attaches it to an application, and never sends it anywhere: the only
> place its contents are written is your own Notion page.

That is a commitment, not a description of the current implementation. Specifically:

- Never modify, move, rename, or delete the source file.
- Never write the document to anywhere except the Experience page in the user's own
  Notion, which is the same place their rubric already lives.
- Never post resume or cover letter contents to Slack, even when Slack is configured.
  notify-slack posts run results, and an experience profile is not a run result.
- Never send the documents anywhere, to anyone, for any reason - including to a job
  posting, a recruiter, or a form. This plugin does not apply to jobs and this skill does
  not change that.
- Never offer to improve the resume, rewrite a bullet, or optimize it for keywords. That
  is a different job than triage and it is not this plugin's job.

## Step 1 - Collect the documents

Ask for what you need and take only what is offered:

> "Point me at your resume - a file path, a Notion page, or just paste the text. If you
> have a cover letter or two you actually sent, those help as well."

Rules for collecting:

- **Only read what the user names.** Never search their disk, Drive, or Notion for
  documents that look like a resume. A file they did not point at is not a file they
  consented to.
- PDF, DOCX, Markdown, plain text, a Notion page, or pasted text are all fine. Use
  whatever document-reading skill is available for the format. If a format cannot be read,
  say so and ask them to paste the text instead of guessing at the contents.
- **Cover letters are optional and plural.** Two or three real ones for roles they wanted
  are worth more than a generic template. Ask which role each was for; a cover letter with
  no target role is much weaker evidence.
- If they have several resume versions, ask which one is current. Read one. A stale
  version mixed into the profile produces claims they can no longer make.

If they have nothing to hand, stop here and say the interview alone is fine. Do not press.

## Step 2 - Read for evidence

Read the whole document before writing anything. Pull out:

**From the resume**

- **Roles**: title, company, dates, and whether it was IC or management. Keep the exact
  titles; they matter when the rubric has a seniority dimension.
- **Scope**: team size, org size, budget, revenue owned, users, scale. Numbers wherever
  the resume gives them.
- **Accomplishments**: the specific, quantified ones. "Grew activation 25% by rebuilding
  onboarding" is evidence. "Responsible for the product roadmap" is a job description and
  proves nothing.
- **Domains**: industries, product surfaces, business models, customer types they have
  actually shipped in. Separate deep experience from a single project.
- **Skills and tools** they claim explicitly.
- **Trajectory**: seniority over time, and total years of relevant experience. Compute
  years from the dates rather than taking a summary line's word for it.
- **Education, credentials, languages, location and authorization** if stated.

**From the cover letters**

- **How they position themselves** - which two or three things they lead with when they
  want the job. This is usually sharper than anything the resume says.
- **Which accomplishments they reach for** under pressure. Those are the ones they can
  actually talk about.
- **Vocabulary** - the words they use for their own work. Scoring summaries read better in
  the user's language than in the job market's.
- **Standout angles** they claim: unusual combinations, outside interests, a reason they
  care about a particular kind of company.
- **Motivations they state**. Record these as *stated in a cover letter*, not as
  preferences. They are a lead for Step 4, not a rubric entry.

Do not embellish. Every line of the Experience page should be traceable to something the
user wrote. If the resume is vague about scope, the profile is vague about scope; that is
information the scorer needs, and inventing a number to fill the gap is the one failure
mode that makes this feature worse than not having it.

## Step 3 - Note what is missing or stale

Before writing, gather the things worth flagging:

- Employment gaps, or a current role with no end date that the dates suggest has ended.
- A resume that stops more than a year before today.
- Claims that conflict between the resume and a cover letter.
- Scope stated in one place and contradicted in another.

Bring these up as questions, not corrections. The user knows why the gap is there.

## Step 4 - Confirm with the user

Read back a compressed version: the roles, the years, the scope, the domains, and the
five or six accomplishments you would put in front of a scorer. Then ask three things:

1. **"Anything here that is out of date or that you would not claim in an interview?"**
   Drop whatever they name. A profile the user would not defend produces summaries they
   cannot use.
2. **"Anything missing that is not on the resume?"** Side projects, unpaid work, a domain
   they know from outside a job. Resumes are edited for a purpose and leave out things
   that matter here.
3. If reading the documents suggested a preference the rubric does not name, ask about it
   now, once, as a question: *"All three cover letters lead with developer tools. Should
   that be a dimension in your rubric, or is it just where you were looking?"* If they say
   yes, offer to add it to the rubric. If they say no, drop it and do not raise it again.

## Step 5 - Write the Experience page

Create a page called **Experience** as a child of the Pipeline Config page, using the
shape in `references/experience-template.md`. If it already exists, replace its contents
and note in the report what changed - this skill is meant to be re-run.

Then add one line under `## Profile` on the Pipeline Config page, if it is not already
there:

> Experience profile: see the **Experience** child page. Loaded from a resume on
> [date]. Re-run "use my resume" to refresh it.

Do not copy the resume verbatim onto the page. The profile is the extracted evidence, in
structured form. The user already has the resume.

Tell them where the page is and that it is theirs to edit: a correction there changes
scoring on the next run, exactly like the rubric.

## Step 6 - Offer a calibration rescore

Scoring changes once this page exists, so show them rather than telling them. Offer:

> "Want me to rescore the last handful of roles with this? You will see what changes."

If they say yes, run score-roles over the most recently scored records and show the before
and after. If a tier moves, name the evidence that moved it. If nothing moves, say that
plainly - it means the rubric was already carrying the weight, which is fine.

## Step 7 - Report

Say what was read (which files, how many cover letters), what the profile now contains in
one line per section, what you flagged as stale or missing, and anything the user chose to
drop. If a document could not be read, name it and why.

## Keeping it current

Resumes change. Say once, at the end of the first run: re-run this with "use my resume"
after any update, and the next scoring run picks it up. Do not remind them again - a
pipeline that nags about its own configuration gets ignored along with the nagging.
