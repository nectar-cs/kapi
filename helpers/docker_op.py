import os

import kubernetes
from k8_kat.base.kube_broker import broker
from kubernetes.client import V1ObjectMeta, V1PodSpec, V1Container, V1EnvVar, V1Pod
from kubernetes.client.rest import ApiException

from k8_kat.base.k8_kat import K8Kat

from utils import utils


class DockerOp:

  def __init__(self, pod_name):
    self.pod_name = pod_name or self.gen_name()
    self._daemon_host = None
    self._pod = None

  @staticmethod
  def find(_id):
    pod = K8Kat.pods().ns('nectar').find(_id).raw
    return __class__(pod.metadata.name)

  @staticmethod
  def latest():
    res = broker.coreV1.list_namespaced_pod(
      namespace='nectar',
      label_selector=utils.dict_to_eq_str(DockerOp.pod_labels())
    ).items[0]
    return __class__(res.metadata.name)

  def command(self):
    raise Exception("Unimplemented!")

  def logs(self):
    try:
      return broker.coreV1.read_namespaced_pod_log(
        namespace='nectar',
        name=self.pod().metadata.name
      )
    except kubernetes.client.rest.ApiException:
      return ''

  def status(self):
    _status = self.pod(True).status
    return _status.phase

  def raw_status(self):
    _status = self.pod(True).status
    return _status

  def pod(self, force = False):
    if (self._pod is None) or force:
      self._pod = K8Kat.pods().ns('nectar').find(self.pod_name).raw
    return self._pod

  def is_pod_ready(self):
    pod = self.pod(True)
    print(f"STATUS {pod and pod.status.phase}")
    return pod and not pod.status.phase == 'Pending'

  def daemon_host(self):
    if self._daemon_host is None:
      from_env = os.environ.get('DOCKER_HOST')
      implied = "tcp://dind.nectar:2375"
      self._daemon_host = from_env or implied
    return self._daemon_host

  def create_work_pod(self):
    broker.coreV1.create_namespaced_pod(
      namespace='nectar',
      body=V1Pod(
        metadata=V1ObjectMeta(
          name=self.pod_name,
          labels=self.pod_labels()
        ),
        spec=V1PodSpec(
          restart_policy='Never',
          containers=[
            V1Container(
              name='docker',
              image='docker:latest',
              command=["/bin/sh"],
              args=["-c", self.command()],
              env=[
                V1EnvVar(
                  name='DOCKER_HOST',
                  value=self.daemon_host()
                )
              ]
            )
          ]
        )
      )
    )

  def destroy(self):
    try:
      broker.coreV1.delete_namespaced_pod(
        namespace='nectar',
        name=self.pod_name
      )
    except ApiException:
      pass

  @staticmethod
  def gen_name():
    return f"docker-worker-{utils.rand_str(4)}"

  @staticmethod
  def pod_labels():
    return { 'job-type': 'docker-op' }

  @staticmethod
  def purge():
    broker.coreV1.delete_collection_namespaced_pod(
      namespace='nectar',
      label_selector=utils.dict_to_eq_str(DockerOp.pod_labels())
    )
