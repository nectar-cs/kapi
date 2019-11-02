#!/usr/bin/env python3
import os

from flask import Blueprint

from helpers.dep_helper import DepHelper
from helpers.kube_broker import broker

controller = Blueprint('status_controller', __name__)

@controller.route('/api/status')
def status():
  return status_body()

@controller.route('/api/status/<which>/restart')
def restart(which):
  DepHelper.restart_nectar_pods(which)
  return { "status": "working" }

@controller.route('/api/status/connect')
def connect():
  broker.connect()
  broker.check_connected()
  return status_body()

def status_body():
  return {
    "is_connected": broker.is_connected,
    "last_error": broker.last_error
  }

@controller.route('/api/status/revision')
def revision():
  return{
    "sha": os.environ.get('REVISION')
  }