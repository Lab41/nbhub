import os
import ast

c.JupyterHub.spawner_class = 'l41_nbhub.L41NbSpawner.L41NbSpawner'
c.JupyterHub.authenticator_class = 'l41_nbhub.L41OAuthenticator.L41OAuthenticator'

c.Authenticator.admin_users = [name.strip() for name in os.environ['JH_ADMIN_USERS'].split(",")]

c.GitHubOAuthenticator.oauth_callback_url = os.environ['OAUTH_CALLBACK_URL']
c.GitHubOAuthenticator.client_id = os.environ['GITHUB_CLIENT_ID']
c.GitHubOAuthenticator.client_secret = os.environ['GITHUB_CLIENT_SECRET']

c.JupyterHub.hub_ip = os.environ['HUB_IP']

c.DockerSpawner.hub_ip_connect = os.environ['HUB_IP_CONNECT']
c.DockerSpawner.use_internal_ip = ast.literal_eval(os.environ['USE_INTERNAL_IP'])

