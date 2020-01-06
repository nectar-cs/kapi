from typing import List, Tuple, Dict

from k8_kat.base.kube_broker import broker
from k8_kat.events.kat_event import KatEvent


class KatRes:

  def __init__(self, raw):
    self.is_dirty = False
    self.raw = raw
    self._assoced_events = None

  @property
  def uid(self):
    return self.raw.metadata.uid

  @property
  def kind(self):
    _kind = self.raw.kind
    if not _kind:
      raise Exception("Unimplemented!")
    return _kind

  @property
  def name(self):
    return self.raw.metadata.name

  @property
  def namespace(self):
    return self.raw.metadata.namespace

  @property
  def ns(self):
    return self.namespace

  @property
  def labels(self):
    return self.raw.metadata.labels or {}

  @property
  def label_tups(self) -> List[Tuple[str, str]]:
    return list(self.labels.items())

  def label(self, which):
    return self.labels.get(which)

  @property
  def pod_select_labels(self) -> Dict[str, str]:
    raise Exception("Unimplemented!")

  def events(self):
    if self._assoced_events is None:
      api = broker.coreV1
      raw_list = api.list_namespaced_event(namespace=self.ns).items
      kat_list = [KatEvent(raw_event) for raw_event in raw_list]
      mine = [event for event in kat_list if event.is_for(self)]
      self._assoced_events = mine
    return self._assoced_events

  def set_label(self, **labels):
    new_label_dict = {**self.labels, **labels}
    self.raw.metadata.labels = new_label_dict
    self._perform_patch_self()

  def _perform_patch_self(self):
    raise Exception("Unimplemented!")

  def serialize(self, serializer):
    return serializer(self)
