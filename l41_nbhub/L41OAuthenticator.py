from oauthenticator import GitHubOAuthenticator
from urllib.parse import urlparse
import requests
import json
from traitlets import Unicode
#import ast

class L41OAuthenticator(GitHubOAuthenticator):
    username_map_file = Unicode('/docker_mnt/username_map',
                         help="File or URI containing mapping of Github user names to local user names",
                         config=True)

    # Check if file or URI
    def is_uri(self, filename):
        parse_result = urlparse(filename)
        print('Name: ', filename)
        print('Parse_result:', parse_result)
        if len(parse_result.scheme) > 0 and len(parse_result.netloc) > 0:
            return True
        else:
            return False

    # Dynamically recreate username_map from file so that we cam change it while Jupyter Hub is running.
    # If username_map_file is mounted inside of the JupyterHub Docker container, we can edit it from the host.
    def get_username_map(self):
        if self.is_uri(self.username_map_file):
            return requests.get(self.username_map_file, verify=False).json()
        else:
            with open(self.username_map_file, 'r') as f:
                return json.load(f)
                # lines = f.read()
                # username_map = ast.literal_eval(lines)
            return username_map

    # At this point, username has already gone through normalize_username().
    def check_whitelist(self, username):
        check_super = super(L41OAuthenticator, self).check_whitelist(username)
        username_map = self.get_username_map()
        return check_super and (username in username_map.values())

    def normalize_username(self, username):
        """Normalize a username.
        
        Override in subclasses if usernames should have some normalization.
        Default: cast to lowercase, lookup in username_map.
        """
        #username = username.lower()
        username_map = self.get_username_map()
        username = username_map.get(username, username)
        return username
