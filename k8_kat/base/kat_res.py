class KatRes:

  def __init__(self, raw):
    self.raw = raw

  @property
  def name(self):
    return self.raw.metadata.name

  @property
  def namespace(self):
    return self.raw.metadata.namespace

  @property
  def ns(self):
    return self.namespace

  @property
  def labels(self):
    return self.raw.metadata.labels