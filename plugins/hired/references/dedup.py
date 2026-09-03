"""
Dedup primitives for the hired plugin.

Single source of truth for URL canonicalization, title normalization, per-job key
extraction, and company-name resolution. The email-scan skill imports these instead of
re-deriving them from prose on every run. Run `python3 test_dedup.py` after any change
and keep it green; when a real duplicate slips through, add the pair to the table first.

Two postings are the SAME req iff:
  - they share a job_key AND canon_url puts them on the same host, OR
  - they share a resolved company AND an equal norm_title.

A specific posting URL (one with a job_key) is decisive on its own. Never require a title
match alongside it: employers rename live reqs. The decision flow lives in
skills/email-scan/SKILL.md, Step 3.
"""

import re
from urllib.parse import urlsplit, parse_qs

# ATS host aliases. Each pair is the same board served from two hostnames and must fold
# to one, or the same posting arrives as two records. Add pairs as you hit them.
ALIAS = {
    "boards.greenhouse.io": "greenhouse.io",
    "job-boards.greenhouse.io": "greenhouse.io",
    "boards.eu.greenhouse.io": "eu.greenhouse.io",
    "job-boards.eu.greenhouse.io": "eu.greenhouse.io",
    "hire.lever.co": "jobs.lever.co",
}

# Query parameters that carry a per-job id on boards whose posting URLs are otherwise one
# generic portal path (PeopleSoft `JobOpeningId`, many municipal and university boards,
# embedded Greenhouse `gh_jid`). A parameter here is kept in the canonical form ONLY when
# the path carries no job id of its own; a native board URL already has the id in the path
# and keeping the parameter too would split one req into two.
JOB_ID_PARAMS = ("JobOpeningId", "jobid", "jobId", "job_id", "gh_jid", "id")


def _strip_www(host):
    return host[4:] if host.startswith("www.") else host


def _path_job_id(host, path):
    """The per-job id carried in the URL path, or None for a generic portal page."""
    m = re.search(r"/jobs/view/(\d+)", path)  # LinkedIn
    if m:
        return m.group(1)
    m = re.search(r"/jobs/([A-Za-z0-9][A-Za-z0-9\-]*)", path)  # Greenhouse, iCIMS, most /jobs/<id>
    if m and re.search(r"\d", m.group(1)):  # /jobs/search and /jobs/view carry no digit
        return m.group(1)
    if host.endswith("ashbyhq.com") or host.endswith("lever.co"):
        segs = [s for s in path.split("/") if s]  # /<company>/<uuid>
        if len(segs) >= 2:
            return segs[-1]
    m = re.search(r"/job/[^/]+/[^/]+_([A-Za-z0-9\-]+)$", path)  # Workday /job/<loc>/<Title>_<REQ>
    if m:
        return m.group(1)
    if host.endswith("smartrecruiters.com"):
        m = re.search(r"/(\d{9,})(?:-|/|$)", path)  # /Company/743999...-slug
        if m:
            return m.group(1)
    if host.endswith("bamboohr.com"):
        m = re.search(r"/careers/(\d+)", path)  # ids are short ints, keep the segment
        if m:
            return "careers/" + m.group(1)
    if host.endswith("breezy.hr"):
        m = re.search(r"/p/([0-9a-f]{8,})", path)  # /p/<hex>-slug
        if m:
            return m.group(1)
    m = re.search(r"/j/([A-Z0-9]{6,})(?:/|$)", path)  # Workable /j/<ID>
    if m:
        return m.group(1)
    return None


def canon_url(u):
    """Canonicalize a posting URL. Store the RAW url in Notion; compare on this form.

    Lowercases the host, strips a leading www., folds ATS host aliases, drops the query
    string and fragment (keeping one job-id parameter only when the path has no id of its
    own), drops a trailing slash, and reduces LinkedIn to linkedin.com/jobs/view/<id>.
    """
    s = urlsplit(u if "://" in u else "https://" + u)
    host = _strip_www(s.netloc.lower())
    host = ALIAS.get(host, host)
    path = s.path.rstrip("/")
    if host.endswith("linkedin.com"):
        m = re.search(r"/jobs/view/(\d+)", path)
        if m:
            return "linkedin.com/jobs/view/" + m.group(1)
    if _path_job_id(host, path) is None:
        qs = parse_qs(s.query)
        for p in JOB_ID_PARAMS:
            v = qs.get(p, [None])[0]
            if v:
                return f"{host}{path}?{p}={v}"
    return host + path


def job_key(u):
    """The stable per-job identifier in a URL, or None for a generic portal.

    The id survives every variation that breaks string equality: scheme, www., /comm/,
    trailing slash, tracking parameters, host aliases. Match candidates against the stored
    URL columns with LIKE '%<job_key>%' (never filter a canonical form against a raw
    column: it matches nothing). None means "no per-job id" (a bare careers page): skip
    the URL check for that candidate and rely on company plus title.
    """
    c = canon_url(u)
    base, _, query = c.partition("?")
    if query:
        qs = parse_qs(query)
        for p in JOB_ID_PARAMS:
            if qs.get(p, [None])[0]:
                return qs[p][0]
    host, _, rest = base.partition("/")
    path = "/" + rest if rest else ""
    return _path_job_id(host, path)


def host_of(u):
    """Canonical host, for confirming that two matching job_keys are on the same board."""
    return canon_url(u).partition("?")[0].partition("/")[0]


EXPAND = {"sr": "senior", "jr": "junior", "pm": "product manager",
          "pmm": "product marketing manager", "swe": "software engineer"}


def norm_title(t):
    """Normalize a job title for exact-equality comparison, scoped to one company.

    A match is EXACT equality of two normalized titles. Substring containment and
    one-word-different are NOT matches; those create the record and flag it for review.
    """
    t = t.lower().strip()
    t = re.sub(r"\s*\([^)]*\)\s*$", "", t)  # trailing parenthetical (location, team, product)
    t = t.replace("&", " and ")
    t = re.sub(r"[.,\-–—()/™®]", " ", t)  # punctuation, dashes, TM, (R)
    t = re.sub(r"\s+", " ", t).strip()
    return " ".join(EXPAND.get(w, w) for w in t.split())


# Legal-entity suffixes safe to strip. Descriptive words (Health, Technologies, Labs) are
# NEVER stripped: they separate "Acme" from "Acme Health", which must stay two companies.
_LEGAL_SUFFIX = {
    "inc", "incorporated", "llc", "ltd", "limited", "corp", "corporation",
    "co", "gmbh", "sa", "plc", "pty", "pte", "ab", "oy", "nv", "bv",
}


def resolve_company(name):
    """Normalize a company name for exact-match lookup-before-create.

    Conservative on purpose: lowercases, normalizes punctuation and whitespace, strips
    only trailing legal-entity suffixes. Two names are the same company iff their resolved
    forms are equal.
    """
    n = name.strip().lower().replace("&", " and ")
    n = re.sub(r"[.,]", " ", n)
    n = re.sub(r"\s+", " ", n).strip()
    parts = n.split()
    while parts and parts[-1] in _LEGAL_SUFFIX:
        parts.pop()
    return " ".join(parts)
