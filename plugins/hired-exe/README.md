# hired-exe

A job search pipeline for Claude Cowork. It reads your inbox for new roles and
application updates, fetches the actual job description, scores each role against a rubric
**you** write during setup, and keeps it all on a Notion board.

The point is not automation for its own sake. It is that every morning there is one view,
sorted, with a two-sentence reason attached to each role, so deciding what to apply to
takes five minutes instead of an hour of tab management.

## What you need

- **Claude with Cowork** (desktop app recommended)
- **Notion connector** - required. Either bring your own tracking board or let setup build
  one.
- **Gmail connector** - required. Works best if job alerts land in a dedicated inbox or
  under a label.
- **Chrome browser tools** - optional. Most job descriptions come from public APIs without
  a browser. A browser only helps on the awkward career pages.

## Getting started

1. Install the plugin.
2. Connect Notion and Gmail.
3. Have 3 to 5 job postings handy that represent what you are going after, plus one or two
   you looked at and passed on. Links are fine.
4. Say **"set up my job search pipeline"**.

Setup takes about 20 minutes and most of it is the rubric interview. Do not skip that
part. A pipeline with a lazy rubric surfaces everything as "High" and you stop looking at
it by week two.

The postings matter more than the answers. What people say they want and what they
actually apply to are different things, and the passes are usually the sharpest signal in
the whole interview.

Setup ends by running a live scan and scoring real postings in front of you, so you can
correct the rubric while it is still cheap to correct.

## Skills

| Skill | Say | What it does |
|---|---|---|
| `setup-pipeline` | "set up my job search pipeline" | Interviews you, builds your rubric, connects or creates the Notion board, schedules the runs |
| `email-scan` | "check my email for new roles" | Reads the inbox, creates records, applies status updates from ATS mail |
| `fetch-jd` | "fetch the job descriptions" | Pulls full descriptions via public ATS APIs, browser as fallback |
| `score-roles` | "score these roles" or "score this: <url>" | Scores against your rubric, writes tier plus summary to Notion |

After setup, two scheduled tasks run this on their own. You mostly just read the board.

## What it does with your email

**It only reads.** It never sends, drafts, replies, forwards, deletes, archives, marks
spam, or touches labels. If an email needs an answer, it appears at the top of the report
and you answer it yourself.

Two lanes, scoped separately:

- **New roles** come only from an allowlist of alert senders you set during setup, usually
  just LinkedIn. Nothing outside that list can ever create a record. Because an allowlist
  fails silently, every run also reports unfamiliar senders that look like job alerts, so
  you can add them deliberately.
- **Status updates** use a wider net, because rejections and interview invitations arrive
  from whatever system the employer happens to use. This is safe because a status email
  can only update a record already on your board. It cannot create one, and no match means
  no write.

Email bodies are treated as data, never as instructions. A message that tries to tell the
assistant what to do gets flagged in the report and changes nothing.

## Bring your own board

If you already track applications in Notion, setup maps to your schema instead of
replacing it. It reads your property names and types, maps them to what the pipeline
needs, offers to add anything missing, and uses your status vocabulary throughout. It
never renames, retypes, or deletes anything you already have.

## The rubric is the whole thing

Everything else is plumbing. The rubric is a page in Notion, in plain language, that you
edit whenever a score annoys you. It holds:

- hard filters that cap a role no matter what
- the dimensions you actually check when reading a posting
- your standout logic, if you have any: the combination that makes you an unusual
  candidate rather than a merely qualified one
- what each tier means and what you do about it
- two calibration anchors from setup, so you can tell later if scoring has drifted

When a score is wrong, fix the rule that produced it, not the score. A rubric corrected a
few times in the first two weeks becomes something you trust.

## What it deliberately does not do

No resume writing, no cover letters, no interview prep, no Slack notifications, no
scanning company career boards directly. This is the intake and triage loop only. Those
other pieces exist but they are much more personal, and they are worth building on top of
a triage loop that already works rather than bundling in on day one.

## Things learned the hard way, now baked in

These are the failures this pipeline has already hit, in case you extend it:

- **Notion databases have a database ID and a data source ID.** Querying the database ID
  returns nothing and raises no error. Every role then looks new, and you get a duplicate
  on every run. Always query the data source ID, and prove one known row round-trips
  before trusting a scan.
- **Never dedup with semantic search.** It caps its result set and ranks by relevance, so
  as the board grows it silently stops returning the row you are checking against.
  Candidate-scoped exact queries stay correct at any size.
- **Never load the whole table to diff against either.** You get the first page only, and
  everything past it looks brand new.
- **A sender allowlist is the wrong filter for a job inbox.** Every gap drops real signal
  with no error to notice. Read broadly and classify by content.
- **Strip tracking parameters before comparing URLs.** The same role arrives with a
  different URL in every email.
- **A retry counter that does not record which technique was tried** turns a tooling
  limitation into a permanent verdict about the data. Postings written off as dead after
  repeated browser failures turned out to be live and resolved instantly through a JSON
  endpoint.
- **Log what a batch cap truncated.** A silent truncation reads as "everything is handled"
  when it is not.
