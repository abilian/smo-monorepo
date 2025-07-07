SMO_URL="http://127.0.0.1:8000"
REGISTRY_URL="http://127.0.0.1:5000"

curl -X POST "$SMO_URL/project/test/graphs" \
     -H "Content-Type: application/json" \
     --data '{"artifact": "'$REGISTRY_URL'/test/image-detection-graph"}'
