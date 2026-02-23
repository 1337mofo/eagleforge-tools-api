import requests, json
TOKEN = open(r"C:\Users\ADMIN\.openclaw\workspace\agentdirectory.exchange\RAILWAY_API_TOKEN.txt").read().strip()
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
q = 'query { deployment(id: "e97f36bc-be96-4547-8850-f30c26f52d9b") { id status } }'
r = requests.post("https://backboard.railway.com/graphql/v2", headers=HEADERS, json={"query": q})
print(json.dumps(r.json(), indent=2))
