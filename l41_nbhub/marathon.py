import os
import pprint
import requests
import socket
from copy import deepcopy


container_type = 'docker'

default_container = {
    "volumes": [],
    container_type: {
      "network": "BRIDGE",
      "portMappings":[ ]
    }
  }

default_request = {
  "cpus": 1,
  "disk": 0,
  "instances": 1,
  "constraints": []
}

class Marathon:
    def __init__(self, hostname):
        self.hostname = hostname

    def _make_request(self, type, endpoint, data=None, json_data=None):
        url = os.path.join(self.hostname, endpoint)
        if type.lower() == 'get':
            return requests.get(url)
        elif type.lower() == 'post':
            r = requests.post(url, json=json_data)
            return r
        elif type.lower() == 'delete':
            return requests.delete(url)


    def start_container(self,
                        container_name,
                        image_name,
                        entry_point,
                        env={},
                        constraints=[],
                        parameters= [{}],
                        resources=None,
                        mem_limit=128,
                        volumes=[],
                        ports=[],
                        network_mode='BRIDGE'):
        new_request = deepcopy(default_request)
        if container_name.startswith('/'):
            new_request['id'] = container_name
        else:
            new_request['id'] = '/' + container_name

        if len(entry_point.strip()) > 0:
            new_request['cmd'] = entry_point
        new_request['mem'] = mem_limit
        new_request['env'] = {}
        new_request['constraints'] = constraints
        for key in env:
            new_request['env'][key] = env[key]

        new_container = deepcopy(default_container)
        if container_type == 'docker':
            new_container['docker']['image'] = image_name
            new_container['docker']['parameters'] = parameters
        else:
            new_container['mesos']['image']['type'] = 'DOCKER'
            new_container['mesos']['image']['docker'] = {'name':image_name}

        # Map Volumes
        for item in volumes:
            if isinstance(item, tuple):
                hostPath = item[0]
                containerPath = item[1]
            else:
                hostPath = item
                containerPath = item

            volume = {
                'containerPath': containerPath,
                'hostPath': hostPath,
                'mode': 'RW'
            }
            new_container['volumes'].append(volume)

        # Map Ports
        for item in ports:
            new_port = {
                'containerPort': item,
                'hostPort': 0
            }
            new_container['docker']['portMappings'].append(new_port)

        new_container['docker']['network'] = network_mode
        new_request['container'] = new_container
        pprint.pprint(new_request)
        response = self._make_request('POST', 'v2/apps', json_data=new_request)
        if response.status_code == 201:
            return None
        else:
            raise ValueError(response.text)

    def stop_container(self, container_name):
        response = self._make_request('DELETE', 'v2/apps/%s'%container_name)
        if response.status_code == 200:
            return None
        else:
            raise ValueError(response.text)

    def get_ip_and_port(self, container_name):
        response = self._make_request('GET', 'v2/apps/%s'%container_name)
        if response.status_code != 200:
            return None
        container = response.json()['app']

        # There should only be one instance of our container
        assert len(container['tasks']) == 1
        running_task = container['tasks'][0]

        hostname =running_task['host']
        # Resolve hostname to ip
        ip = socket.gethostbyname(hostname)

        return (ip, running_task['ports'][0])

    def get_container_status(self, container_name):
        response = self._make_request('GET', 'v2/apps/%s'%container_name)
        if response.status_code != 200:
            return None
        container = response.json()['app']
        return container

    def get_running_containers(self):
        response = self._make_request('GET', 'v2/apps')
        return response.json()['apps']

