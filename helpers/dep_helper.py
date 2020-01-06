#!/usr/bin/env python3

from k8_kat.base.kube_broker import broker
from helpers.res_utils import ResUtils
from helpers.svc_helper import SvcHelper
from utils.utils import Utils

class DepHelper:
  @staticmethod
  def find(namespace, name):
    return broker.appsV1Api.read_namespaced_deployment(
      namespace=namespace,
      name=name
    )

  @staticmethod
  def restart_nectar_pods(dep_name):
    dep = DepHelper.find('nectar', dep_name)
    pod_labels = dep.spec.template.metadata.labels
    selector = Utils.dict_to_eq_str(pod_labels)
    broker.coreV1.delete_collection_namespaced_pod(
      'nectar',
      label_selector=selector
    )

  @staticmethod
  def simple_ser(dep):
    containers = dep.spec.template.spec.containers

    return {
      "name": dep.metadata.name,
      "namespace": dep.metadata.namespace,
      "labels": dep.spec.selector.match_labels,
      "replicas": dep.spec.replicas,
      "image_name": Utils.try_or(lambda: containers[0].image),
      "container_name": Utils.try_or(lambda: containers[0].name),
      "image_pull_policy": Utils.try_or(lambda: containers[0].image_pull_policy),
      "commit": DepHelper.commit_ser(dep)
    }

  @staticmethod
  def commit_ser(dep):
    bundle = {
      "sha": dep.metadata.annotations.get('commit-sha'),
      "branch": dep.metadata.annotations.get('commit-branch'),
      "message": dep.metadata.annotations.get('commit-message'),
      "timestamp": dep.metadata.annotations.get('commit-timestamp')
    }
    is_worthwhile = bundle['sha'] or bundle['message']
    return bundle if is_worthwhile else None

  # noinspection PyTypeChecker
  @staticmethod
  def complex_ser(bundle):
    base = DepHelper.simple_ser(bundle['dep'])
    child_nodes = {
      'pods': list(map(ResUtils.child_ser, bundle['pods'])),
      'services': list(map(SvcHelper.child_ser, bundle['svcs'])),
    }
    return dict(list(base.items()) + list(child_nodes.items()))
