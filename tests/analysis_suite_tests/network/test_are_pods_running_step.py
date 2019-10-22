import unittest

from analysis_suites.network.are_pods_running_step import ArePodsRunningStep
from analysis_suites.network.do_pods_connect_step import DoPodsConnectStep
from analysis_suites.network.is_svc_visible_step import IsSvcVisibleStep
from tests.analysis_suite_tests.network.base import Base

class ArePodsRunningStepTest(Base):

  @classmethod
  def setUpClass(cls):
    super().stdSetUpClass(ArePodsRunningStep)

  def test_positive(self):
    self.step.perform()
    self.post_test_positive()

  def _test_negative(self):
    self.step.perform()
    self.post_test_negative()

  def test_negative(self):
    self.mock_step_method("phase", 'Idle', self._test_negative)

if __name__ == '__main__':
  unittest.main()