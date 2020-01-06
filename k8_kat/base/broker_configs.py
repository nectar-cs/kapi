import os
from utils.utils import Utils

prod_defaults = dict(
  auth_type='in',
)

dev_defaults = dict(
  auth_type='out',
  sa_name='nectar-dev',
  sa_ns='nectar',
  kubectl='kubectl',
  crb_name='nectar',
  cluster_name='dev'
)

test_defaults = dict(
  auth_type='out',
  sa_name='nectar-test',
  sa_ns='nectar',
  kubectl='microk8s.kubectl',
  crb_name='nectar-ci',
  cluster_name='test'
)

defaults = None
if Utils.run_env() == 'production':
  defaults = dev_defaults
elif Utils.run_env() == 'development':
  defaults = dev_defaults
elif Utils.run_env() == 'test':
  defaults = dev_defaults
else:
  print(f"[kube_broker] WARN unknown env {Utils.run_env()}")

val = lambda env, key: os.environ.get(env, defaults.get(key))

default_config = dict(
  auth_type=val('CONNECT_AUTH_TYPE', 'auth_type'),
  sa_name=val('CONNECT_SA_NAME', 'sa_name'),
  sa_ns=val('CONNECT_SA_NS', 'sa_ns'),
  crb_name=val('CONNECT_CRB_NAME', 'cbr_name'),
  kubectl=val('CONNECT_KUBECTL', 'kubectl'),
  cluster_name=os.environ.get('CONNECT_CLUSTER', 'dev')
)
