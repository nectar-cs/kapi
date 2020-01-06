from k8_kat.base.res_collection import ResCollection
from k8_kat.base.res_query import ResQuery
from k8_kat.dep.dep_query_exec import DepQueryExec
from k8_kat.dep.kat_dep import KatDep


class KatDeps(ResCollection):
  def create_query(self):
    return ResQuery(DepQueryExec(), KatDep)
