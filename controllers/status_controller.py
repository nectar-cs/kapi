import os

from flask import Blueprint, request, jsonify
from k8_kat.utils.main import utils as k8_kat_utils
from k8_kat.base import broker_configs
from k8_kat.base.k8_kat import K8Kat
from k8_kat.base.kube_broker import broker
from utils import utils as kapi_utils

controller = Blueprint('status_controller', __name__)

@controller.route('/api/status')
def status():
  return status_body()

@controller.route('/api/status/restart', methods=['POST'])
def restart():
  for which in request.json['deployments']:
    K8Kat.deps().ns('nectar').find(which).restart_pods()
  return jsonify(status='working')

@controller.route('/api/status/connect')
def connect():
  broker.connect()
  broker.check_connected_or_raise()
  return status_body()

def status_body():
  return jsonify(
    is_connected=broker.is_connected,
    default_env_config=broker_configs.default_config(),
    connect_config=broker.connect_config,
    kapi_env=kapi_utils.run_env(),
    kat_env=k8_kat_utils.run_env()
  )

@controller.route('/api/status/revision')
def revision():
  return jsonify(sha=os.environ.get('REVISION'))
