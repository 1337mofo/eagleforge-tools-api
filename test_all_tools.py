"""Full test of all 5 EagleForge tools."""
import requests, json

BASE = "https://eagleforge-tools-api-production.up.railway.app"
HEADERS = {"x-api-key": "eagle-demo-key-2026", "Content-Type": "application/json"}

def test(name, method, path, payload=None):
    print(f"\n{'='*50}")
    print(f"TEST: {name}")
    print(f"{'='*50}")
    try:
        if method == "GET":
            r = requests.get(f"{BASE}{path}", headers=HEADERS, timeout=15)
        else:
            r = requests.post(f"{BASE}{path}", json=payload, headers=HEADERS, timeout=15)
        print(f"Status: {r.status_code}")
        data = r.json()
        print(json.dumps(data, indent=2)[:600])
        return r.status_code == 200
    except Exception as e:
        print(f"ERROR: {e}")
        return False

results = []
results.append(("Health", test("Health Check", "GET", "/health")))
results.append(("Pricing", test("Pricing", "GET", "/pricing")))
results.append(("Scrape", test("Web Scraper", "POST", "/tools/scrape", 
    {"url": "https://httpbin.org/html", "format": "text", "max_chars": 500})))
results.append(("Email", test("Email Validator", "POST", "/tools/email-validate",
    {"email": "steve@theaerie.ai"})))
results.append(("DNS", test("DNS Lookup", "POST", "/tools/dns-lookup",
    {"domain": "agentdirectory.exchange"})))
results.append(("Search", test("Search", "POST", "/tools/search",
    {"query": "AI agent marketplace", "count": 3})))
results.append(("Convert", test("Format Converter", "POST", "/tools/convert",
    {"content": "# Hello World\n\nThis is **bold** text.", "from_format": "markdown", "to_format": "html"})))

print(f"\n{'='*50}")
print("RESULTS SUMMARY")
print(f"{'='*50}")
for name, passed in results:
    print(f"  {name}: {'PASS' if passed else 'FAIL'}")
print(f"\n{sum(1 for _,p in results if p)}/{len(results)} passed")
