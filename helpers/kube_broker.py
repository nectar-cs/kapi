import base64
import os
import json
from kubernetes import config, client
import subprocess
import urllib3

from utils.utils import Utils


class BrokerConnException(Exception):
  def __init__(self, message):
    super().__init__(message)

class KubeBroker:

  def __init__(self):
    self.is_connected = False
    self.last_error = None
    self.coreV1 = None
    self.appsV1Api = None
    self.client = None
    self.auth_type = None

  def connect(self, force_type=None):
    self.auth_type = force_type or self.env_auth_type('remote')
    is_local = self.auth_type == 'local'
    connect = self.in_cluster_connect if is_local else self.out_cluster_connect
    self.is_connected = connect()

    if self.is_connected:
      self.auth_type = self.auth_type
      self.client = client
      self.coreV1 = client.CoreV1Api()
      self.appsV1Api = client.AppsV1Api()

    return self.is_connected

  def in_cluster_connect(self):
    try:
      config.load_incluster_config()
      return True
    except Exception as e:
      print(f"[KubeBroker] In-cluster auth Failed: {e}")
      self.last_error = e
      return False

  def out_cluster_connect(self):
    if self.connect_with_token():
      return True
    else:
      print(f"[KubeBroker] Falling back to kube config auth")
      return self.connect_with_kube_config()

  def connect_with_kube_config(self):
    try:
      config.load_kube_config()
      return True
    except Exception as e:
      self.last_error = e
      print(f"[KubeBroker] Kube config auth failed: {e}")
      return False

  def connect_with_token(self):
    try:
      print(f"[KubeBroker] Cred discovery with for token auth")
      user_token = KubeBroker.read_target_cluster_user_token()
      configuration = client.Configuration()
      configuration.host = KubeBroker.read_target_cluster_ip()
      configuration.verify_ssl = False
      configuration.debug = False
      configuration.api_key = {"authorization": f"Bearer {user_token}"}
      client.Configuration.set_default(configuration)
      urllib3.disable_warnings()
      print(f"[KubeBroker] Cred discovered success for token auth")
      return True
    except Exception as e:
      print(f"[KubeBroker] Cred discovered success for token auth: {e}")
      self.last_error = e
      return False

  @staticmethod
  def kubectl():
    return 'kubectl' if Utils.is_dev() else 'microk8s.kubectl'

  @staticmethod
  def read_target_cluster_ip():
    k = KubeBroker.kubectl()
    local_config = KubeBroker.jcmd(f"{k} config view -o json")
    clusters = local_config['clusters']
    target = 'nectar-dev' if Utils.is_dev() else 'microk8s-cluster'
    nectar_dev = [c for c in clusters if c['name'] == target][0]
    return nectar_dev['cluster']['server']

  @staticmethod
  def read_target_cluster_user_token():
    k = KubeBroker.kubectl()
    sa_bundle = KubeBroker.jcmd(f"{k} get sa/nectar-dev -o json")
    secret_name = sa_bundle['secrets'][0]['name']
    secret_bundle = KubeBroker.jcmd(f"{k} get secret {secret_name} -o json")
    b64_user_token = secret_bundle['data']['token']
    out = str(base64.b64decode(b64_user_token))[2:-1]
    return out

  @staticmethod
  def jcmd(cmd_str):
    try:
      return json.loads(KubeBroker.cmd(cmd_str))
    except:
      return None

  @staticmethod
  def cmd(cmd_str):
    formatted_cmd = cmd_str.split(' ')
    output = subprocess.run(formatted_cmd, stdout=subprocess.PIPE).stdout
    return output

  @staticmethod
  def env_auth_type(fallback=None):
    return os.environ.get('K8S_AUTH_TYPE', fallback)

  def check_connected_or_raise(self):
    if not self.is_connected:
      if not self.connect():
        raise BrokerConnException(self.last_error or "unknown")


broker = KubeBroker()
