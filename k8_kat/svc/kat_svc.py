from typing import Dict

from kubernetes.client import V1ServicePort

from helpers.kube_broker import broker
from k8_kat.base.kat_res import KatRes
from utils.utils import Utils


class KatSvc(KatRes):

  def __init__(self, raw):
    super().__init__(raw)
    self.assoced_pods = None
    self._am_dirty = raw is not None

  @property
  def kind(self):
    return "Service"

  @property
  def pod_select_labels(self) -> Dict[str, str]:
    return self.raw.spec.selector or {}

  @property
  def main_port_obj(self) -> V1ServicePort:
    ports = self.raw.spec.ports
    return len(ports) and ports[0]

  @property
  def internal_ip(self) -> str:
    return self.raw.spec.cluster_ip

  @property
  def external_ip(self) -> str:
    load_bal = self.raw.status.load_balancer
    return Utils.try_or(lambda: load_bal.ingress[0].ip)

  @property
  def from_port(self) -> int:
    port_obj = self.main_port_obj
    return port_obj and port_obj.port

  @property
  def to_port(self):
    port_obj = self.main_port_obj
    return port_obj and port_obj.target_port

  @property
  def short_dns(self) -> str:
    return f"{self.name}.{self.namespace}"

  @property
  def fqdn(self) -> str:
    return f"{self.short_dns}.svc.cluster.local"

  @property
  def type(self) -> str:
    return self.raw.spec.type

  def pods(self, force_reload=False):
    if force_reload or self.assoced_pods is None:
      self.find_and_assoc_pods()
    return self.assoced_pods

  def find_and_assoc_pods(self):
    from k8_kat.base.k8_kat import K8Kat
    matchers = list(self.pod_select_labels.items())
    self.assoced_pods = K8Kat.pods().ns(self.ns).lbs_inc_each(matchers).go()

  def raw_endpoints(self):
    return broker.coreV1.read_namespaced_endpoints(self.name, self.ns)

  def flat_endpoints(self):
    raw_endpoints = self.raw_endpoints()
    per_sub = lambda sub: [addr for addr in (sub.addresses or [])]
    return Utils.flatten([per_sub(sub) for sub in raw_endpoints.subsets])

  @property
  def endpoint_ips(self):
    return [ep.ip for ep in self.flat_endpoints()]

  def __repr__(self):
    return f"Svc[{self.ns}:{self.name}({self.internal_ip})]"
