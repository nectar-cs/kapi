from flask import Blueprint, request, jsonify
from k8_kat.res.base.k8_kat import K8Kat
from k8_kat.res.pod import pod_factory
from k8_kat.res.pod.kat_pod import KatPod

controller = Blueprint('run_controller', __name__)

@controller.route('/api/run/curl', methods=['POST'])
def run_curl_command():
  j_body = request.json
  ns, name = [j_body['namespace'], "curl-man"]
  response = pod_factory.one_shot_curl(ns, **j_body)
  return jsonify(data=response)

@controller.route('/api/run/cmd', methods=['POST'])
def run_command():
  j = request.json
  ns, pod_name, cmd = j['pod_namespace'], j['pod_name'], j['command']
  pod = KatPod.find(ns, pod_name)
  return jsonify(data=pod.shell_exec(cmd))

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
