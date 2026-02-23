"""Check deployment status and get URL."""
import requests, json, time

TOKEN = open(r"C:\Users\ADMIN\.openclaw\workspace\agentdirectory.exchange\RAILWAY_API_TOKEN.txt").read().strip()
PROJECT_ID = "df459949-3d36-4601-afcc-e50869c28223"
SERVICE_ID = "37494c87-1943-43a3-a2a2-1021f02aec78"
URL = "https://backboard.railway.com/graphql/v2"
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}

def gql(query, variables=None):
    body = {"query": query}
    if variables:
        body["variables"] = variables
    r = requests.post(URL, headers=HEADERS, json=body)
    return r.json()

# Check deployments
result = gql("""query($id: String!) {
    service(id: $id) {
        name
        serviceInstances { edges { node { 
            domains { serviceDomains { domain } customDomains { domain } }
        } } }
        deployments(first: 3) { edges { node { id status createdAt } } }
    }
}""", {"id": SERVICE_ID})
print(json.dumps(result, indent=2))
