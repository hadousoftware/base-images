#TAG=x
TAG="${TAG:=edge}"

docker build --pull -f Dockerfile -t hadou.io/base/abi:${TAG} .
docker push hadou.io/base/abi:${TAG}
echo "Done building ${TAG}"
