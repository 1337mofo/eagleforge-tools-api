"""Check deployment logs."""
import requests, json

TOKEN = open(r"C:\Users\ADMIN\.openclaw\workspace\agentdirectory.exchange\RAILWAY_API_TOKEN.txt").read().strip()
DEPLOYMENT_ID = "e97f36bc-be96-4547-8850-f30c26f52d9b"
URL = "https://backboard.railway.com/graphql/v2"
HEADERS = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}

def gql(query, variables=None):
    body = {"query": query}
    if variables:
        body["variables"] = variables
    r = requests.post(URL, headers=HEADERS, json=body)
    return r.json()

result = gql("""query($id: String!) {
    deployment(id: $id) {
        id status
        buildLogs(limit: 30) 
    }
}""", {"id": DEPLOYMENT_ID})
print(json.dumps(result, indent=2))
