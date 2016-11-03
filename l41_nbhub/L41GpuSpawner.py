from tornado.web import HTTPError
from tornado import gen
import pprint

import docker
import socket
from dockerspawner import SystemUserSpawner, DockerSpawner
from .QueryUser import query_user
from .L41NbSpawner import L41NbSpawner
from .GPUResourceAllocator import GPUResourceAllocator
import os

from textwrap import dedent
from traitlets import (
    Integer,
    Unicode,
)
def comma_split(x):
    return [item.strip() for item in x.split(',')]


clas s L41GpuSpawner(DockerSpawner):
    container_image = os.environ["CONTAINER_IMAGE"]
    gpu_resources = GPUResourceAllocator(os.environ['RESOURCE_FILENAME'],
                                         os.environ['STATUS_FILENAME'])
    hostname = None

    # Dictionary of paths to mount inside container
    volumes = os.environ['JH_MIRROR_MOUNTS']
    volumes = { path : path for path in comma_split(volumes) }
    _client = None

    user_id = Integer(-1,
        help=dedent(
            """
            If system users are being used, then we need to know their user id
            in order to mount the home directory.
            User IDs are looked up in two ways:
            1. stored in the state dict (authenticator can write here)
            2. lookup via pwd
            """
        )
    )

    @property
    def volume_binds(self):
        """
        The second half of declaring a volume with docker-py happens when you
        actually call start().  The required format is a dict of dicts that
        looks like:
        {
            host_location: {'bind': container_location, 'mode': 'rw'}
        }
        mode may be 'ro', 'rw', 'z', or 'Z'.
        """
        binds = self._volumes_to_binds(self.volumes, {})
        binds = self._volumes_to_binds(self.read_only_volumes, binds, mode='ro')
        return binds


    @property
    def client(self):
        """single global client instance"""
        cls = self.__class__
        if cls._client is None:
            cls._client = {}

        username = self.user.name
        if username not in cls._client:
            if self.use_docker_client_env:
                kwargs = kwargs_from_env(
                    assert_hostname=self.tls_assert_hostname
                )
                client = docker.Client(version='auto', **kwargs)
            else:
                if self.tls:
                    tls_config = True
                elif self.tls_verify or self.tls_ca or self.tls_client:
                    tls_config = docker.tls.TLSConfig(
                        client_cert=self.tls_client,
                        ca_cert=self.tls_ca,
                        verify=self.tls_verify,
                        assert_hostname=self.tls_assert_hostname)
                else:
                    tls_config = None

                hostname, gpu_id = self.gpu_resources.get_host_id(username)
                self.docker_host = hostname
                self.gpu_id = gpu_id
                client = docker.Client(base_url=self.docker_host, tls=tls_config, version='auto')
            cls._client[username] = client

        return cls._client[username]

    @gen.coroutine
    def get_ip_and_port(self):
        ip, port = yield super(L41GpuSpawner, self).get_ip_and_port()

        hostname = self.docker_host[:self.docker_host.find(':')]
        self.hostname = hostname
        ip = socket.gethostbyname(hostname)
        self.container_ip = ip
        #print("PORT: %s" % port)

        return ip, port #hostname, port

    def get_env(self):
        env = super(L41GpuSpawner, self).get_env()
        env.update(dict(
            USER=self.user.name,
            USER_ID=self.user_id,
            HOME="/home/%s" % self.user.name,
        ))
        port = 8888 
        self.extra_host_config.update({
            "port_bindings": {
                int(port): None,
            },
            "devices": [
                "/dev/nvidiactl:/dev/nvidiactl",
                "/dev/nvidia-uvm:/dev/nvidia-uvm",
                "/dev/nvidia{}:/dev/nvidia0".format(self.gpu_id)
            ]
        })

        self.extra_create_kwargs = {
            "ports": [int(port)],
            "working_dir": os.path.join(os.environ['JH_USER_HOME'], self.user.name),
        }
        env.update(dict(
            CONTAINER_NAME=self.container_name,
            NOTEBOOK_PORT=port,
            HOSTNAME=self.hostname,
        ))

        for l41_env_variable in os.environ:
            if l41_env_variable.lower().startswith("l41"):
                env[l41_env_variable] = os.environ[l41_env_variable]
        env['PYSPARK_SUBMIT_ARGS'] = " "
        pprint.pprint(os.environ)
        return env

    def stop(self, now=False):
        super(L41GpuSpawner, self).stop(now)
        username = os.environ['L41_USERNAME']
        self.gpu_resources.release_resource(username)

    def _user_id_default(self):
        """
        Query the REST user client running on a local socket.
        """
        response = query_user(self.user.name)
        if "uid" not in response:
            raise HTTPError(403)
        return response['uid']
