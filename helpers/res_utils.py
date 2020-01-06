import re
from typing import Optional, Dict, List

from kubernetes.client import V1Service, V1ReplicaSet, V1Pod, V1Deployment
from kubernetes.client.rest import ApiException

from k8_kat.base.kube_broker import broker
from utils.utils import Utils


class ResUtils:
  LOG_REGEX = r"(\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b) - - (.*)"

  @staticmethod
  def label_matrix(matcher):
    pods = matcher.pods()
    all_labels = Utils.flatten([pod.label_tups for pod in pods])
    all_labels = list(set(all_labels))
    all_selectors = list(matcher.pod_select_labels.items())
    col_names = [f"{t[0]}:{t[1]}" for t in all_labels]
    row_names = [f"{t[0]}:{t[1]}" for t in all_selectors]
    row_values = []
    for i, sel in enumerate(all_selectors):
      booleans = [sel == lb for lb in all_labels]
      # noinspection PyTypeChecker
      booleans.insert(0, row_names[i])
      row_values.append(booleans)
    return dict(
      col_names=col_names,
      row_names=row_names,
      row_values=row_values
    )

  @staticmethod
  def list_namespaces():
    _namespaces = broker.coreV1.list_namespace().items
    extractor = lambda n: n.metadata.name
    return list(map(extractor, _namespaces))

  @staticmethod
  def label_combinations():
    all_deps = broker.appsV1Api.list_deployment_for_all_namespaces().items
    map_labels_fn = lambda d: d.spec.selector.match_labels
    label_hash_list = list(map(map_labels_fn, all_deps))
    label_list = []

    for _hash in label_hash_list:
      for key in _hash:
        label_list.append(f"{key}:{_hash[key]}")

    return list(set(label_list))

  @staticmethod
  def dep_by_ns() -> List[Dict[str, str]]:
    from k8_kat.base.k8_kat import K8Kat
    deps = K8Kat.deps().not_ns('kube-system').go()
    output = []
    for name in set([dep.name for dep in deps]):
      appears_in = set([dep.ns for dep in deps if dep.name == name])
      output.append(dict(name=name, namespaces=list(appears_in)))
    return output

  @staticmethod
  def find_svc(ns, name) -> Optional[V1Service]:
    try:
      return broker.coreV1.read_namespaced_service(
        namespace=ns,
        name=name
      )
    except ApiException:
      return None

  @staticmethod
  def find_rs(namespace, name) -> Optional[V1ReplicaSet]:
    try:
      return broker.appsV1Api.read_namespaced_replica_set(
        name,
        namespace
      )
    except ApiException:
      return None

  @staticmethod
  def find_pod(namespace, name) -> Optional[V1Pod]:
    try:
      return broker.coreV1.read_namespaced_pod(
        name,
        namespace
      )
    except ApiException:
      return None

  @staticmethod
  def matching_ref(refs, exp_type, exp_name):
    for res_ref in refs:
      if res_ref.kind == exp_type:
        if res_ref.name == exp_name:
          return res_ref
    return None

  @staticmethod
  def try_clean_log_line(line):
    try:
      match = re.search(ResUtils.LOG_REGEX, line)
      return match.group(2) or line
    except:
      return line

  @staticmethod
  def find_dp(namespace, name):
    try:
      return broker.appsV1Api.read_namespaced_deployment(
        name,
        namespace
      )
    except ApiException as r:
      return None

  @staticmethod
  def dep_owns_pod(dep: V1Deployment, pod: V1Pod) -> bool:
    if dep.metadata.namespace == pod.metadata.namespace:
      dep_matchers = dep.spec.selector.match_labels
      pod_labels = pod.metadata.labels
      if dep_matchers is None or pod_labels is None: return False
      return dep_matchers.items() <= pod_labels.items()
    else:
      return False

  @staticmethod
  def dep_matches_svc(dep: V1Deployment, svc: V1Service) -> bool:
    if dep.metadata.namespace == svc.metadata.namespace:
      dep_pod_labels = dep.spec.template.metadata.labels
      svc_matchers = svc.spec.selector
      if dep_pod_labels is None or svc_matchers is None: return False
      return dep_pod_labels.items() >= svc_matchers.items()
    else:
      return False

  @staticmethod
  def dep_svcs(dep: V1Deployment) -> [V1Service]:
    ns_svcs = broker.coreV1.list_namespaced_service(
      namespace=dep.metadata.namespace
    ).items

    pod_labels = dep.spec.template.metadata.labels
    inclusion_check = lambda svc: ResUtils.dep_covers_svc_labels(svc, pod_labels)
    return [svc for svc in ns_svcs if inclusion_check(svc)]

  @staticmethod
  def dep_covers_svc_labels(svc: V1Service, labels: Dict[str, str]) -> bool:
    svc_matchers: Dict[str, str] = svc.spec.selector
    return svc_matchers >= labels if svc_matchers is not None else False

  @staticmethod
  def dep_covers_svc_pod(svc: V1Service, pod: V1Pod) -> bool:
    pod_labels: Dict[str, str] = pod.metadata.labels
    svc_matchers: Dict[str, str] = svc.spec.selector
    return svc_matchers >= pod_labels if svc_matchers is not None else False
