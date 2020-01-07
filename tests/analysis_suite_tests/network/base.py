from unittest import mock
from unittest.mock import PropertyMock, MagicMock

from tests.k8_kat.base.k8_kat_test import K8katTest
from utils.utils import Utils

TESTING_NS = "n1"
TESTING_DEP_NM = "simple-app-dep"
TESTING_SVC_NM = "simple-app-svc"

class Base(K8katTest):

  @classmethod
  def setUpClass(cls) -> None:
    cls.nk_apply('n1', 'simple-dep_svc')

  @classmethod
  def stdSetUpClass(cls, step_class):
    cls.dep = K8Kat.deps().ns(TESTING_NS).find(TESTING_DEP_NM)
    cls.svc = K8Kat.svcs().ns(TESTING_NS).find(TESTING_SVC_NM)
    cls.step = step_class(
      from_port=cls.svc.from_port,
      dep_ns=TESTING_NS,
      svc_name=TESTING_SVC_NM,
      dep_name=TESTING_DEP_NM,
    )

  def setUp(self):
    self.step.from_port = self.svc.port

  def post_test_positive(self):
    self.assertTrue(self.step.outcome)
    self.ensure_copy_working()

  def post_test_negative(self):
    self.assertFalse(self.step.outcome)
    self.ensure_copy_working()

  def ensure_copy_working(self):
    self.assertIsNotNone(self.step.copy_bundle())
    self.assertIsNotNone(self.step.summary_copy())
    self.assertIsNotNone(self.step.commands_copy())
    self.assertIsNotNone(self.step.steps_copy())
    self.assertIsNotNone(self.step.outcome_copy())

  def mock_step_method(self, prop_name, value, callback):
    mock_name = f"{Utils.fqcn(self.step)}.{prop_name}"
    with mock.patch(mock_name, new_callable=MagicMock) as v:
      v.return_value = value
      callback()

  def mock_step_prop(self, prop_name, value, callback):
    mock_name = f"{Utils.fqcn(self.step)}.{prop_name}"
    with mock.patch(mock_name, new_callable=PropertyMock) as v:
      v.return_value = value
      callback()

  def scale_to(self, amount):
    self.dep.scale(amount)
