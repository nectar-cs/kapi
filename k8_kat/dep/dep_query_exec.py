from k8_kat.base.kube_broker import broker
from k8_kat.base.res_query_exec import ResQueryExec


class DepQueryExec(ResQueryExec):

  @staticmethod
  def fetch_for_single_ns(ns, label_exp):
    return broker.appsV1Api.list_namespaced_deployment(
      namespace=ns,
      label_selector=label_exp
    ).items

  @staticmethod
  def fetch_for_all_ns(label_exp):
    return broker.appsV1Api.list_deployment_for_all_namespaces(
      label_selector=label_exp
    ).items

