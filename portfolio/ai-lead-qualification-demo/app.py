"""LeadPilot: local, zero-cost, synthetic B2B prospect qualification demo."""
import csv
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parent
SECTOR = {"warehouse": 35, "forklift_service": 35, "manufacturing": 35, "restaurant": 20, "hotel": 20}
EVIDENCE = {"confirmed": 30, "potential": 10, "unknown": 0}

def qualify(records):
    """Deterministic, inspectable ranking. Scores never authorize outreach."""
    seen, output = set(), []
    for src in records:
        x = dict(src)
        key = (x["company"].strip().casefold(), x["city"].strip().casefold())
        duplicate = key in seen
        seen.add(key)
        score = SECTOR.get(x["industry"], 0)
        reasons = [f"Industry fit +{score}"] if score else []
        if x["service_area"] == "yes":
            score += 25
            reasons.append("Within service area +25")
        ev = EVIDENCE.get(x["propane_evidence"], 0)
        score += ev
        if ev:
            reasons.append(f"Propane evidence ({x['propane_evidence']}) +{ev}")
        if x["contact_verified"] == "yes":
            score += 10
            reasons.append("Verified business contact +10")
        flags = []
        if duplicate:
            flags.append("Duplicate business/location")
        if x["existing_customer"] == "yes":
            flags.append("Already a customer")
        if x["service_area"] != "yes":
            flags.append("Outside service area")
        if x["propane_evidence"] != "confirmed":
            flags.append("Usage unconfirmed; human verification required")
        x.update(score=score, priority=("high" if score >= 75 else "medium" if score >= 50 else "low"),
                 reasons=reasons, flags=flags, review_status=("blocked" if duplicate or
                 x["existing_customer"] == "yes" or x["service_area"] != "yes" else "needs_human_review"))
        output.append(x)
    return sorted(output, key=lambda row: (-row["score"], row["company"]))

def sample():
    with (ROOT / "sample_leads.csv").open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))

def dashboard(leads):
    payload = json.dumps(leads).replace("<", "\\u003c")
    html = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>LeadPilot — B2B Lead Qualification Demo</title><style>
:root{font-family:system-ui;color:#edf5ff;background:#0d1522}*{box-sizing:border-box}body{margin:0}
main{max-width:1160px;margin:auto;padding:32px 22px}h1{font-size:38px;letter-spacing:-1px;margin-bottom:8px}
p,small{color:#aebed0;line-height:1.6}.brand{color:#6ce6c3;font-weight:800}
.metrics{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:24px 0}
.metric{background:#152338;border:1px solid #2b4058;border-radius:14px;padding:18px}
.metric strong{display:block;font-size:30px;margin-top:6px}.controls{display:flex;gap:10px;flex-wrap:wrap;margin:20px 0}
input,select,button{border:1px solid #354e65;background:#16283c;color:white;padding:12px;border-radius:9px}
button{cursor:pointer;background:#176a64}.table{overflow:auto;border:1px solid #293d52;border-radius:12px}
table{border-collapse:collapse;width:100%;min-width:850px}th,td{text-align:left;border-bottom:1px solid #293d52;padding:14px;font-size:13px}
th{color:#aabbce;font-size:11px;text-transform:uppercase}tr:last-child td{border:0}
.tag{background:#263b52;border-radius:6px;padding:5px 8px;display:inline-block}
.blocked{background:#602d43}.high{background:#1f5a46}details{max-width:280px}
footer{margin-top:24px;color:#98aabc;font-size:12px;line-height:1.7}
@media(max-width:680px){.metrics{grid-template-columns:repeat(2,1fr)}h1{font-size:29px}}
</style></head><body><main>
<div class="brand">LeadPilot / PORTFOLIO DEMO</div><h1>Explainable B2B lead qualification.</h1>
<p>Local, zero-cost prospect prioritization for a synthetic propane supplier. No real customers, scraping, AI API charges, CRM modifications or automatic outreach.</p>
<section class="metrics" id="metrics"></section>
<section class="controls"><input id="q" placeholder="Search company or city" aria-label="Search">
<select id="filter" aria-label="Status"><option value="all">All leads</option><option value="high">High priority</option>
<option value="needs_human_review">Needs human review</option><option value="blocked">Blocked</option></select>
<button id="export">Export review CSV</button></section>
<div class="table"><table><thead><tr><th>Company</th><th>Sector</th><th>Evidence</th>
<th>Score</th><th>Review status</th><th>Reasons & flags</th></tr></thead><tbody id="rows"></tbody></table></div>
<footer>Scoring: industry up to 35 + service area 25 + evidence up to 30 + verified contact 10.
Duplicates, existing customers and out-of-area businesses are blocked regardless of score.
Potential or unknown propane usage must never be presented as confirmed. Every lead requires review.</footer>
</main><script>
const leads=__LEADS__, el=id=>document.getElementById(id);
const esc=x=>String(x??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
function visible(){let q=el('q').value.toLowerCase(),f=el('filter').value;
return leads.filter(x=>(x.company+' '+x.city).toLowerCase().includes(q)&&(f==='all'||x.review_status===f||(f==='high'&&x.priority==='high')));}
function render(){let data=visible();
el('metrics').innerHTML=[['Sample leads',leads.length],['High priority',leads.filter(x=>x.priority==='high').length],
['Needs review',leads.filter(x=>x.review_status==='needs_human_review').length],
['Blocked',leads.filter(x=>x.review_status==='blocked').length]]
.map(x=>'<div class="metric"><small>'+x[0]+'</small><strong>'+x[1]+'</strong></div>').join('');
el('rows').innerHTML=data.map(x=>'<tr><td><b>'+esc(x.company)+'</b><br><small>'+esc(x.city)+'</small></td><td>'+esc(x.industry)+'</td><td><span class="tag">'+esc(x.propane_evidence)+'</span></td><td><b>'+x.score+'/100</b></td><td><span class="tag '+(x.review_status==='blocked'?'blocked':x.priority==='high'?'high':'')+'">'+esc(x.review_status)+'</span></td><td><details><summary>Show details</summary><small>'+x.reasons.map(s=>'✓ '+esc(s)).join('<br>')+'<br>'+x.flags.map(s=>'⚠ '+esc(s)).join('<br>')+'<br>Source: '+esc(x.source_note)+'</small></details></td></tr>').join('')||'<tr><td colspan="6">No matches</td></tr>';}
el('q').oninput=render;el('filter').onchange=render;
el('export').onclick=()=>{let cols=['company','city','industry','score','priority','review_status','flags'];
let rows=[cols.join(','),...visible().map(x=>cols.map(k=>'"'+String(Array.isArray(x[k])?x[k].join('; '):x[k]??'').replace(/"/g,'""')+'"').join(','))];
let a=document.createElement('a');a.href=URL.createObjectURL(new Blob([rows.join('\n')],{type:'text/csv'}));a.download='lead_review_queue.csv';a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000);};render();
</script></body></html>"""
    return html.replace("__LEADS__", payload)

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = urlparse(self.path).path
        leads = qualify(sample())
        if path == "/":
            body, kind = dashboard(leads).encode(), "text/html; charset=utf-8"
        elif path == "/api/leads":
            body, kind = json.dumps({"sample_only": True, "leads": leads}, indent=2).encode(), "application/json"
        else:
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header("Content-Type", kind)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

if __name__ == "__main__":
    print("Open http://127.0.0.1:8000/")
    ThreadingHTTPServer(("127.0.0.1", 8000), Handler).serve_forever()
