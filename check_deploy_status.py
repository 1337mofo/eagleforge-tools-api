import requests, json
TOKEN = open(r"C:\Users\ADMIN\.openclaw\workspace\agentdirectory.exchange\RAILWAY_API_TOKEN.txt").read().strip()
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
SERVICE_ID = "37494c87-1943-43a3-a2a2-1021f02aec78"

r = requests.post("https://backboard.railway.com/graphql/v2", headers=HEADERS,
    json={"query": f'query {{ service(id: "{SERVICE_ID}") {{ name deployments(first: 5) {{ edges {{ node {{ id status createdAt }} }} }} }} }}'})
print(json.dumps(r.json(), indent=2))
