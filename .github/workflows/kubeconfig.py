import requests, sys


try:
    token = sys.argv[1]
    headers = {'Authorization': 'Bearer ' + token}
except:
    print("Missing Linode token. Aborting.")
    sys.exit(1)



try:
    print("** Fetching clusters")
    response = requests.get("https://api.linode.com/v4/lke/clusters", headers=headers)
    if len(response.json()["data"]) > 1:
        print("ERROR: more than one cluster exists.")

except:
    print("Fetching clusters failed. Aborting.")
    sys.exit(1)

try:
    print("** Fetching kubeconfig")
    cluster_id = response.json()["data"][0]["id"]
    kubeconfig = requests.get(f"https://api.linode.com/v4/lke/clusters/{cluster_id}/kubeconfig", headers=headers)

except:
    print("Fetching kubeconfig failed. Aborting.")
    sys.exit(1)

with open("config", 'w') as h:
    print("** Writing config")
    h.write(kubeconfig.json()["kubeconfig"])