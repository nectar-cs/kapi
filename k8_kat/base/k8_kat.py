from k8_kat.dep.dep_collection import KatDeps
from k8_kat.pod.pod_collection import KatPods
from k8_kat.svc.svc_collection import SvcCollection


class K8Kat:

  @staticmethod
  def deps(**kwargs) -> KatDeps:
    collection = KatDeps()
    return collection.where(**kwargs)

  @staticmethod
  def svcs(**kwargs) -> SvcCollection:
    collection = SvcCollection()
    return collection.where(**kwargs)

  @staticmethod
  def pods(**kwargs) -> KatPods:
    collection = KatPods()
    return collection.where(**kwargs)
