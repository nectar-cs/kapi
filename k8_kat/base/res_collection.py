from collections import UserList
from typing import List
from k8_kat.base.res_query import ResQuery


class ResCollection(UserList):
  def __init__(self):
    super().__init__()
    self.query: ResQuery = self.create_query()
    self._is_dirty = True

  def __getitem__(self, y):
    self.go()
    return super().__getitem__(y)

  def __iter__(self):
    self.go()
    return super().__iter__()

  def __len__(self):
    self.go()
    return super().__len__()

  def find(self, name):
    candidates = self.names(name).go()
    return len(candidates) and candidates[0]

  def names(self, *_names):
    actual = list(_names[0]) if isinstance(_names[0], list) else list(_names)
    return self.where(name_in=actual)

  def not_names(self, *_names):
    actual = list(_names[0]) if isinstance(_names[0], list) else list(_names)
    return self.where(name_not_in=actual)

  def where(self, **query_hash):
    self.query.update(**query_hash)
    self._is_dirty = True
    return self

  def ns(self, *_ns):
    inst = self() if isinstance(self, type) else self
    actual = list(_ns[0]) if isinstance(_ns[0], list) else list(_ns)
    return inst.where(ns_in=actual)

  def not_ns(self, *_ns):
    actual = list(_ns[0]) if isinstance(_ns[0], list) else list(_ns)
    return self.where(ns_nin=actual)

  def lbs_inc_each(self, label_array=None, **kwargs):
    label_array = list(kwargs.items()) if kwargs else label_array
    return self.where(lbs_inc_each=label_array)

  def lbs_exc_each(self, label_array=None, **kwargs):
    label_array = list(kwargs.items()) if kwargs else label_array
    return self.where(lbs_exc_each=label_array)

  def lbs_inc_any(self, label_array=None, **kwargs):
    label_array = list(kwargs.items()) if kwargs else label_array
    return self.where(lbs_inc_any=label_array)

  def lbs_exc_any(self, label_array=None, **kwargs):
    label_array = list(kwargs.items()) if kwargs else label_array
    return self.where(lbs_exc_any=label_array)

  def pluck(self, feature_name, unique=False):
    resolved = [getattr(r, feature_name) for r in self.go()]
    return list(set(resolved)) if unique else resolved

  def pretty_pluck(self, *f_names):
    actual = list(f_names[0]) if isinstance(f_names[0], list) else list(f_names)
    val = lambda res, feat: getattr(res, feat)
    line_feats = lambda res: [val(res, f) for f in actual]
    line_feats_str = lambda res: " | ".join(line_feats(res))
    line = lambda res: f"<{res.name} : {line_feats_str(res)}>"
    return [line(res) for res in self.go()]

  def feature_in(self, feature: str, possibilities: List[str]):
    self.query.add_feature_filter(
      feature, 'in', possibilities
    )
    return self

  def feature_not_in(self, feature: str, possibilities: List[str]):
    self.query.add_feature_filter(
      feature, 'not_in', possibilities
    )
    return self

  def feature_is(self, feature: str, challenge):
    return self.feature_in(feature, [challenge])

  def feature_is_not(self, feature: str, challenge):
    return self.feature_not_in(feature, [challenge])

  def delete_all(self):
    actual_namespaces = self.pluck('namespace', True)
    actual_names = self.pluck('name', True)
    self.query.delete(actual_namespaces, actual_names)

  def serialize(self, serializer):
    return [serializer(res) for res in self.go()]

  def go(self):
    if self._is_dirty:
      self.data = self.query.evaluate()
      self._is_dirty = False
    return self

  def create_query(self):
    raise Exception("Unimplemented!")

