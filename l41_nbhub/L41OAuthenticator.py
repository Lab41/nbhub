from oauthenticator import GitHubOAuthenticator
import ast

class L41OAuthenticator(GitHubOAuthenticator):
    username_map_file = '/docker_mnt/username_map'

    # Dynamically recreate username_map from file so that we cam change it while Jupyter Hub is running.
    # If username_map_file is mounted inside of the JupyterHub Docker container, we can edit it from the host.
    def get_username_map(self):
        with open(self.username_map_file, 'r') as f:
            lines = f.read()
            username_map = ast.literal_eval(lines)
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
