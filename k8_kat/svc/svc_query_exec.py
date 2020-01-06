from typing import List

from kubernetes.client import V1Service

from k8_kat.base.kube_broker import broker
from k8_kat.base.res_query_exec import ResQueryExec


class SvcQueryExec(ResQueryExec):

  @staticmethod
  def fetch_for_single_ns(ns, label_exp) -> List[V1Service]:
    return broker.coreV1.list_namespaced_service(
      namespace=ns,
      label_selector=label_exp
    ).items

  @staticmethod
  def fetch_for_all_ns(label_exp) -> List[V1Service]:
    return broker.coreV1.list_namespaced_service(
      label_selector=label_exp
    ).items

