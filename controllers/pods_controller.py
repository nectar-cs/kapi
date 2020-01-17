#!/usr/bin/env python3
from flask import Blueprint, request, jsonify
from k8_kat.res.base.k8_kat import K8Kat
from k8_kat.res.events.event_serialization import EventSerialization

controller = Blueprint('pods_controller', __name__)

@controller.route('/api/pods/<ns>/<name>/logs')
def logs(ns, name):
  pod = K8Kat.pods().ns(ns).find(name)
  since_seconds = int(request.args.get('since_seconds', '5000'))
  return dict(data=pod.logs(since_seconds))

@controller.route('/api/pods/<ns>/<name>/events')
def events(ns, name):
  pod = K8Kat.pods().ns(ns).find(name)
  serializer = EventSerialization.standard
  serialized = [serializer(e) for e in pod.events()]
  return jsonify(data=serialized)
