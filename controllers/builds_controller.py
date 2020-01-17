import importlib

import inflection
from flask import Blueprint, request

from helpers.docker_build_op import DockerBuildOp
from helpers.docker_push_op import DockerPushOp

controller = Blueprint('builds_controller', __name__)

@controller.route('/api/docker/build_image', methods=['POST'])
def build_image():
  args = request.json
  operation = DockerBuildOp(
    repo_tar_url=args['repo_tar_url'],
    dockerfile_path=args['dockerfile_path'],
    docker_build_path=args['docker_build_path'],
    output_img=args['output_img']
  )

  operation.create_work_pod()
  return new_job_bundle(operation)

@controller.route('/api/docker/push_image', methods=['POST'])
def push_image():
  args = request.json
  operation = DockerPushOp(
    username=args['username'],
    password=args['password'],
    image_name=args['image_name']
  )
  operation.create_work_pod()
  return new_job_bundle(operation)


@controller.route('/api/docker/<job_type>/<job_id>/job_info')
def job_info(job_type, job_id):
  instance = job_instance(job_type, job_id)
  return {
    'logs': instance.logs().split("\n"),
    'status': instance.status()
  }

@controller.route('/api/docker/<job_type>/<job_id>/clear_job', methods=['POST'])
def clear_job(job_type, job_id):
  instance = job_instance(job_type, job_id)
  instance and instance.destroy()

  return {'status': 'success'}

def new_job_bundle(operation):
  class_name = operation.__class__.__name__
  return {
    'job_id': operation.pod_name,
    'job_type': inflection.underscore(class_name)
  }

def job_instance(job_type, job_id):
  module_name = f"helpers.{job_type}"
  class_name = inflection.camelize(job_type, True)
  loaded_module = importlib.import_module(module_name)
  klass = getattr(loaded_module, class_name)
  return klass.find(job_id)
