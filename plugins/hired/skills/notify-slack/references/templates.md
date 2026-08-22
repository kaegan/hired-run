# Slack message templates

Five layouts for notify-slack. Formatting rules, the linking rule, and the tier/mention
rules all live in `SKILL.md` - every template below assumes them. Start from a template,
fill in real data, substitute real Notion URLs per the linking rule, and never ship a
placeholder like "[X roles]" in an actual message.

---

## 1. High-fit roles

Use when score-roles produced roles whose tier is in the user's configured `post_tiers`.

```
**New roles worth a look**
‎
**<notion_page_url|Role Title>** -- <notion_company_url|Company Name>
Tier · Location · Flexibility
One specific reason this fits, pulled from the score summary - not generic filler.
‎
**<notion_page_url|Role Title>** -- <notion_company_url|Company Name>
Tier · Location · Flexibility
One specific reason this fits.
‎
[repeat per role, best tier first]
‎
→ <board_url|Open the board>
```

No @mention - a good score is good news, not urgent news.

---

## 2. Application status update

Use when email-scan applied a status change from an ATS email.

```
**Status update**
‎
**<notion_company_url|Company Name>** -- **<notion_page_url|Role Title>**
Old Status → **New Status**
```

For an offer or an interview invitation, escalate and add the mention:

```
**Offer -- <notion_company_url|Company Name>**
**<notion_page_url|Role Title>**. Check email.
‎
<@mention>
```

Every other transition (including a move into a terminal "no response" or rejected state)
posts without the mention - informational, not urgent.

---

## 3. Needs you

Use for interview invitations awaiting a reply, recruiter outreach worth answering, or
anything with a deadline - the items email-scan's own report lists first.

```
**Needs a reply**
‎
**<notion_company_url|Company Name>** -- **<notion_page_url|Role Title>**
What it is and any deadline, in one line.
‎
[repeat per item]
```

---

## 4. Combining sections

A single run can produce more than one kind of news. Send **one message**, not one per
section. Stack whichever of sections 1-3 apply, in this order: needs-you first (the user
reads this part), then status updates, then high-fit roles. Use a `‎` line between
sections, not a repeated heading style - the section content makes the kind of news clear
on its own.

---

## 5. Errors-only notice

Use only when a run produced nothing to post per templates 1-3, but did produce errors -
per SKILL.md Step 2, this is the one case where a quiet run still posts.

```
Run hit an error and found nothing else to report: <one-line reason>.
```

Keep it to one line. This is a heads-up, not an incident report - the full detail stays in
the calling skill's own chat report where the user is more likely to be looking right
after triggering a run.
