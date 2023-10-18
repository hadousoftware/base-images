#!/bin/zsh -x
DOCKER_REPO=gcr.io/hadou-ops-tools/abi
BASE_IMAGE=${DOCKER_REPO}:edge

#TAG=x
TAG="${TAG:=runtime}"

BASE_IMAGE_TAR=base.tar
RUNTIME_TAR=runtime.tar.gz

TMP_DIR=tmp

# Get base image
docker rmi -f ${BASE_IMAGE} || exit 1
docker pull ${BASE_IMAGE} || exit 1

# Extract layer.tar
mkdir ${TMP_DIR}
docker save ${BASE_IMAGE} | gzip > ${BASE_IMAGE_TAR} || exit 1
tar --same-owner -C ${TMP_DIR} -xf ./${BASE_IMAGE_TAR} || exit 1

cd ${TMP_DIR} || exit 1
FIRST_DIR=$(ls -d */|head -n 1)
LAYER_TAR=${FIRST_DIR}layer.tar

mv "${LAYER_TAR}" ../${BASE_IMAGE_TAR}
cd .. || exit 1

rm -rf ${TMP_DIR} && mkdir ${TMP_DIR}
tar --same-owner -C ${TMP_DIR} -xf ./${BASE_IMAGE_TAR} || exit 1

# Remove unnecessary stuff
cd ${TMP_DIR} || exit 1
# Removing apk
rm -rf etc/apk && rm -rf lib/apk && rm -rf lib/libapk.so.3.12.0 && rm -f sbin/apk
rm -rf usr/share/apk && rm -rf var/cache/apk
# Stuff that never should be used
rm -rf media && rm -rf mnt
# Other stuff
rm -rf etc/profile.d && rm -f usr/bin/getconf && rm -f usr/bin/iconv

# Replace busybox with true (remove shell)
cp ../true bin/busybox

# Creating runtime tar
tar -czf ${RUNTIME_TAR} ./* || exit 1
cd ..
mv ${TMP_DIR}/"${RUNTIME_TAR}" . || exit 1

# Creating Docker image
docker build -f Dockerfile -t ${DOCKER_REPO}:${TAG} . || exit 1

# Cleanup
rm -rf ${TMP_DIR}
rm -rf ${BASE_IMAGE_TAR}
rm -rf ${RUNTIME_TAR}

# Ship it
docker push ${DOCKER_REPO}:${TAG}
