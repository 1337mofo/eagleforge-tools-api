import requests, json
TOKEN = open(r"C:\Users\ADMIN\.openclaw\workspace\agentdirectory.exchange\RAILWAY_API_TOKEN.txt").read().strip()
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
SERVICE_ID = "37494c87-1943-43a3-a2a2-1021f02aec78"
ENV_ID = "8c2d2a68-c760-4a39-b5bf-9c53e4900d0f"

r = requests.post("https://backboard.railway.com/graphql/v2", headers=HEADERS,
    json={"query": f'mutation {{ serviceInstanceRedeploy(serviceId: "{SERVICE_ID}", environmentId: "{ENV_ID}") }}'})
print("Redeploy:", json.dumps(r.json(), indent=2))
