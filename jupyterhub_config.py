import os
import ast

c.JupyterHub.spawner_class = 'l41_nbhub.MarathonSpawner.MarathonSpawner'
c.JupyterHub.authenticator_class = 'l41_nbhub.L41OAuthenticator.L41OAuthenticator'

c.Authenticator.admin_users = [name.strip() for name in os.environ['JH_ADMIN_USERS'].split(",")]

c.GitHubOAuthenticator.oauth_callback_url = os.environ['OAUTH_CALLBACK_URL']
c.GitHubOAuthenticator.client_id = os.environ['GITHUB_CLIENT_ID']
c.GitHubOAuthenticator.client_secret = os.environ['GITHUB_CLIENT_SECRET']

c.JupyterHub.hub_ip = os.environ['HUB_IP']

c.L41OAuthenticator.username_map_file=os.environ['JH_USERNAME_MAP']

c.MarathonSpawner.mem_limit = os.environ['JH_MEM_LIMIT']
c.MarathonSpawner.hub_ip_connect = os.environ['HUB_IP']
c.MarathonSpawner.volumes = [os.environ['JH_MNT_VOLUME']
c.MarathonSpawner.home_basepath = os.environ['JH_HOME_BASEPATH']
c.MarathonSpawner.marathon_host = os.environ['MARARTHON_API_ENDPOINT']
c.MarathonSpawner.docker_image_name = 'lab41/tensorflow-notebook'
c.MarathonSpawner.resource_file_name = os.environ['JH_RESOURCE_FILENAME']
c.MarathonSpawner.status_file_name = os.environ['JH_STATUS_FILENAME']
c.MarathonSpawner.env_url = os.environ['JH_NBSERVER_ENV_VARS_URI']
