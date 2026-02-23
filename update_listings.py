"""Update tool listings in agentdirectory DB with live API URLs and code snippets."""
import psycopg2

conn = psycopg2.connect("postgresql://postgres:aRFnDbaXZvAaIKFgFBnpjRmzoanlwGkO@mainline.proxy.rlwy.net:11716/railway")
cur = conn.cursor()

API = "https://eagleforge-tools-api-production.up.railway.app"
REGISTER = f"{API}/auth/register"
DOCS = f"{API}/docs"

updates = {
    "@eagleforge/web-scraper": {
        "documentation_url": DOCS,
        "install_command": f'curl -X POST {API}/tools/scrape -H "X-API-Key: YOUR_KEY" -H "Content-Type: application/json" -d \'{{"url":"https://example.com","format":"markdown"}}\'',
    },
    "@eagleforge/email-validator": {
        "documentation_url": DOCS,
        "install_command": f'curl -X POST {API}/tools/email-validate -H "X-API-Key: YOUR_KEY" -H "Content-Type: application/json" -d \'{{"email":"test@example.com"}}\'',
    },
    "@eagleforge/dns-lookup": {
        "documentation_url": DOCS,
        "install_command": f'curl -X POST {API}/tools/dns-lookup -H "X-API-Key: YOUR_KEY" -H "Content-Type: application/json" -d \'{{"domain":"example.com"}}\'',
    },
    "@eagleforge/search": {
        "documentation_url": DOCS,
        "install_command": f'curl -X POST {API}/tools/search -H "X-API-Key: YOUR_KEY" -H "Content-Type: application/json" -d \'{{"query":"AI agents","count":5}}\'',
    },
    "@eagleforge/format-converter": {
        "documentation_url": DOCS,
        "install_command": f'curl -X POST {API}/tools/convert -H "X-API-Key: YOUR_KEY" -H "Content-Type: application/json" -d \'{{"content":"# Hello","from_format":"markdown","to_format":"html"}}\'',
    },
}

for pkg, data in updates.items():
    cur.execute(
        "UPDATE tools SET documentation_url=%s, install_command=%s, updated_at=NOW() WHERE package_name=%s",
        (data["documentation_url"], data["install_command"], pkg),
    )
    print(f"Updated: {pkg}")

conn.commit()
cur.close()
conn.close()
print(f"\nAll {len(updates)} tool listings updated with live API URLs and code snippets.")
print(f"API docs: {DOCS}")
print(f"Register: {REGISTER}")
