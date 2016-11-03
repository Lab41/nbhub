export PATH=$PATH:/opt/conda/bin/
jupyterhub --config=/srv/jupyterhub/jupyterhub_config.py --port 443 --ssl-key $SSL_KEY --ssl-cert $SSL_CERT 
