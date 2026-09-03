# hired

A job search pipeline for Claude Cowork. It reads your inbox for new roles and
application updates, fetches the actual job description, scores each role against a rubric
**you** write during setup, and keeps it all on a Notion board.

Site: [hired.run](https://hired.run)

The point is not automation for its own sake. It is that every morning there is one view,
sorted, with a two-sentence reason attached to each role, so deciding what to apply to
takes five minutes instead of an hour of tab management.

## What you need

- **Claude with Cowork** (desktop app recommended)
- **Notion connector** - required. Either bring your own tracking board or let setup build
  one.
- **Gmail connector** - required. Works best if job alerts land in a dedicated inbox or
  under a label.
- **Browser tools** - optional. Most job descriptions come from public ATS endpoints
  (Greenhouse, Lever, Ashby, SmartRecruiters, Workday, BambooHR) or the posting's own page
  without a browser. The built-in browser is preferred for the awkward career pages
  because it works in an unattended scheduled run; Claude in Chrome works too.
- **Slack connector** - optional. Outbound only: posts run results to a channel you pick.
  Off unless you turn it on during setup.

## Getting started

1. Install the plugin.
2. Connect Notion and Gmail.
3. Have 3 to 5 job postings handy that represent what you are going after, plus one or two
   you looked at and passed on. Links are fine.
4. Optionally, have your resume handy, and a cover letter or two you actually sent.
5. Say **"set up my job search pipeline"**.

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
| `load-experience` | "use my resume" | Reads a resume and cover letters you point at, and writes the evidence scoring cites |
| `email-scan` | "check my email for new roles" | Reads the inbox, creates records, applies status updates from ATS mail |
| `fetch-jd` | "fetch the job descriptions" | Pulls full descriptions via public ATS APIs, browser as fallback |
| `score-roles` | "score these roles" or "score this: <url>" | Scores against your rubric, writes tier plus summary to Notion |
| `notify-slack` | (runs automatically after a scan or score, if configured) | Posts high-fit roles, status changes, and items needing a reply to a Slack channel you chose |

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
assistant what to do gets flagged in the report and changes nothing. The same goes for
job descriptions fetched from the web: a posting that tells the scorer what tier to give
it is scored like any other.

Two opt-ins, both off by default. If the mailbox is dedicated to the job search, setup
offers **content mode**, which drops the allowlist and classifies every message by what it
says, since on a dedicated mailbox the allowlist protects nothing and its gaps still lose
roles. And **sent mail** can be read too, to catch applications you email directly and
replies where you confirm an interview. Sent mail can only update a record that already
exists, and never marks anything withdrawn or rejected on your behalf.

## Bring your own board

If you already track applications in Notion, setup maps to your schema instead of
replacing it. It reads your property names and types, maps them to what the pipeline
needs, offers to add anything missing, and uses your status vocabulary throughout. It
never renames, retypes, or deletes anything you already have.

## Your resume, as evidence

Point setup at a resume - a file, a Notion page, or pasted text - and it reads it instead
of making you recite your own career. Add a cover letter or two you actually sent and it
picks up how you position yourself, which is usually sharper than anything on the resume.
What comes out is an **Experience** page next to your rubric: roles, scope, proof points,
domains you are genuinely deep in versus ones you touched once, and the gaps.

Scoring then cites it. Instead of "strong product background", a summary says which of
your accomplishments maps to the scope in the posting, and names the one or two things
the posting asks for that nothing in your background supports. That second half is the
useful one, and it is the part a rubric alone cannot produce.

The split that keeps this honest: **the rubric says what you want, the resume says what
is true about you.** A resume never becomes criteria. Four fintech roles on it is not a
preference for fintech; only the rubric states preferences, and only you write the rubric.

It is optional - the pipeline scores fine without it, off the proof points from the
interview. And your resume is read, never written: nothing edits it, nothing improves it,
nothing sends it anywhere. The contents land on your own Notion page and stop there.

Re-run it with "use my resume" whenever the resume changes.

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

## Board hygiene (optional)

A pipeline is good at filling the intake queue and bad at emptying it. Two rules, each
opt-in during setup with its own number of days:

- **No response.** An application left in the submitted state for that long with no
  status mail moves to a "no response" status, so the board stops counting it as live.
- **Stale.** An intake role you have not decided on after that long gets a `Stale`
  checkbox, which hides it from the "Needs action" view without touching its status. You
  clear it by moving the record.

Neither touches phone screens or interviews that go quiet. Those are conversations, and
the report mentions a backlog of them instead of moving anything.

## Slack notifications (optional)

Turn it on during setup and the pipeline posts high-fit roles, application status
changes, and anything needing a reply to a channel you pick. It is off by default, and
outbound only - it never reads a channel, never replies, and never treats anything
written there as an instruction back to the pipeline. A quiet run stays quiet; nothing
posts unless something actually happened.

## What it deliberately does not do

No resume or cover letter writing, no interview prep, no auto-applying, no scanning
company career boards directly. It reads a resume you point it at, as evidence for
scoring; it never writes one, never edits one, and never sends one anywhere. This is the
intake and triage loop only. Those other pieces exist but they are much more personal,
and they are worth building on top of a triage loop that already works rather than
bundling in on day one.

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
- **A sender allowlist fails silently.** Every gap drops real signal with no error to
  notice. This pipeline still uses one for intake, deliberately, because it is the only
  filter that keeps record creation contained — but it pairs the allowlist with a
  coverage check that reports senders which fell outside it, so gaps become visible and
  get added on purpose instead of discovered by accident.
- **Strip tracking parameters before comparing URLs.** The same role arrives with a
  different URL in every email.
- **But never filter the canonical URL against the stored column.** The column holds raw
  URLs, so an exact match on the cleaned form returns nothing, every role looks new, and
  you get a full set of duplicates in one run. Match on the per-job id as a substring,
  and prove one known id round-trips before trusting an all-clear. The primitives ship
  as `references/dedup.py` with a regression table of real duplicate pairs.
- **Keep both URLs.** Pointing a record at the company's own posting and dropping the
  LinkedIn link means the next LinkedIn alert for the same req sails past dedup.
- **A relation can point at nothing.** Notion accepts a company relation whose page id
  does not exist, with no error, and the record shows a blank company forever. Ids come
  from a live response in the same run, and every batch write is re-read afterwards.
- **Write page bodies with real newlines.** A literal `\n` lands as one run-on paragraph
  with stray `n` characters and no headings. Read one page back after every batch.
- **Never accept the first read of a rendered page.** A page read before it finishes
  loading returns the title, company, and location from the server-rendered header with
  no description body and no error, so a partial description gets stored as complete and
  scored against text nobody read. Assert a minimum length, re-read, then fall back.
- **Log the attempt before the fetch, not after.** A scheduled run that dies mid-fetch
  never reaches the logging step, so an unlogged failure reads as fresh backlog forever.
- **A retry counter that does not record which technique was tried** turns a tooling
  limitation into a permanent verdict about the data. Postings written off as dead after
  repeated browser failures turned out to be live and resolved instantly through a JSON
  endpoint.
- **Log what a batch cap truncated.** A silent truncation reads as "everything is handled"
  when it is not.
