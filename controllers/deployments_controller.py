from flask import Blueprint, request, jsonify
from k8_kat.res.base.k8_kat import K8Kat
from k8_kat.res.dep.dep_composer import DepComposer
from k8_kat.res.dep.dep_serializers import DepSerialization
from k8_kat.res.dep.dep_warnings import DepWarnings
from k8_kat.res.dep.kat_dep import KatDep
from k8_kat.res.pod.pod_serialization import PodSerialization
from k8_kat.res.svc.svc_serialization import SvcSerialization

from helpers.annotator import Annotator

controller = Blueprint('deployments_controller', __name__)


@controller.route('/api/deployments')
def index():
  deps = params_to_deps()
  serialized = [DepSerialization.as_needed(dep) for dep in deps]
  return jsonify(dict(data=serialized))

@controller.route('/api/deployments/<ns>/<name>')
def show(ns, name):
  dep = K8Kat.deps().ns(ns).find(name).with_friends()
  serialized = dep.serialize(DepSerialization.with_pods_and_svcs)
  return jsonify(serialized)

@controller.route('/api/deployments/across_namespaces')
def across_namespaces():
  return jsonify(dict(data=KatDep.across_namespaces()))

@controller.route('/api/deployments/<ns>/<name>/pods')
def deployment_pods(ns, name):
  dep = K8Kat.deps().ns(ns).find(name)
  serialized = [PodSerialization.standard(pod) for pod in dep.pods()]
  return jsonify(dict(data=serialized))

@controller.route('/api/deployments/<ns>/<name>/services')
def deployment_services(ns, name):
  dep = K8Kat.deps().ns(ns).find(name)
  svcs = dep.svcs()
  serialized = [SvcSerialization.with_endpoints(svc) for svc in svcs]
  return jsonify(dict(data=serialized))

@controller.route('/api/deployments/<ns>/<name>/annotate_git', methods=['POST'])
def annotate(ns, name):
  j = request.json
  sha, message, branch = [j['sha'], j['message'], j['branch']]
  KatDep.find(ns, name).git_annotate(sha, message, branch)
  return jsonify(dict(annotations={}))

@controller.route('/api/deployments/<ns>/<name>/validate_labels', methods=['POST'])
def validate_labels(ns, name):
  dep = K8Kat.deps().ns(ns).find(name)
  v = DepWarnings
  return jsonify(dict(
    template_covers=v.check_pod_template_inclusive(dep),
    no_eavesdrop=v.check_no_pods_eavesdrop(dep),
    labels_unique=v.check_labels_unique(dep),
    pods_same_ns=v.check_pods_in_same_ns(dep)
  ))

def eq_strs_to_tups(as_str: str):
  return [tuple(eq.split(':')) for eq in as_str.split(',')]

def params_to_deps():
  q = K8Kat.deps()

  ns_white = request.args.get('ns_filter_type', 'whitelist')
  lb_white = request.args.get('lb_filter_type', 'blacklist')

  ns_filters = request.args.get('ns_filters')
  lb_filters = request.args.get('lb_filters')

  ns_filters = ns_filters and ns_filters.split(',') or None
  lb_filters = lb_filters and eq_strs_to_tups(lb_filters)

  ns_filtering_op = q.ns if ns_white == 'whitelist' else q.not_ns
  q = ns_filtering_op(ns_filters) if ns_filters is not None else q

  lb_filtering_op = q.lbs_inc_each if lb_white == 'whitelist' else q.lbs_exc_each
  q = lb_filtering_op(lb_filters) if lb_filters is not None else q

  deps = q.go()

  if request.args.get('svcs') == 'true':
    DepComposer.associate_svcs(deps)

  if request.args.get('pods') == 'true':
    DepComposer.associate_pods(deps)

  return deps
