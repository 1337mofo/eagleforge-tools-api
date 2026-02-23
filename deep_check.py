import requests, json
TOKEN = open(r"C:\Users\ADMIN\.openclaw\workspace\agentdirectory.exchange\RAILWAY_API_TOKEN.txt").read().strip()
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
DEP_ID = "01189105-0b15-4dc4-be5c-7037d56e445a"

# Check deployment details including meta
r = requests.post("https://backboard.railway.com/graphql/v2", headers=HEADERS,
    json={"query": f'query {{ deployment(id: "{DEP_ID}") {{ id status url staticUrl canRedeploy meta }} }}'})
print(json.dumps(r.json(), indent=2))
