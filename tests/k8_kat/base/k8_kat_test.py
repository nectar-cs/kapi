import os
import unittest
from typing import Tuple, List
from kubernetes.client import V1Deployment, V1Service

from k8_kat.base.kube_broker import broker
from helpers.res_utils import ResUtils
from utils.utils import Utils

NAMESPACES = ['n1', 'n2', 'n3']

class K8katTest(unittest.TestCase):

  @staticmethod
  def k(cmd: str):
    os.system(f"microk8s.kubectl {cmd}")

  @staticmethod
  def nk(cmd: str, ns: str):
    if ns:
      me.k(f"{cmd} -n {ns}")
    else:
      me.k(cmd)

  @staticmethod
  def read_dep(ns, name) -> V1Deployment:
    return ResUtils.find_dp(ns, name)

  @staticmethod
  def read_svc(ns, name) -> V1Service:
    return ResUtils.find_svc(ns, name)

  @staticmethod
  def create_dep(ns: str, dep_name: str, labels=None):
    me.nk(f"create deploy {dep_name} --image nginx", ns)
    if labels:
      me.nk_label_dep(ns, dep_name, labels)

  @staticmethod
  def create_svc(ns: str, name: str, subs=None):
    from tests.k8_kat.fixtures.simple_svc import create
    subs = {**(subs or {}), 'name': name}
    create(ns, subs)

  @staticmethod
  def create_pod(ns: str, name: str, subs=None):
    from tests.k8_kat.fixtures.simple_pod import create
    subs = {**(subs or {}), **dict(name=name, ns=ns)}
    create(subs)

  @staticmethod
  def create_dep_svc(ns: str, dep_name):
    me.nk(f"expose deployment/{dep_name} --port 80", ns)

  @staticmethod
  def nk_apply(ns, fname):
    fname = K8katTest.gen_yaml_path(fname)
    me.nk(f"apply -f {fname}", ns)

  @staticmethod
  def gen_yaml_path(fname) -> str:
    import app
    root = app.app.instance_path.replace('/instance', '')
    return os.path.join(root, f"tests/yamls/{fname}.yaml")

  @staticmethod
  def k_apply(fname):
    me.nk_apply(None, fname)

  @staticmethod
  def nk_label_dep(ns: str, dep_name: str, labels: List[Tuple[str, str]]):
    lb_str = ' '.join([f"{l[0]}={l[1]}" for l in labels])
    me.nk(f"label deploy {dep_name} {lb_str}", ns)

  @staticmethod
  def prepare_cluster():
    if Utils.is_ci():
      me.k_apply('ci-perms')

  @staticmethod
  def ensure_no_pods(namespaces=None):
    namespaces = namespaces if namespaces else NAMESPACES
    for ns in namespaces:
      me.nk("delete pod --all", ns)

  @classmethod
  def setUpClass(cls) -> None:
    cls.prepare_cluster()
    broker.connect(
      auth_type="out",
      kubectl="microk8s.kubectl"
    )

    if Utils.is_ci():
      for ns in NAMESPACES:
        cls.k(f"create ns {ns}")

  @classmethod
  def tearDownClass(cls):
    if Utils.is_ci() and not Utils.is_ci_keep():
      cls.k('delete clusterrolebinding nectar')
      for ns in NAMESPACES:
        cls.k(f"delete ns {ns}")
    else:
      for ns in NAMESPACES:
        cls.nk("delete deploy --all", ns)
        cls.nk("delete svc --all", ns)
        # cls.nk("delete pod --all", ns)


me = K8katTest
