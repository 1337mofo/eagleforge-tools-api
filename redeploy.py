"""Cancel stuck deploy and redeploy."""
import requests, json

TOKEN = open(r"C:\Users\ADMIN\.openclaw\workspace\agentdirectory.exchange\RAILWAY_API_TOKEN.txt").read().strip()
URL = "https://backboard.railway.com/graphql/v2"
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
SERVICE_ID = "37494c87-1943-43a3-a2a2-1021f02aec78"
ENV_ID = "8c2d2a68-c760-4a39-b5bf-9c53e4900d0f"

def gql(query, variables=None):
    body = {"query": query}
    if variables:
        body["variables"] = variables
    r = requests.post(URL, headers=HEADERS, json=body)
    return r.json()

# Cancel stuck deployment
print("Cancelling stuck deploy...")
result = gql("""mutation { deploymentRemove(id: "e97f36bc-be96-4547-8850-f30c26f52d9b") }""")
print(json.dumps(result, indent=2))

# Trigger new deployment
print("Triggering redeploy...")
result = gql("""mutation($serviceId: String!, $environmentId: String!) {
    serviceInstanceRedeploy(serviceId: $serviceId, environmentId: $environmentId)
}""", {"serviceId": SERVICE_ID, "environmentId": ENV_ID})
print(json.dumps(result, indent=2))
