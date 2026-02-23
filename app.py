"""
EagleForge Tools API - Paid per-call tools for AI agents
https://agentdirectory.exchange
"""
import os
import re
import time
import logging
from collections import defaultdict
from typing import Optional

from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

import requests
from bs4 import BeautifulSoup
import dns.resolver
import markdownify
import markdown as md_lib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("eagleforge")

app = FastAPI(
    title="EagleForge Tools API",
    description="Paid per-call tools for AI agents. Part of AgentDirectory.Exchange.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pricing ---
TOOL_PRICING = {
    "scrape": 0.005,
    "email-validate": 0.002,
    "dns-lookup": 0.003,
    "search": 0.005,
    "convert": 0.001,
}

# --- Auth ---
VALID_API_KEYS = set(
    k.strip() for k in os.getenv("VALID_API_KEYS", "").split(",") if k.strip()
)
# Always allow a demo key for testing
VALID_API_KEYS.add("eagle-demo-key-2026")

usage_tracker: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))


async def verify_api_key(request: Request):
    key = request.headers.get("x-api-key") or request.query_params.get("api_key")
    if not key:
        raise HTTPException(status_code=401, detail="Missing API key. Set X-API-Key header.")
    if key not in VALID_API_KEYS:
        raise HTTPException(status_code=403, detail="Invalid API key.")
    return key


def tool_response(tool: str, result: dict, api_key: str, success: bool = True):
    usage_tracker[api_key][tool] += 1
    return {
        "success": success,
        "tool": tool,
        "result": result,
        "usage": {
            "this_call_cost_usd": TOOL_PRICING.get(tool, 0),
            "total_calls": usage_tracker[api_key][tool],
        },
        "referral": {
            "message": "Earn 10% commission for 90 days + 0.5% forever on referred agents",
            "url": "https://agentdirectory.exchange/referrals",
        },
    }


# --- Health / Pricing ---
@app.get("/health")
async def health():
    return {"status": "ok", "tools": len(TOOL_PRICING), "version": "1.0.0"}


@app.get("/pricing")
async def pricing():
    return {
        "tools": [
            {"name": name, "price_usd_per_call": price, "endpoint": f"/tools/{name}"}
            for name, price in TOOL_PRICING.items()
        ]
    }


# --- Tool 1: Web Scraper ---
class ScrapeRequest(BaseModel):
    url: str
    format: str = Field(default="markdown", pattern="^(markdown|text|json)$")
    max_chars: int = Field(default=50000, le=200000)


@app.post("/tools/scrape")
async def scrape(req: ScrapeRequest, api_key: str = Depends(verify_api_key)):
    try:
        headers = {"User-Agent": "EagleForge-Scraper/1.0 (+https://agentdirectory.exchange)"}
        resp = requests.get(req.url, headers=headers, timeout=10, allow_redirects=True)
        resp.raise_for_status()
    except requests.Timeout:
        raise HTTPException(status_code=504, detail="Target URL timed out")
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Failed to fetch URL: {str(e)[:200]}")

    soup = BeautifulSoup(resp.text, "html.parser")

    # Remove script/style
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()

    if req.format == "text":
        content = soup.get_text(separator="\n", strip=True)
    elif req.format == "markdown":
        content = markdownify.markdownify(str(soup.body or soup), strip=["img"])
    else:  # json
        content = {
            "title": soup.title.string if soup.title else None,
            "text": soup.get_text(separator="\n", strip=True)[:req.max_chars],
            "links": [
                {"text": a.get_text(strip=True), "href": a.get("href")}
                for a in soup.find_all("a", href=True)[:50]
            ],
        }
        return tool_response("scrape", {"url": req.url, "format": req.format, "content": content}, api_key)

    content = content[:req.max_chars]
    return tool_response("scrape", {"url": req.url, "format": req.format, "length": len(content), "content": content}, api_key)


# --- Tool 2: Email Validator ---
DISPOSABLE_DOMAINS = {
    "mailinator.com", "guerrillamail.com", "tempmail.com", "throwaway.email",
    "yopmail.com", "sharklasers.com", "guerrillamailblock.com", "grr.la",
    "dispostable.com", "trashmail.com", "maildrop.cc", "fakeinbox.com",
    "tempail.com", "temp-mail.org", "getnada.com", "mohmal.com",
    "mailnesia.com", "mailsac.com", "10minutemail.com", "minutemail.com",
    "emailondeck.com", "tempr.email", "discard.email", "tmpmail.net",
    "tmpmail.org", "binkmail.com", "safetymail.info", "filzmail.com",
    "trashmail.me", "trashmail.net", "mytemp.email", "mt2015.com",
    "thankyou2010.com", "trash-mail.com", "harakirimail.com", "bugmenot.com",
    "mailexpire.com", "tempinbox.com", "incognitomail.org", "mailcatch.com",
    "tempmailaddress.com", "jetable.org", "spamgourmet.com", "sneakemail.com",
    "mintemail.com", "crazymailing.com", "mailforspam.com", "spamavert.com",
    "spamfree24.org", "trashymail.com", "mailnull.com", "wh4f.org",
}

EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


class EmailRequest(BaseModel):
    email: str


@app.post("/tools/email-validate")
async def email_validate(req: EmailRequest, api_key: str = Depends(verify_api_key)):
    email = req.email.strip().lower()
    format_ok = bool(EMAIL_RE.match(email))

    domain = email.split("@")[-1] if "@" in email else None
    disposable = domain in DISPOSABLE_DOMAINS if domain else False

    mx_exists = False
    mx_records = []
    if domain and format_ok:
        try:
            answers = dns.resolver.resolve(domain, "MX", lifetime=5)
            mx_records = [str(r.exchange).rstrip(".") for r in answers]
            mx_exists = len(mx_records) > 0
        except Exception:
            pass

    return tool_response("email-validate", {
        "email": email,
        "valid": format_ok and mx_exists and not disposable,
        "format_ok": format_ok,
        "mx_exists": mx_exists,
        "mx_records": mx_records[:5],
        "domain": domain,
        "disposable": disposable,
    }, api_key)


# --- Tool 3: DNS Lookup ---
class DnsRequest(BaseModel):
    domain: str


@app.post("/tools/dns-lookup")
async def dns_lookup(req: DnsRequest, api_key: str = Depends(verify_api_key)):
    domain = req.domain.strip().lower()
    results = {}

    for rtype in ["A", "AAAA", "MX", "NS", "TXT", "CNAME"]:
        try:
            answers = dns.resolver.resolve(domain, rtype, lifetime=5)
            results[rtype] = [str(r).rstrip(".") for r in answers]
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.NoNameservers):
            results[rtype] = []
        except Exception:
            results[rtype] = []

    return tool_response("dns-lookup", {"domain": domain, "records": results}, api_key)


# --- Tool 4: Search (placeholder for Brave API) ---
class SearchRequest(BaseModel):
    query: str
    count: int = Field(default=5, ge=1, le=10)


@app.post("/tools/search")
async def search(req: SearchRequest, api_key: str = Depends(verify_api_key)):
    brave_key = os.getenv("BRAVE_API_KEY")
    if not brave_key:
        return tool_response("search", {
            "query": req.query,
            "count": req.count,
            "results": [],
            "note": "Search API ready. Configure BRAVE_API_KEY to enable live results.",
        }, api_key)

    try:
        resp = requests.get(
            "https://api.search.brave.com/res/v1/web/search",
            params={"q": req.query, "count": req.count},
            headers={"X-Subscription-Token": brave_key, "Accept": "application/json"},
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        results = [
            {"title": r.get("title"), "url": r.get("url"), "snippet": r.get("description")}
            for r in data.get("web", {}).get("results", [])
        ]
    except Exception as e:
        results = []
        logger.warning(f"Brave search failed: {e}")

    return tool_response("search", {"query": req.query, "count": req.count, "results": results}, api_key)


# --- Tool 5: Format Converter ---
class ConvertRequest(BaseModel):
    content: str
    from_format: str = Field(pattern="^(html|markdown|text)$")
    to_format: str = Field(pattern="^(html|markdown|text)$")


@app.post("/tools/convert")
async def convert(req: ConvertRequest, api_key: str = Depends(verify_api_key)):
    if req.from_format == req.to_format:
        output = req.content
    elif req.from_format == "html" and req.to_format == "markdown":
        output = markdownify.markdownify(req.content)
    elif req.from_format == "html" and req.to_format == "text":
        soup = BeautifulSoup(req.content, "html.parser")
        output = soup.get_text(separator="\n", strip=True)
    elif req.from_format == "markdown" and req.to_format == "html":
        output = md_lib.markdown(req.content)
    elif req.from_format == "markdown" and req.to_format == "text":
        html = md_lib.markdown(req.content)
        soup = BeautifulSoup(html, "html.parser")
        output = soup.get_text(separator="\n", strip=True)
    elif req.from_format == "text" and req.to_format == "html":
        output = "<p>" + req.content.replace("\n\n", "</p><p>").replace("\n", "<br>") + "</p>"
    elif req.from_format == "text" and req.to_format == "markdown":
        output = req.content  # Text is already valid markdown
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported conversion: {req.from_format} -> {req.to_format}")

    return tool_response("convert", {
        "from": req.from_format,
        "to": req.to_format,
        "input_length": len(req.content),
        "output_length": len(output),
        "content": output,
    }, api_key)


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)
