from kubernetes.client.rest import ApiException
from kubernetes.stream import stream

from k8_kat.base.kube_broker import broker
from helpers.res_utils import ResUtils
from k8_kat.base.kat_res import KatRes
from k8_kat.pod.pod_utils import PodUtils
from utils.utils import Utils


class KatPod(KatRes):
  def __init__(self, raw):
    super().__init__(raw)

  @property
  def kind(self):
    return "Pod"

  @property
  def labels(self):
    base = super().labels
    bad_key = 'pod-template-hash'
    return {k: base[k] for k in base.keys() if k != bad_key}

  @property
  def status(self):
    return PodUtils.true_pod_state(
      self.raw.status.phase,
      self.container_status,
      False
    )

  @property
  def full_status(self):
    return PodUtils.true_pod_state(
      self.raw.status.phase,
      self.container_status,
      True
    )

  @property
  def container(self):
    return self.raw.spec.containers[0]

  @property
  def container_status(self):
    return self.raw.status.container_statuses[0]

  @property
  def ip(self):
    return Utils.try_or(lambda: self.raw.status.pod_ip)

  @property
  def image(self):
    return self.container and self.container.image

  @property
  def container_state(self):
    status = self.container_status
    if status:
      if status.state:
        state = status.state
        return state.running or state.waiting or state.terminated
    return None

  @property
  def updated_at(self):
    return Utils.try_or(lambda: self.container_state.started_at)

  @property
  def is_running(self):
    return self.status == 'Running'

  @property
  def wtf(self):
    return 'coming soon!'

  def _perform_patch_self(self):
    broker.coreV1.patch_namespaced_pod(
      name=self.name,
      namespace=self.namespace,
      body=self.raw
    )

  def logs(self, seconds=60):
    try:
      log_dump = broker.coreV1.read_namespaced_pod_log(
        namespace=self.namespace,
        name=self.name,
        since_seconds=seconds
      )
      log_lines = log_dump.split("\n")
      return [ResUtils.try_clean_log_line(line) for line in log_lines]
    except ApiException:
      return None

  def cmd(self, command):
    return stream(
      broker.coreV1.connect_get_namespaced_pod_exec,
      self.name,
      self.namespace,
      command=Utils.coerce_cmd_format(command),
      stderr=False,
      stdin=False,
      stdout=True,
      tty=False
    )

  def __repr__(self):
    return f"Dep[{self.ns}:{self.name}({self.labels})]"
