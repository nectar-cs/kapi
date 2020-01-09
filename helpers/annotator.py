import datetime

from k8_kat.base.k8_kat import K8Kat
from k8_kat.base.kube_broker import broker


class Annotator:
  def __init__(self, namespace, name, **kwargs):
    self.deployment = K8Kat.deps().ns(namespace).find(name)
    self.sha = kwargs['sha']
    self.message = kwargs['message']
    self.branch = kwargs['branch']

  def gen_annotation_dict(self):
    return {
      "commit-sha": self.sha,
      "commit-message": self.message,
      "commit-branch": self.branch,
      "commit-timestamp": str(datetime.datetime.now())
    }

  def annotate(self):
    annotations = self.deployment.metadata.annotations
    updated_annot = { **annotations, **self.gen_annotation_dict() }
    self.deployment.metadata.annotations = updated_annot
    broker.appsV1Api.patch_namespaced_deployment(
      name=self.deployment.metadata.name,
      namespace=self.deployment.metadata.namespace,
      body=self.deployment
    )
    return self.gen_annotation_dict()
