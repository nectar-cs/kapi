from k8_kat.base.kube_broker import broker
from utils.utils import Utils


class SvcHelper:

  @staticmethod
  def find(namespace, name):
    return broker.coreV1.read_namespaced_service(
      name,
      namespace
    )

  @staticmethod
  def svcs_for_dep(dep, all_svcs):
    match_labels = dep.spec.selector.match_labels
    finder = lambda svc: svc.spec.selector == match_labels
    return list(filter(finder, all_svcs))

  @staticmethod
  def child_ser(svc):

    def port_bundle(bun):
      return { "from_port": bun.port, "to_port": bun.target_port}

    name = svc.metadata.name
    namespace = svc.metadata.namespace
    port_obj = svc.spec.ports[0]
    get_ip = lambda: svc.status.load_balancer.ingress[0].ip
    port_objs = list(map(port_bundle, svc.spec.ports))

    return {
      "name": name,
      "namespace": namespace,
      "internal_ip": svc.spec.cluster_ip,
      "external_ip": Utils.try_or(get_ip),
      "from_port": port_obj.port,
      "to_port": port_obj.target_port,
      "short_dns": name + "." + namespace,
      "long_dns": name + "." + namespace + ".svc.cluster.local",
      "ports": port_objs,
      "type": svc.spec.type
    }