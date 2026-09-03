# Notion schema (Branch B: creating a new board)

Only use this when the user does not already have a tracking board. If they do, map to
their schema instead and change nothing about it.

Create a top level page **Job Search**, then both databases inside it. Create Companies
first, because Applications holds a relation pointing at it.

## Companies

| Property | Type | Notes |
|---|---|---|
| Name | Title | Company name as listed on the posting |
| Website | URL | Inferred from the posting domain |
| Job Board URL | URL | Careers page, if known |
| Applications | Relation | Auto-created by the Applications relation |
| Notes | Text | Freeform |

Set each company page icon to
`https://www.google.com/s2/favicons?domain=<domain>&sz=128` at creation. If the favicon
fails, skip it and carry on. Never let an icon failure block a record.

## Applications

| Property | Type | Options / notes |
|---|---|---|
| Job Title | Title | Exact title from the posting |
| Company | Relation | To Companies. Expects an array of page URLs or IDs |
| Application Status | Status | To Review, Submitted, Phone Screen, Interviewing, Offer, Rejected, Withdrawn, Passed, No Response |
| Fit Score | Select | Very High, High, Medium, Low, Very Low |
| Posting | URL | The company-site or ATS posting link. Store the raw URL, dedup on the per-job key |
| Source URL | URL | The job board's own link (a LinkedIn view URL) when the alert carried both. A LinkedIn-only role holds it in both columns. Dedup checks both |
| Application Date | Date | The day the application was actually sent, from the confirmation email in the user's timezone. Set once, never overwritten |
| Stale | Checkbox | Set by scoring on To Review records left undecided for `stale_days`. Cleared by the user moving the record. Never a scoring input |
| Location | Text | As listed |
| Flexibility | Select | Remote, Hybrid, In-person |
| Salary Range | Text | Formatted, e.g. "CAD $150K-$180K" |
| Source | Select | LinkedIn, Indeed, Wellfound, Company Site, Referral, Manual, Other |
| Date Added | Date | Creation date |
| Last Seen | Date | Refreshed every time a scan sees the role live |
| Times Seen | Number | Incremented on each sighting |

`To Review` is the intake state. Every new record starts there. `No Response` exists for
the optional sweep that retires applications left in `Submitted` past `no_response_days`;
`Withdrawn` and `Passed` are only ever set by the user.

`Posting` holds the canonical link and `Source URL` the job board mirror. Both matter for
dedup: the next alert for a req arrives carrying the job board URL, so a record that only
kept the company-site URL cannot be matched against it.

`Last Seen` and `Times Seen` exist so the pipeline can tell an evergreen posting that
keeps appearing in alerts from one that has gone quiet, and so a suppressed duplicate
still leaves a trace on the record it matched. Dedup itself does not branch on them: a
company plus title match suppresses regardless of how old the existing record is. They
are cheap and worth having.

## Page icons

New records get `https://www.notion.so/icons/document_gray.svg`. The scoring skill
recolors by tier:

- Very High: `document_purple.svg`
- High: `document_green.svg`
- Medium: `document_yellow.svg`
- Low: `document_orange.svg`
- Very Low: `document_red.svg`

All under `https://www.notion.so/icons/`. This turns the board into something readable at
a glance, which is most of why anyone opens it.

## Views on Applications

1. **Pipeline** - board grouped by Application Status. The default view.
2. **Needs action** - table, filtered to Fit Score is High or Very High, Application
   Status is To Review, and Stale is unchecked, sorted by Date Added descending. This is
   the view the user should actually check each morning. Hiding stale records is what
   keeps it short enough to be checked.
3. **Unscored queue** - table, filtered to Fit Score is empty. This is the work queue the
   scoring run drains. The pipeline reads it every run, so create it.
4. **All** - table, no filter, sorted by Date Added descending.

## The data source ID gotcha

Notion databases have both a database ID and a **data source** ID. Queries against the
database ID return nothing, with no error. Silent empty results make every role look new,
which produces a duplicate on every single run.

After creating the databases, capture the data source ID from the create response and
save it in the config Field Map. Every dedup query in this plugin uses the data source
ID. Before finishing setup, run one query that you know should return a row and confirm
it does.

## The relation id gotcha

Notion accepts a Company relation that points at a page id which does not exist. The
write succeeds, no error is raised, and the record shows a blank company forever. Every
relation write in this plugin uses an id copied from a live API response in the same run,
never one recalled from earlier in a conversation, and every batch write is followed by a
re-query confirming the company shows. Build the sample records during setup the same
way.
