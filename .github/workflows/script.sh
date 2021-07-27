TOKEN=$1

echo "** Fetching kubeconfig from Linode"

# Create .kube directory if not exists
mkdir -p $HOME/.kube

# Run python script to fetch kubeconfig
python3 ${GITHUB_WORKSPACE}/.github/workflows/kubeconfig.py $TOKEN

# Decode and add kubeconfig file
cat ${GITHUB_WORKSPACE}/config | base64 -d > $HOME/.kube/config

# Create test pod
echo "** Creating pod"
kubectl apply -f manifests/trader.Deployment.yaml