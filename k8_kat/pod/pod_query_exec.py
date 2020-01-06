from k8_kat.base.kube_broker import broker
from k8_kat.base.res_query_exec import ResQueryExec


class PodQueryExec(ResQueryExec):

  @staticmethod
  def fetch_for_single_ns(ns, label_exp):
    return broker.coreV1.list_namespaced_pod(
      namespace=ns,
      label_selector=label_exp
    ).items

  @staticmethod
  def fetch_for_all_ns(label_exp):
    return broker.coreV1.list_pod_for_all_namespaces(
      label_selector=label_exp
    ).items

  @staticmethod
  def delete_by_label_in_ns(ns, label_exp):
    broker.coreV1.delete_collection_namespaced_pod(
      namespace=ns,
      label_selector=label_exp
    )

  @staticmethod
  def delete_individual(ns, name):
    broker.coreV1.delete_namespaced_pod(
      namespace=ns,
      name=name
    )
