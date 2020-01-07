#!/usr/bin/env python3
from flask import Blueprint, request, jsonify

from stunt_pods.curl_pod import CurlPod

controller = Blueprint('run_controller', __name__)

@controller.route('/api/run/curl', methods=['POST'])
def run_curl_command():
  j_body = request.json
  curl_pod = CurlPod(
    pod_name="curl-man",
    namespace=j_body['namespace']
  )
  raw_curl_response = curl_pod.curl(**j_body)
  return jsonify(data=raw_curl_response)

@controller.route('/api/run/cmd', methods=['POST'])
def run_command():
  j = request.json
  ns, pod_name, cmd = j['pod_namespace'], j['pod_name'], j['command']
  pod = K8Kat.pods().ns(ns).find(pod_name)
  return jsonify(data=pod.cmd(cmd))

@controller.route('/api/run/image_reload', methods=['POST'])
def image_reload():
  j = request.json
  ns, name = j['dep_namespace'], j['dep_name']
  K8Kat.deps().ns(ns).find(name).restart_pods()
  return jsonify(data=dict(status='working'))

@controller.route('/api/run/new_image', methods=['POST'])
def new_image():
  j = request.json
  ns, name, img_name = j['dep_namespace'], j['dep_name'], j['target_name']
  K8Kat.deps().ns(ns).find(name).replace_image(img_name)
  return jsonify(data=dict(status='working'))

@controller.route('/api/run/scale_replicas', methods=['POST'])
def scale_replicas():
  j = request.json
  ns, name, scale_to = j['dep_namespace'], j['dep_name'], j['scale_to']
  K8Kat.deps().ns(ns).find(name).scale(int(scale_to))
  return jsonify(data=dict(status='working'))
