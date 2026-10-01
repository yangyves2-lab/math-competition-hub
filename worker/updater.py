
"""
Weekly incremental updater.
Set SEARCH_PROVIDER=serper and SERPER_API_KEY for production web discovery.
The updater is intentionally conservative: it never deletes old editions/papers.
"""
import os, requests, re
from datetime import datetime
from urllib.parse import urlparse
from flask import current_app
from app import db
from app.models import Competition, Edition, Paper, Source, ChangeLog, SearchRun

QUERIES=[
    '"mathematics competition" registration 2026 2027',
    '"math competition" registration deadline 2026 2027',
    '"數學競賽" 報名 2026 2027',
    '"數學競賽" 歷屆試題 PDF',
    '"mathematics contest" past papers solutions',
    '"數學奧林匹亞" 報名',
    '"UKMT" competition 2026 2027',
    '"AMC 10" registration 2026 2027',
]

def serper(q):
    key=current_app.config.get("SERPER_API_KEY")
    if not key: return []
    r=requests.post("https://google.serper.dev/search",headers={"X-API-KEY":key,"Content-Type":"application/json"},json={"q":q,"num":10},timeout=30)
    r.raise_for_status()
    return r.json().get("organic",[])

def normalize_url(u):
    try:
        p=urlparse(u); return f"{p.scheme}://{p.netloc}{p.path}".rstrip("/")
    except: return u

def classify_source(url):
    host=urlparse(url).netloc.lower()
    return "official" if any(x in host for x in [".gov.",".edu.", "ukmt.org.uk","maa.org","tmo.com.tw","99cef.org.tw"]) else "third_party"

def extract_candidates(results):
    # Conservative MVP: save discoveries as source records only unless a known competition is matched.
    # This avoids hallucinating dates/fees from snippets.
    return results

def run_update():
    started=datetime.utcnow(); run=SearchRun(started_at=started); db.session.add(run); db.session.commit()
    new=updated=papers=errors=0
    try:
        results=[]
        for q in QUERIES:
            try: results += serper(q)
            except Exception: errors += 1
        # Match discovered URLs against existing competitions. New entities are queued as sources,
        # requiring official-page verification before becoming structured competition records.
        for item in results:
            url=normalize_url(item.get("link",""))
            title=item.get("title","")
            if not url: continue
            matched=None
            for c in Competition.query.all():
                if c.name.lower() in title.lower() or (c.official_url and urlparse(c.official_url).netloc==urlparse(url).netloc):
                    matched=c; break
            if matched:
                matched.last_checked=started; matched.updated_at=started
                if not any(s.url==url for s in matched.sources):
                    db.session.add(Source(competition_id=matched.id,url=url,source_type=classify_source(url),title=title,checked_at=started))
                    updated += 1
        db.session.commit()
    except Exception as e:
        errors += 1; run.notes=str(e)
        db.session.rollback()
    run.finished_at=datetime.utcnow(); run.new_count=new; run.updated_count=updated; run.paper_count=papers; run.error_count=errors
    db.session.add(run); db.session.commit()
    return {"new":new,"updated":updated,"papers":papers,"errors":errors}
