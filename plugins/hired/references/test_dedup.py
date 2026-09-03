"""
Regression table for dedup.py. Every row is a real pair that produced (or would have
produced) a duplicate on a live board. Run with plain Python or pytest:

    python3 test_dedup.py
    python3 -m pytest test_dedup.py -q

If you change dedup.py, this must stay green. If you find a duplicate the current logic
misses, add the pair here FIRST (red), then fix dedup.py (green).
"""

import sys
from dedup import canon_url, norm_title, job_key, resolve_company, host_of


# (raw_a, raw_b, same_req?) -- same host + same job_key means the same posting.
URL_PAIRS = [
    ("https://boards.greenhouse.io/figma/jobs/5989134004?gh_jid=5989134004",
     "https://job-boards.greenhouse.io/figma/jobs/5989134004", True),
    ("https://www.linkedin.com/comm/jobs/view/4434940147/",
     "https://www.linkedin.com/jobs/view/4434940147", True),
    ("https://linkedin.com/jobs/view/4437788998?refId=abc&trackingId=xyz",
     "https://linkedin.com/jobs/view/4437788998/", True),
    ("https://company.com/careers?gh_jid=7308929",
     "https://company.com/careers?gh_jid=7308930", False),
    ("https://job-boards.greenhouse.io/gitlab/jobs/8597805002",
     "https://www.linkedin.com/jobs/view/8597805002", False),  # different host, same digits
    ("https://hire.lever.co/acme/1a2b3c4d-0000-4000-8000-123456789abc/apply",
     "https://jobs.lever.co/acme/1a2b3c4d-0000-4000-8000-123456789abc", False),  # /apply is a different path; title match catches it
    ("https://jobs.lever.co/acme/1a2b3c4d-0000-4000-8000-123456789abc?lever-origin=applied",
     "https://jobs.lever.co/acme/1a2b3c4d-0000-4000-8000-123456789abc/", True),
    ("https://jobs.ashbyhq.com/acme/9f8e7d6c-1111-4222-8333-abcdefabcdef?utm_source=li",
     "https://jobs.ashbyhq.com/Acme/9f8e7d6c-1111-4222-8333-abcdefabcdef", True),
    ("https://adobe.wd5.myworkdayjobs.com/en-US/external_experienced/job/San-Francisco/Product-Manager_R170204?source=LinkedIn",
     "https://adobe.wd5.myworkdayjobs.com/external_experienced/job/San-Francisco/Product-Manager_R170204", True),  # locale prefix differs, same req id on the same host
    ("https://adobe.wd5.myworkdayjobs.com/external_experienced/job/San-Francisco/Product-Manager_R170204?source=LinkedIn",
     "https://adobe.wd5.myworkdayjobs.com/external_experienced/job/San-Francisco/Product-Manager_R170204/", True),
    ("https://jobs.smartrecruiters.com/Acme/743999999999999-senior-product-manager",
     "https://jobs.smartrecruiters.com/Acme/743999999999999-senior-product-manager?trid=x", True),
    ("https://acme.bamboohr.com/careers/25",
     "https://acme.bamboohr.com/careers/25/detail", True),
    ("https://acme.breezy.hr/p/035bb7b9f68c-senior-pm",
     "https://acme.breezy.hr/p/035bb7b9f68c-senior-pm?utm=1", True),
    ("https://example.com/psc/EXT/EMPLOYEE/HRMS/c/HRS_HRAM_FL.HRS_CG_SEARCH_FL.GBL?Page=HRS_APP_JBPST_FL&Action=U&JobOpeningId=20260593&PostingSeq=1",
     "https://example.com/psc/EXT/EMPLOYEE/HRMS/c/HRS_HRAM_FL.HRS_CG_SEARCH_FL.GBL?Page=HRS_APP_SCHJOB_FL&JobOpeningId=20260593", True),
    ("https://example.com/psc/x?JobOpeningId=20260593",
     "https://example.com/psc/x?JobOpeningId=20260600", False),
    ("https://jobs.example.org/careers?jobid=115321",
     "https://www.jobs.example.org/careers?jobid=115321&extra=1", True),
]

# URLs with no per-job id: job_key must be None so the URL check is skipped.
GENERIC_PORTALS = [
    "https://www.acme.com/careers",
    "https://boards.greenhouse.io/acme",
    "https://jobs.lever.co/acme",
    "https://www.linkedin.com/jobs/search/?keywords=pm",
    "https://acme.com/jobs/search",
]


def _same_posting(a, b):
    ka, kb = job_key(a), job_key(b)
    if ka is None or kb is None:
        return False
    return ka == kb and host_of(a) == host_of(b)


def test_url_pairs():
    for a, b, expected in URL_PAIRS:
        assert _same_posting(a, b) is expected, f"{a} vs {b}: expected same={expected}"


def test_generic_portals_have_no_key():
    for u in GENERIC_PORTALS:
        assert job_key(u) is None, f"{u} should have no job_key, got {job_key(u)!r}"


def test_canon_examples():
    assert canon_url("https://www.linkedin.com/comm/jobs/view/123/?trk=x") == "linkedin.com/jobs/view/123"
    assert canon_url("https://boards.greenhouse.io/figma/jobs/5989134004?gh_jid=5989134004") == "greenhouse.io/figma/jobs/5989134004"
    assert canon_url("https://company.com/careers?gh_jid=7308929&utm=1") == "company.com/careers?gh_jid=7308929"
    assert canon_url("HTTPS://WWW.Acme.com/Careers/") == "acme.com/Careers"


# (title_a, title_b, same_title?)
TITLE_PAIRS = [
    ("Sr. Product Manager, Platform & Agentic Integrations",
     "Senior Product Manager - Platform and Agentic Integrations", True),
    ("Sr. PMM, Platform & LLMs",
     "Senior Product Marketing Manager, Platform & LLMs", True),
    ("Head of Product & Growth (Dreamwell)",
     "Head of Product & Growth", True),
    ("Lead Product Manager",
     "Lead Game Product Manager - EA SPORTS™ FC", False),
    ("Senior PMM, Command by Asana",
     "Principal PMM, Command by Asana", False),
    ("Product Manager, Platform",
     "Product Manager, Core Platform", False),
    ("Staff Software Engineer (Remote - Canada)",
     "Staff Software Engineer", True),
]


def test_title_pairs():
    for a, b, expected in TITLE_PAIRS:
        assert (norm_title(a) == norm_title(b)) is expected, f"{a!r} vs {b!r}: expected same={expected}"


# (name_a, name_b, same_company?)
COMPANY_PAIRS = [
    ("Acme, Inc.", "Acme", True),
    ("Acme Inc", "ACME INC.", True),
    ("Velora", "Velora Health", False),
    ("D2L", "D2L Technologies", False),
    ("Shopify Inc.", "Shopify", True),
    ("Procter & Gamble", "Procter and Gamble", True),
]


def test_company_pairs():
    for a, b, expected in COMPANY_PAIRS:
        assert (resolve_company(a) == resolve_company(b)) is expected, f"{a!r} vs {b!r}: expected same={expected}"


if __name__ == "__main__":
    failures = 0
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"ok   {name}")
            except AssertionError as e:
                failures += 1
                print(f"FAIL {name}: {e}")
    sys.exit(1 if failures else 0)
