from k8_kat.auth.kube_broker import broker
from k8_kat.res.dep.kat_dep import KatDep
from k8_kat.res.svc.kat_svc import KatSvc

from analysis_suites.base.analysis_step import AnalysisStep
from analysis_suites.network.copy import copy_tree
from utils import utils


class BaseNetworkStep(AnalysisStep):
  def __init__(self, **args):
    super().__init__()
    self.from_port = args['from_port']
    self.dep = KatDep.find(args['dep_ns'], args['dep_name'])
    self.svc = KatSvc.find(args['dep_ns'], args['svc_name'])
    self._stunt_pod = None

  @property
  def ns(self):
    return self.svc.ns

  @property
  def port_bundle(self):
    bundles = self.svc.raw.spec.ports
    matches = [b for b in bundles if str(b.port) == str(self.from_port)]
    return matches[0]

  @property
  def to_port(self):
    return self.port_bundle.target_port

  @property
  def target_url(self):
    return f"{self.svc.fqdn}:{self.svc.from_port}"

  @property
  def pod_label_comp(self):
    dep_labels = self.dep.pod_select_labels
    return utils.dict_to_eq_str(dep_labels)

  @property
  def api(self):
    return broker.coreV1

  def _copy_bundle(self):

    img = self.dep.image_name

    return {
      "dep_name": self.dep.name,
      "svc_name": self.svc.name,
      "img": img,
      "port": self.svc.from_port,
      "target_port": self.svc.to_port,
      "ns": self.dep.ns,
      "pod_name": "network_debug",
      "target_url": self.target_url,
      "fqdn": self.svc.short_dns,
      "tfqdn": self.svc.fqdn,
      "svc_ip": self.svc.internal_ip,
      "pod_label_comp": self.pod_label_comp
    }

  def _terminal_copy_bundle(self):
    return {}

  def load_copy_tree(self):
    return copy_tree
