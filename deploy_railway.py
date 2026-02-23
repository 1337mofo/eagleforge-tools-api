"""Deploy eagleforge-tools-api to Railway as a new service."""
import requests
import json

TOKEN = open(r"C:\Users\ADMIN\.openclaw\workspace\agentdirectory.exchange\RAILWAY_API_TOKEN.txt").read().strip()
PROJECT_ID = "df459949-3d36-4601-afcc-e50869c28223"
REPO = "1337mofo/eagleforge-tools-api"
URL = "https://backboard.railway.com/graphql/v2"
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}

def gql(query, variables=None):
    body = {"query": query}
    if variables:
        body["variables"] = variables
    r = requests.post(URL, headers=HEADERS, json=body)
    return r.json()

# 1. Get production environment
print("Getting environments...")
result = gql("""query($id: String!) { 
    project(id: $id) { 
        environments { edges { node { id name } } } 
    } 
}""", {"id": PROJECT_ID})
print(json.dumps(result, indent=2))

envs = result.get("data", {}).get("project", {}).get("environments", {}).get("edges", [])
prod_env = None
for e in envs:
    if e["node"]["name"] == "production":
        prod_env = e["node"]["id"]
        break

if not prod_env:
    print("ERROR: No production environment found")
    exit(1)

print(f"Production env: {prod_env}")

# 2. Create service
print("Creating service...")
result = gql("""mutation($input: ServiceCreateInput!) {
    serviceCreate(input: $input) { id name }
}""", {"input": {
    "projectId": PROJECT_ID,
    "name": "eagleforge-tools-api",
    "source": {"repo": REPO}
}})
print(json.dumps(result, indent=2))

service_id = result.get("data", {}).get("serviceCreate", {}).get("id")
if not service_id:
    print("ERROR: Failed to create service")
    exit(1)

print(f"Service created: {service_id}")

# 3. Set environment variables
print("Setting env vars...")
result = gql("""mutation($input: VariableCollectionUpsertInput!) {
    variableCollectionUpsert(input: $input)
}""", {"input": {
    "projectId": PROJECT_ID,
    "environmentId": prod_env,
    "serviceId": service_id,
    "variables": {
        "VALID_API_KEYS": "eagle-demo-key-2026,eagle-prod-key-001",
        "PORT": "8000"
    }
}})
print("Env vars set:", json.dumps(result, indent=2))

print("\nDONE! Service should auto-deploy from GitHub repo.")
print(f"Repo: https://github.com/{REPO}")
print(f"Service ID: {service_id}")
