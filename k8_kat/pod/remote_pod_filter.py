from k8_kat.base.kube_broker import broker
from k8_kat.dep.kat_dep import KatDep

class RemotePodFilter:

  @staticmethod
  def fetch_single_namespace(namespace):
    api = broker.appsV1Api
    raw_items = api.list_namespaced_deployment(
      namespace=namespace
    ).items
    return [KatDep(item) for item in raw_items]

  @staticmethod
  def fetch_poly_namespace():
    api = broker.appsV1Api
    raw_items = api.list_deployment_for_all_namespaces().items
    return [KatDep(item) for item in raw_items]
