import requests, json
TOKEN = open(r"C:\Users\ADMIN\.openclaw\workspace\agentdirectory.exchange\RAILWAY_API_TOKEN.txt").read().strip()
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}

q = """mutation {
    deploymentTriggerCreate(input: {
        serviceId: "37494c87-1943-43a3-a2a2-1021f02aec78"
        environmentId: "8c2d2a68-c760-4a39-b5bf-9c53e4900d0f"
    }) { id }
}"""
r = requests.post("https://backboard.railway.com/graphql/v2", headers=HEADERS, json={"query": q})
print(json.dumps(r.json(), indent=2))
