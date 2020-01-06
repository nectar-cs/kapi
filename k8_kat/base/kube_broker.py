import base64
import json

from kubernetes import config, client
import urllib3

from k8_kat.base.broker_configs import default_config
from utils.utils import Utils


class BrokerConnException(Exception):
  def __init__(self, message):
    super().__init__(message)

class KubeBroker:

  def __init__(self):
    self.connect_config = {}
    self.is_connected = False
    self.last_error = None
    self.coreV1 = None
    self.appsV1Api = None
    self.client = None

  def connect(self, **connect_config):
    self.connect_config = {**default_config, **connect_config}
    connect_in = self.connect_in_cluster
    connect_out = self.connect_out_cluster
    connect_fn = connect_in if self.is_in_cluster_auth() else connect_out
    self.is_connected = connect_fn()
    self.load_api() if self.is_connected else None
    return self.is_connected

  def load_api(self):
    self.client = client
    self.coreV1 = client.CoreV1Api()
    self.appsV1Api = client.AppsV1Api()

  def connect_in_cluster(self):
    try:
      print(f"[kube_broker] In-cluster auth...")
      config.load_incluster_config()
      print(f"[kube_broker] In-cluster auth success.")
      return True
    except Exception as e:
      print(f"[kube_broker] In-cluster connect Failed: {e}")
      self.last_error = e
      return False

  def connect_out_cluster(self):
    sa_name = self.connect_config['sa_name']
    sa_ns = self.connect_config['sa_ns']

    try:
      print(f"[kube_broker] Out-cluster auth with {self.kubectl()}...")

      user_token = self.read_target_cluster_user_token()
      configuration = client.Configuration()
      configuration.host = self.read_target_cluster_ip()
      configuration.verify_ssl = False
      configuration.debug = False
      configuration.api_key = {"authorization": f"Bearer {user_token}"}
      client.Configuration.set_default(configuration)
      urllib3.disable_warnings()

      print(f"[kube_broker] Out-cluster auth success ({sa_ns}/{sa_name})")
      return True
    except Exception as e:
      print(f"[kube_broker] Out-cluster auth failed ({sa_ns}/{sa_name}): {e}")
      self.last_error = e
      return False

  def is_in_cluster_auth(self):
    return self.connect_config['auth_type'] == 'in'

  def kubectl(self):
    return self.connect_config['kubectl']

  def read_target_cluster_ip(self):
    on_board_config = self.jk_exec('config view')
    clusters = on_board_config['clusters']
    target = self.connect_config['cluster_name']
    dev_cluster = [c for c in clusters if c['name'] == target][0]
    return dev_cluster['cluster']['server']

  def read_target_cluster_user_token(self):
    sa_name = self.connect_config['sa_name']
    sa_ns = self.connect_config['sa_ns']
    sa_bundle = self.jk_exec(f"get sa/{sa_name} -n {sa_ns}")
    secret_name = sa_bundle['secrets'][0]['name']
    secret_bundle = self.jk_exec(f"get secret/{secret_name} -n {sa_ns}")
    b64_user_token = secret_bundle['data']['token']
    out = str(base64.b64decode(b64_user_token))[2:-1]
    return out

  def jk_exec(self, cmd_str):
    cmd_str = f"{self.kubectl()} {cmd_str} -o json"
    return json.loads(Utils.shell_exec(cmd_str))

  def check_connected_or_raise(self):
    if not self.is_connected:
      if not self.connect():
        raise BrokerConnException(self.last_error or "unknown")


broker = KubeBroker()
