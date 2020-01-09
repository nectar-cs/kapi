import json
import unittest

from k8_kat.utils.testing.fixtures import test_env

from app import app


class TestClusterController(unittest.TestCase):

  @classmethod
  def setUpClass(cls) -> None:
    test_env.cleanup()
    test_env.create_namespaces()

  def test_get_namespaces(self):
    response = app.test_client().get('/api/cluster/namespaces')
    body = json.loads(response.data)
    all_present = set(body['data']) >= {'n1', 'n2', 'n3'}
    self.assertEqual(response.status_code, 200)
    self.assertTrue(all_present, True)

  def test_get_label_combinations(self):
    response = app.test_client().get('/api/cluster/label_combinations')
    self.assertEqual(response.status_code, 200)

  def test_get_stunt_pods(self):
    response = app.test_client().get('/api/cluster/stunt_pods')
    self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
  unittest.main()
