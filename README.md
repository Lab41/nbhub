# L41 NB Hub

This project is a Lab41-customized version of a notebook hub and is meant to be used in tandem with the L41 NB Server. The entire hub is run from inside of a Docker container and acts as a proxy for the notebook servers which run in their own Docker containers.

This project is configured to further extend the [jupyterhub/dockerspawner](https://github.com/jupyterhub/dockerspawner) extension, as well as the [jupyterhub/oauthenticator](https://github.com/jupyterhub/oauthenticator) extension. The dockerspawner extension is responsible for starting the notebook servers in their own Docker containers, while oauthenticator handles Github Oauth..

## Setup (WIP)

Ensure that Docker is installed on the machine where you plan to run L41 NB Hub.

We will also need to run [kylemvz/restuser](https://github.com/kylemvz/restuser) on the hub machine. This is a local REST service exposed on a UNIX socket which the hub queries in order to determine UID/GID for a particular user. The UID and GID is passed on to the notebook server at creation time, which allows the notebook server to dynamically create the user with the proper UID/GID inside of its container.  kylemvz/restuser is a fork of [minrk/restuser](https://github.com/minrk/restuser), with a slight change to make the service query-only (the user will not be created if it does not exist). We assume ahead of time that the hub machine has been properly configured via CM to have all of the proper user accounts and consistent UIDs/GIDs across all machines involved with these Jupyter Docker containers.

After cloning this repository and cd'ing inside of the cloned directory, the next step is to build the container:

`
docker build -t lab41/nbhub .
`

Run with:

`
docker run -it -p 443:443 -p 8000:8000 -p 8001:8001 -p 8081:8081 \
--name ganymedehub -v /var/run/docker.sock:/var/run/docker.sock \
-v /var/run/restuser.sock:/var/run/restuser.sock --env-file env \
-v certs/:/certs -v docker_mnt:/docker_mnt \
-v super:/opt/super -v /log:/log -v /home:/home lab41/nbhub /bin/bash
`

You may need to change the env file to match your current configuration.
