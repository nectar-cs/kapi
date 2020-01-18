#!/usr/bin/env python3
from flask import Blueprint, jsonify, request
from k8_kat.auth.kube_broker import broker
from k8_kat.res.base.k8_kat import K8Kat
from k8_kat.res.cluster import kat_cluster
from k8_kat.res.pod.pod_serialization import PodSerialization

controller = Blueprint('cluster_controller', __name__)

@controller.route('/api/cluster/namespaces')
def namespaces():
  broker.check_connected_or_raise()
  _namespaces = kat_cluster.list_namespaces()
  return jsonify(data=_namespaces)

@controller.route('/api/cluster/label_combinations')
def label_combinations():
  broker.check_connected_or_raise()
  combinations = kat_cluster.label_combinations()
  return jsonify(data=list(set(combinations)))
