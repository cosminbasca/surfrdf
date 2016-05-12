#!/bin/bash

cd "$(dirname ${0})"

cp Dockerfile Dockerfile.orig
sed -i 's,^ENV TOX_USER_ID=.*\$,ENV TOX_USER_ID='$UID',g' Dockerfile

docker build -t surf-tox . && \
if [ -d ".tox" ]; then
    docker run --rm --entrypoint="tox" -v "$(pwd)/.tox:/src/.tox" surf-tox "${@}"
else
    docker run --rm --entrypoint="tox" surf-tox "${@}"
fi

mv Dockerfile.orig Dockerfile

cd -
