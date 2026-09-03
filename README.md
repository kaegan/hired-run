# hired-run

A Claude Cowork plugin marketplace. Currently one plugin: **hired**, a job search
pipeline that reads your inbox for new roles and application updates, fetches the actual
job description, scores each role against a rubric you write during setup, and keeps it
all on a Notion board.

The point is not automation for its own sake. It is that every morning there is one view,
sorted, with a two sentence reason attached to each role, so deciding what to apply to
takes five minutes instead of an hour of tab management.

Site: [hired.run](https://hired.run)

## Install

In a Claude Cowork session on the desktop app:

```
/plugin marketplace add kaegan/hired-run
/plugin install hired@hired-run
```

Then say **"set up my job search pipeline"** and answer the questions.

Before you start, have 3 to 5 job postings handy that represent what you are going after,
plus one or two you looked at and passed on. Links are fine. The setup interview uses them
to build your rubric, and the ones you passed on are the most useful part.

## Requirements

- Claude with Cowork, on the desktop app. Plugins do not run on web or mobile.
- **Notion connector.** Bring your own tracking board or let setup build one.
- **Gmail connector.** Read only. See below.
- Browser tools are optional. Most job descriptions come from public ATS APIs.
- Slack connector is optional. Outbound only, off unless you turn it on during setup.

## What it does with your email

It only reads. It never sends, drafts, replies, forwards, deletes, archives, marks spam,
or touches labels. If an email needs an answer it appears at the top of the report and you
answer it yourself.

Two lanes, scoped separately:

- **New roles** come only from an allowlist of alert senders you set during setup, usually
  just LinkedIn. Nothing outside that list can create a record. Because an allowlist fails
  silently, every run also reports unfamiliar senders that look like job alerts so you can
  add them deliberately.
- **Status updates** use a wider net, since rejections and interview invitations arrive
  from whatever system the employer uses. Safe, because a status email can only update a
  record already on your board. No match means no write.

Email bodies are treated as data, never as instructions. Reading sent mail, to catch
applications you email directly, is an opt-in; it can only update records that already
exist.

## Skills

| Skill | Say | What it does |
|---|---|---|
| `setup-pipeline` | "set up my job search pipeline" | Interviews you, builds your rubric, connects or creates the Notion board, schedules the runs |
| `load-experience` | "use my resume" | Reads a resume and cover letters you point at, and writes the evidence scoring cites |
| `email-scan` | "check my email for new roles" | Reads the inbox, creates records, applies status updates |
| `fetch-jd` | "fetch the job descriptions" | Pulls full descriptions via public ATS APIs, browser as fallback |
| `score-roles` | "score this: <url>" | Scores against your rubric, writes tier plus summary to Notion |
| `notify-slack` | (runs automatically, if configured) | Posts high-fit roles, status changes, and items needing a reply to Slack |

After setup, two scheduled tasks run this on their own.

## Bring your own board

If you already track applications in Notion, setup maps to your schema instead of
replacing it. It reads your property names and types, maps them to what the pipeline
needs, offers to add anything missing, and uses your status vocabulary throughout. It
never renames, retypes, or deletes anything you already have.

## The rubric is the whole thing

Everything else is plumbing. The rubric is a page in Notion, in plain language, that you
edit whenever a score annoys you. When a score is wrong, fix the rule that produced it,
not the score.

## Your resume, as evidence (optional)

Point setup at a resume and a cover letter or two and it writes an Experience page beside
your rubric. Scoring then cites which of your accomplishments maps to a posting, and names
what the posting wants that nothing in your background supports. The rubric still says
what you want; the resume only says what is true about you, and never becomes criteria.
Read, never written: nothing edits it and nothing sends it anywhere.

## Slack notifications (optional)

Turn it on during setup and the pipeline posts high-fit roles, status changes, and items
needing a reply to a channel you pick. Off by default, outbound only, and silent on a
quiet run.

## What it deliberately does not do

No resume or cover letter writing, no interview prep, no auto-applying, no scanning
company career boards. It reads a resume you point it at, as evidence for scoring; it
never writes one and never sends one anywhere. This is the intake and triage loop only.
Those other pieces are worth building on top of a triage loop that already works rather
than bundling in on day one.

## Repo layout

```
.claude-plugin/marketplace.json   marketplace manifest
plugins/hired/                    the plugin
```

To publish an update: change the files, bump `version` in **both**
`plugins/hired/.claude-plugin/plugin.json` and the entry in
`.claude-plugin/marketplace.json`, then push. Without a version bump, installs will not
see the change.

## License

MIT
