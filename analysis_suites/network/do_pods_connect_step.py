from k8_kat.res.pod import pod_factory

from analysis_suites.network.network_suite import BaseNetworkStep


class DoPodsConnectStep(BaseNetworkStep):

  @staticmethod
  def result_str(result):
    noun = 'pass' if result['pass'] else 'fail'
    return f"{result['name']} @ {result['url']} --> {noun}"

  def pod_endpoint(self, pod):
    return f"{pod.ip}:{self.to_port}"

  def curl_pass_fail(self, pod):
    result = pod_factory.one_shot_curl(self.ns, url=self.pod_endpoint(pod))
    return {
      "name": pod.name,
      "pass": result['finished'],
      "url": self.pod_endpoint(pod)
    }

  def perform(self):
    pods = self.dep.pods()
    results = [self.curl_pass_fail(pod) for pod in pods]
    failures = [result for result in results if not result['pass']]
    culprits = ", ".join([result['name'] for result in failures])
    results_str = [self.result_str(r) for r in results]

    return self.record_step_performed(
      outcome=len(failures) == 0,
      outputs=results_str,
      bundle={"culprits": culprits}
    )

