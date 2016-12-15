from collections import defaultdict
import json
import os


class GPUResourceAllocator:
    """
    Quick and dirty class to manage GPU allocations. Uses flat files which are read at each instance

    """
    def __init__(self, resource_filename, status_filename, allow_oversubscription=True):
        """
        Initialize GPUResourceAllocator
        Args:
            resource_filename: Filename of a text file of the format "hostname #gpus\n hostname #gpus"
            status_filename: A json object of the format {username:(hostname,gpuid)}

        Returns:

        """
        self.resource_filename = resource_filename
        self.status_filename = status_filename
        self.allow_oversubscription = allow_oversubscription
    
    def get_resources(self):
        """
        Gets the available resources from the specified text file
        Returns:
            resources: A list of the available resources, tuple of (hostname, number of gpus)
        """
        self.driver_versions = {}
        resources = []
        with open(self.resource_filename) as input_file:
            for line in input_file:
                line = line.split()
                # 0=hostname, 1=number of gpus, 2=driver version
                resources.append((line[0], int(line[1])))
                if len(line) > 1:
                    self.driver_versions[line[0]] = line[2]
        return resources

    def get_driver_version(self, hostname):
        if hostname in self.driver_versions:
            return self.driver_versions[hostname]
        else:
            return None

    def get_current_allocations(self):
        """
        Get the current state of gpu allocations
        Returns:
            current_allocations: A dictionary of the format {username:(hostname,gpuid)}
        """
        if not os.path.exists(self.status_filename):
            with open(self.status_filename, 'w') as fOut:
                json.dump({}, fOut, indent=4)
            
        # user:{[(host,id)]}
        current_allocations = json.load(open(self.status_filename))
        return current_allocations
    
    def save_current_allocations(self, current_allocations):
        """
        Save the current state of gpu allocations
        Args:
            current_allocations: A dictionary of the format {username:(hostname,gpuid)}
        """
        with open(self.status_filename, 'w') as fOut:
            json.dump(current_allocations, fOut, indent=4)

    @staticmethod
    def get_lowest_available_id(current_usage, max_available):
        for i in range(max_available):
            if i not in current_usage:
                return i
        raise ValueError('Should never get here')
        
    def get_host_id(self, desired_username):
        """
        Returns the hostname/id to assign a given user
        Args:
            desired_username: the username to allocate resources for

        Returns:
            (Hostname, GPU_ID): Tuple of resources to be assigned
        """
        resources = self.get_resources()
        current_allocations = self.get_current_allocations()

        # If we've already assigned resources
        if desired_username in current_allocations:
            return current_allocations[desired_username]
        
        current_usage_by_resource = defaultdict(set)
        for username in current_allocations:
            hostname, gpu_id = current_allocations[username]
            current_usage_by_resource[hostname].add(gpu_id)
        
        for hostname, available_resources in resources:
            if len(current_usage_by_resource[hostname]) < available_resources:
                # Find host to assign to
                host = hostname
                gpu_id = self.get_lowest_available_id(current_usage_by_resource[hostname], available_resources)
                
                # Assign host to be used
                current_allocations[desired_username] = (host, gpu_id)
                
                # write file
                self.save_current_allocations(current_allocations)
                return current_allocations[desired_username]
            
        raise ValueError('No resources available to fufill request')
    
    def release_resource(self, desired_username):
        """
        Return the resources for a given user to the pool
        Args:
            desired_username: username to return resources for

        Returns:

        """
        current_allocations = self.get_current_allocations()
        if desired_username in current_allocations:
            del current_allocations[desired_username]
        
        self.save_current_allocations(current_allocations)
