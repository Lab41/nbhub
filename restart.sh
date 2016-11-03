#!/bin/bash
docker kill jupyterhub
docker rm jupyterhub
docker build -t lab41/nbhub .
docker run -it -p 8000:8000 -p 8001:8001 -p 8081:8081 -p 443:443 \
    -d --name jupyterhub -v ~/nbhub/super:/opt/super \
    -v ~/nbhub/docker_mnt:/docker_mnt -v /usr/local/etc/certs/:/certs \
    -v /var/run/docker.sock:/var/run/docker.sock \
    -v /var/run/restuser.sock:/var/run/restuser.sock \
    --env-file env.gpu -v /log:/log -v /home:/home \
    -v /usr/local/resources:/resources lab41/nbhub
