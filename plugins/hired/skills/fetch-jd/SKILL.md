---
name: fetch-jd
description: >
  Fetch the full job description for postings that have a URL but no description yet, and
  store it as a subpage on the Notion record. Trigger when the user says "fetch the job
  descriptions", "get the JDs", "fill in the postings", when scoring needs a description
  that is missing, or as part of a scheduled hired.run scoring run.
metadata:
  version: "0.2.1"
---

# Fetch job description

Alert emails contain a teaser, not a job description. Scoring on a teaser produces
confident nonsense. This skill fills the gap.

It is **API first**. Most postings live on one of a handful of applicant tracking systems,
all of which expose a public JSON endpoint that returns the full description over a plain
`curl`, with no browser, no auth, and no rendering. Use those first. They are faster, more
reliable, and cheaper than driving a browser, and they work in a headless scheduled run
where a browser may not be available.

## Step 0 - Read the config and build the queue

Read the Pipeline Config page for the field map and batch caps.

Query the board for records that have a `posting_url` and no job description subpage.
Cap the run at the configured limit (default 15). Leftovers stay in the queue for the next
run, which is fine. Say how many you skipped.

## Step 1 - Detect the platform

Match the URL host against these. The token is the company identifier in the URL path.

| Platform | URL looks like | JSON endpoint |
|---|---|---|
| Greenhouse | `boards.greenhouse.io/{token}/jobs/{id}` | `https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true` |
| Lever | `jobs.lever.co/{token}/{id}` | `https://api.lever.co/v0/postings/{token}?mode=json` |
| Ashby | `jobs.ashbyhq.com/{token}/{id}` | `https://api.ashbyhq.com/posting-api/job-board/{token}?includeCompensation=true` |
| SmartRecruiters | `careers.smartrecruiters.com/{token}` | `https://api.smartrecruiters.com/v1/companies/{token}/postings` |
| LinkedIn | `linkedin.com/jobs/view/{id}` | `https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{id}` |

The LinkedIn guest endpoint is worth calling out: it returns the full description as HTML
over an unauthenticated `curl`. It defeats every problem the rendered LinkedIn page
creates, including postings behind a login wall and listings with a hidden employer. Try
it before anything else on any LinkedIn URL.

Fetch with `curl` from bash, with a timeout:

```
curl -s --max-time 25 "<endpoint>"
```

Use `curl` rather than a web fetch tool. Fetch tools are frequently proxy blocked on
applicant tracking domains, and the failure looks like an empty page rather than an error.

For the board-wide endpoints (Greenhouse, Lever, Ashby, SmartRecruiters), the response
contains every open role at that company. Match the one you want by job ID from the URL,
falling back to an exact title match.

## Step 2 - Fall back

In order, stopping at the first that works:

1. The platform JSON endpoint above.
2. A plain `curl` of the posting URL itself. Server rendered career pages, which includes
   most Greenhouse, Lever, and Ashby pages, return usable HTML. Strip tags and keep the
   text.
3. Browser tools, if available in this session. Navigate, wait a few seconds, read the
   page text. Workday and other heavy single page apps need roughly 8 seconds and
   sometimes a second attempt. If browser tools are not available, skip straight to 4.
4. Give up on this record for now. Record the failure and move on.

Never spend more than a few attempts on one posting. A stuck fetch on one record should
not consume the run.

## Step 3 - Track failures so dead URLs stop costing you

Keep a small failure record per posting: the URL, how many attempts, and **which
technique was used each time**.

After three failed attempts with the same technique, stop retrying that record on future
runs. Expired postings are common and a permanent retry loop wastes the entire budget on
records that will never resolve.

The technique detail matters more than the count. An attempt counter that does not record
what was tried turns a tooling limitation into a permanent verdict about the data. When a
better technique becomes available, reset the counter and retry everything marked dead.
That exact situation has happened: a batch of postings written off as dead after repeated
browser failures were all live, and all of them resolved on the first try through a JSON
endpoint.

Store the failure record wherever the config says, or as a short section on the Pipeline
Config page if no location is set.

## Step 4 - Write it to Notion

Create a child page titled **Job Description** inside the Application record, containing
the full text. Keep the structure (responsibilities, requirements, and so on) rather than
flattening it, since the scorer reads these sections.

Do not put the description in the parent page body. It buries everything else and makes
the board unpleasant to use.

While you have the text, backfill any structured fields that are unambiguously stated in
it and empty on the record: location, flexibility, salary range. Only when the description
states it plainly. Do not infer a salary from a job title, and do not search elsewhere
for one.

## Step 5 - Report

Output: attempted, succeeded (by platform), failed with the reason, records newly marked
dead, and how many were left in the queue for the next run.

Say explicitly when a cap truncated the run. A silent truncation reads as "everything is
handled" when it is not.
