import requests, json

TOKEN = open(r"C:\Users\ADMIN\.openclaw\workspace\agentdirectory.exchange\RAILWAY_API_TOKEN.txt").read().strip()
URL = "https://backboard.railway.com/graphql/v2"
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
SERVICE_ID = "37494c87-1943-43a3-a2a2-1021f02aec78"
ENV_ID = "8c2d2a68-c760-4a39-b5bf-9c53e4900d0f"

def gql(query, variables=None):
    r = requests.post(URL, headers=HEADERS, json={"query": query, **({"variables": variables} if variables else {})})
    return r.json()

# Check service source config
print("Service info:")
result = gql(f'query {{ service(id: "{SERVICE_ID}") {{ name source {{ repo branch }} }} }}')
print(json.dumps(result, indent=2))

# Try deployment create
print("\nCreating deployment...")
result = gql("""mutation($input: DeploymentTriggerInput!) {
    deploymentTriggerCreate(input: $input) { id }
}""", {"input": {"serviceId": SERVICE_ID, "environmentId": ENV_ID}})
print(json.dumps(result, indent=2))
