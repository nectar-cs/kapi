from helpers.docker_op import DockerOp

TAR_NAME = "repo-tar.tar.gz"
WORK_DIR = "cloned-repo"

class DockerBuildOp(DockerOp):

  def __init__(self, **kwargs):
    super().__init__(None)
    self.repo_tar_url = kwargs['repo_tar_url']
    self.output_img = kwargs['output_img']
    self.docker_build_path = kwargs['docker_build_path']
    self.dockerfile_path = kwargs['dockerfile_path']

  def full_build_path(self):
    return f"{WORK_DIR}{self.docker_build_path}"

  def full_df_path(self):
    return f"{WORK_DIR}{self.dockerfile_path}"

  def full_paths(self):
    return f"{self.full_build_path()} -f {self.full_df_path()}"

  def command(self):
    return f"wget -O {TAR_NAME} {self.repo_tar_url} -q && " \
           f"mkdir {WORK_DIR} && " \
           f"tar xzf {TAR_NAME} -C {WORK_DIR} --strip-components=1 && " \
           f"docker build {self.full_paths()} -t {self.output_img} "
