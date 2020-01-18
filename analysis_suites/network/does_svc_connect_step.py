from k8_kat.res.pod import pod_factory

from analysis_suites.network.network_suite import BaseNetworkStep

class DoesSvcConnectStep(BaseNetworkStep):

  def perform(self):
    pod_factory.one_shot_curl(self.ns, url=super().target_url)
    output = pod_factory.one_shot_curl(self.ns, url=super().target_url)
    if output['finished']:
      super().as_positive(
        outputs=[f"{output['status']}", output['body'][0:100]],
        bundle={**output}
      )
    else:
      super().as_negative(
        outputs=["Could not connect"],
        bundle={**output}
      )
