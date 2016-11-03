FROM jupyter/jupyterhub
MAINTAINER Lab41

# Update apt-get
RUN apt-get -y update

# Install Docker (see https://docs.docker.com/engine/installation/linux/debian/)
RUN apt-get -y install apt-transport-https ca-certificates && \
    apt-key adv --keyserver hkp://p80.pool.sks-keyservers.net:80 --recv-keys 58118E89F3A912897C070ADBF76221572C52609D && \
    mkdir -p /etc/apt/sources.list.d/ && \
    echo "deb https://apt.dockerproject.org/repo debian-jessie main" > /etc/apt/sources.list.d/docker.list && \
    apt-get update && \
    apt-cache policy docker-engine && \
    apt-get -y install docker-engine

# Install Ganymede Hub + dependencies
RUN git clone https://github.com/jupyter/dockerspawner.git /srv/dockerspawner && \
    pip install /srv/dockerspawner/. && \
    rm -rf /srv/dockerspawner && \
    git clone https://github.com/jupyter/oauthenticator.git /srv/oauthenticator && \
    pip install /srv/oauthenticator/. && \
    rm -rf /srv/oauthenticator


# nopleats logging stuf
RUN apt-get install -y \
    socat \
    rsyslog \
    sudo \
    vim

# Install Mustache templater for replacing variables
RUN cd /opt/ && \
    git clone https://github.com/Lab41/mo.git && \
    ln -s /opt/mo/mo /usr/bin/mo

# Install filebeat
RUN apt-get install -y curl apt-transport-https ca-certificates && \
    cd /tmp && \
    curl -Ls -O https://download.elastic.co/beats/filebeat/filebeat_1.2.0_amd64.deb && \
    dpkg -i filebeat_1.2.0_amd64.deb && \
    rm filebeat_1.2* && \
    mkdir -p /opt/nopleats && \
    mkdir -p /opt/super && \
    mkdir -p /opt/user

COPY . /srv/ganymede_hub
RUN pip install /srv/ganymede_hub/. && \
    rm -rf /srv/ganymede_hub

# add in the helper files
ADD nopleats/* /opt/nopleats/
ADD super/* /opt/super/
ADD user/* /opt/user/

# /opt/nopleats/start_user.sh is the entry point..
# after running it you will be the user defined in L41_USERNAME

ENTRYPOINT ["/opt/nopleats/start_user.sh"]

# Eventually we can use pip to install, but for now we must install through git (see above).
# The latest pypi release of oauthenticator is 0.2.0 from Jan 4, but we are using a feature (username_map) first introduced in commit a37ec45120e1058a19aee49707724c6b90470323 from Jan 7.
# Additionally, we are also relying on a change (_env_default -> get_env) in PR #84 of dockerspawner, which was merged on Mar 24 (the latest version on pypi is 0.2.0 from Feb 18).
#RUN pip install -r /srv/l41_nbhub/requirements.txt /srv/l41_nbhub/. && \
#    rm -rf /srv/l41_nbhub
