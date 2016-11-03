from tornado.web import HTTPError
from tornado import gen
import pprint

from dockerspawner import SystemUserSpawner
from .QueryUser import query_user

import os

def comma_split(x):
    return [item.strip() for item in x.split(',')]

class L41NbSpawner(SystemUserSpawner):
    container_image = os.environ["CONTAINER_IMAGE"]
    base_port = 10000
    base_mod = 1000
    remove_containers = True

    extra_host_config = {"network_mode": "host"}
    # Dictionary of paths to mount inside container
    volumes = os.environ['JH_MIRROR_MOUNTS'] 
    volumes = { path : path for path in comma_split(volumes) }

    def get_notebook_port(self):
        port = (int(self.user_id) % self.base_mod) + int(self.base_port)
        return port

    @gen.coroutine
    def get_ip_and_port(self):
        resp = yield self.docker('inspect_container', self.container_id)
        port = str(self.get_notebook_port())
        pprint.pprint(resp)
        ip = resp["HostConfig"]["PortBindings"]["%s/tcp" % port][0]["HostIp"]
        ip = resp['Node']['IP']

        print ('****************************************** IP:%s PORT:%s\n' %(str(ip),str(port)))    
        return ip, port

    def get_env(self):
        env = super(L41NbSpawner, self).get_env()

        port = self.get_notebook_port()
        self.extra_host_config.update({
            "port_bindings": {
                int(port) : None,
            }
        })
        self.extra_create_kwargs = {"ports": [int(port)]}
        env.update(dict(
            CONTAINER_NAME=self.container_name,
            NOTEBOOK_PORT=port,
        ))

        pyspark_submit_args=[]
        for l41_evar in os.environ:
            if l41_evar.lower().startswith("l41"):
                env[l41_evar] = os.environ[l41_evar]
                pyspark_submit_args.append("--conf spark.executorEnv.%s=%s"%(l41_evar, os.environ[l41_evar]))
        env['PYSPARK_SUBMIT_ARGS'] = " ".join(pyspark_submit_args)
        return env

    def _user_id_default(self):
        """
        Query the REST user client running on a local socket.
        """
        response = query_user(self.user.name)
        if "uid" not in response:
            raise HTTPError(403)
        return response['uid']
