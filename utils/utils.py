import os
import random
import string
import subprocess

class Utils:

  @staticmethod
  def shell_exec(cmd):
    formatted_cmd = cmd.split(' ')
    output = subprocess.run(
      formatted_cmd,
      stdout=subprocess.PIPE
    )
    return output.stdout

  @staticmethod
  def run_env():
    return os.environ.get('ENVIRONMENT', 'development')

  @staticmethod
  def is_prod():
    return Utils.run_env() == 'production'

  @staticmethod
  def is_dev():
    return Utils.run_env() == 'development'

  @staticmethod
  def is_test():
    return Utils.run_env() == 'test'

  @staticmethod
  def is_ci():
    return Utils.is_test() and os.environ.get('CI')

  @staticmethod
  def is_ci_keep():
    return os.environ.get("CI") == 'keep'

  @staticmethod
  def is_non_trivial(dict_array):
    if not dict_array:
      return False
    return [e for e in dict_array if e]

  @staticmethod
  def is_either_hash_in_hash(big_hash, little_hashes):
    little_tuples = [list(h.items())[0] for h in little_hashes]
    for _tuple in (big_hash or {}).items():
      if _tuple in little_tuples:
        return True
    return False

  @staticmethod
  def try_or(lam, fallback=None):
    try:
      return lam()
    except:
      return fallback

  @staticmethod
  def dict_to_eq_str(_dict):
    return ",".join(
      ["=".join([k, str(v)]) for k, v in _dict.items()]
    )

  @staticmethod
  def parse_dict_array(_string):
    parts = _string.split(',')
    return [Utils.parse_dict(part) for part in parts]

  @staticmethod
  def parse_dict(encoded_dict):
    result_dict = {}
    for encoded_kv in encoded_dict.split(','):
      key, value = encoded_kv.split(':')
      result_dict[key] = value
    return result_dict

  @staticmethod
  def rand_str(string_len=10):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(string_len))

  @staticmethod
  def fqcn(o):
    module = o.__class__.__module__
    if module is None or module == str.__class__.__module__:
      return o.__class__.__name__
    else:
      return module + '.' + o.__class__.__name__

  @staticmethod
  def coerce_cmd_format(cmd):
    if isinstance(cmd, str):
      return cmd.split(" ")
    else:
      return cmd

  @staticmethod
  def flatten(l):
    return [item for sublist in l for item in sublist]
