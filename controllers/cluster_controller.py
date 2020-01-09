#!/usr/bin/env python3
from flask import Blueprint, jsonify, request
from k8_kat.base.kube_broker import broker

from k8_kat.base.k8_kat import K8Kat
from k8_kat.cluster import kat_cluster
from k8_kat.pod.pod_serialization import PodSerialization
from stunt_pods.stunt_pod import StuntPod

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

@controller.route('/api/cluster/stunt_pods')
def stunt_pods():
  broker.check_connected_or_raise()
  garbage = K8Kat.pods().lbs_inc_each(StuntPod.labels()).go()
  ser = garbage.serialize(PodSerialization.standard)
  return jsonify(data=ser)

@controller.route('/api/cluster/kill_stunt_pods', methods=['POST'])
def kill_stunt_pods():
  garbage = K8Kat.pods().lbs_inc_each(StuntPod.labels())
  garbage.delete_all()
  return jsonify(status='done')
