#!/usr/bin/env python3
import os

from flask import Flask, jsonify, request
from flask_cors import CORS
from k8_kat.base.kube_broker import broker, BrokerConnException

from controllers import analysis_controller, deployments_controller, run_controller, cluster_controller, \
  status_controller, builds_controller, pods_controller
from utils import utils

app = Flask(__name__, static_folder=".", static_url_path="")
app.config["SECRET_KEY"] = os.environ.get('SECRET_KEY')

controllers = [
  status_controller,
  deployments_controller,
  cluster_controller,
  run_controller,
  analysis_controller,
  builds_controller,
  pods_controller
]

for controller in controllers:
  app.register_blueprint(controller.controller)

CORS(app)

@app.shell_context_processor
def make_shell_context():
  from k8_kat.base.k8_kat import K8Kat
  classes = [K8Kat, utils]
  classes = { klass.__name__: klass for klass in classes }
  return dict(**classes, broker=broker)

@app.errorhandler(BrokerConnException)
def all_exception_handler(error):
  return jsonify(dict(
    error='could not connect to Kubernetes API',
    reason=str(error)
  )), 500

@app.before_request
def ensure_broker_connected():
  if "/api/status" not in request.path:
    broker.check_connected_or_raise()

if __name__ == '__main__':
  broker.connect()
  app.config["cmd"] = ["bash"]
  app.run(host='0.0.0.0', port=5000)
