import json
import unittest
from k8_kat.utils.testing.fixtures import test_env
from app import app


class TestDeploymentsController(unittest.TestCase):

  @classmethod
  def setUpClass(cls) -> None:
    test_env.cleanup()
    test_env.create_namespaces()

    test_env.create_dep('n1', 'd1', labels=dict(l1='v1'), replicas=1)
    test_env.create_dep('n1', 'd2', labels=dict(l2='v2'), replicas=1)
    test_env.create_dep('n2', 'd1', labels=dict(l1='v1', c='c'), replicas=1)
    test_env.create_svc('n2', 'd1', labels=dict(l1='v1', c='c'))
    test_env.create_dep('n3', 'd3', labels=dict(l3='v3', c='c'), replicas=1)

  def test_index_shallow(self):
    resp = app.test_client().get('/api/deployments')
    print(ns_and_names(resp))
    exp = {('n1', 'd1'), ('n1', 'd2'), ('n2', 'd1'), ('n3', 'd3')}
    self.assertTrue(set(ns_and_names(resp)) >= exp)

    # arg = 'ns_filter_type=whitelist&ns_filters=n1'
    # resp = app.test_client().get(f'/api/deployments?{arg}')
    # self.assertCountEqual(names(resp), ['d1', 'd2'])
    #
    # arg = 'ns_filter_type=whitelist&ns_filters=n1,n3'
    # resp = app.test_client().get(f'/api/deployments?{arg}')
    # self.assertCountEqual(names(resp), ['d1', 'd2', 'd3'])
    #
    # arg = 'ns_filter_type=blacklist&ns_filters=n1,n2'
    # resp = app.test_client().get(f'/api/deployments?{arg}')
    # self.assertCountEqual(names(resp), ['d3'])
    #
    # arg = 'ns_filter_type=whitelist&ns_filters=n1'
    # arg2 = 'lb_filter_type=whitelist&lb_filters=l1:v1'
    # resp = app.test_client().get(f'/api/deployments?{arg}&{arg2}')
    # self.assertCountEqual(names(resp), ['d1'])
    #
    # arg = 'ns_filter_type=whitelist&ns_filters=n1,n2,n3'
    # arg2 = 'lb_filter_type=whitelist&lb_filters=c:c,l3:v3'
    # resp = app.test_client().get(f'/api/deployments?{arg}&{arg2}')
    # self.assertCountEqual(names(resp), ['d3'])

  # def test_index_with_assocs(self):
  #   arg = 'ns_filter_type=whitelist&ns_filters=n3'
  #   arg2 = '&svcs=false'
  #   resp = app.test_client().get(f'/api/deployments?{arg}&{arg2}')
  #   self.assertIsNone(dep_called(resp, 'd3').get('pods'))
  #
  #   arg = 'ns_filter_type=whitelist&ns_filters=n3'
  #   arg2 = '&svcs=true'
  #   resp = app.test_client().get(f'/api/deployments?{arg}&{arg2}')
  #   self.assertEqual(dep_called(resp, 'd3')['svcs'], [])
  #
  #   arg = 'ns_filter_type=whitelist&ns_filters=n2'
  #   arg2 = '&svcs=true'
  #   resp = app.test_client().get(f'/api/deployments?{arg}&{arg2}')
  #   self.assertEqual(dep_called_svcs_names(resp, 'd1'), ['d1'])
  #
  #   arg = 'ns_filter_type=whitelist&ns_filters=n2'
  #   arg2 = '&svcs=true&pods=true'
  #   resp = app.test_client().get(f'/api/deployments?{arg}&{arg2}')
  #   self.assertEqual(dep_called_pods_labels(resp, 'd1'), [dict(app='d1')])
  #   self.assertEqual(dep_called_svcs_names(resp, 'd1'), ['d1'])

  # def test_show(self):
  #   resp = app.test_client().get('/api/deployments/n2/d1')
  #   jdep = json.loads(resp.data)
  #   self.assertEqual(jdep['name'], 'd1')
  #   self.assertEqual(jdep['namespace'], 'n2')
  #   self.assertEqual(len(jdep['pods']), 1)
  #   self.assertEqual(len(jdep['svcs']), 1)

  # def test_deployment_pods(self):
  #   resp = app.test_client().get('/api/deployments/n2/d1/pods')
  #   jpods = json.loads(resp.data)['data']
  #   self.assertEqual(len(jpods), 1)
  #   self.assertEqual(jpods[0]['namespace'], 'n2')
  #   self.assertEqual(jpods[0]['labels'], {'app': 'd1'})

  # def test_across_namespaces(self):
  #   resp = app.test_client().get('/api/deployments/across_namespaces')
  #   actual = json.loads(resp.data)['data']
  #   exp_d1 = dict(name='d1', namespaces=['n1', 'n2'])
  #   exp_d2 = dict(name='d2', namespaces=['n1'])
  #   exp_d3 = dict(name='d3', namespaces=['n3'])
  #   print(actual)
  #   print([exp_d1, exp_d2, exp_d3])
  #   self.assertCountEqual(actual, [exp_d1, exp_d2, exp_d3])


def names(resp):
  return [d['name'] for d in json.loads(resp.data)['data']]


def ns_and_names(resp):
  data = json.loads(resp.data)['data']
  return [(d['namespace'], d['name']) for d in data]


def dep_called(resp, name):
  ser_deps = json.loads(resp.data)['data']
  return [d for d in ser_deps if d['name'] == name][0]


def dep_called_svcs_names(resp, name):
  return [s['name'] for s in dep_called(resp, name)['svcs']]


def dep_called_pods_labels(resp, name):
  return [p['labels'] for p in dep_called(resp, name)['pods']]


if __name__ == '__main__':
  unittest.main()
