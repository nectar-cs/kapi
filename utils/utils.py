import os
import random
import string

def run_env():
  return os.environ.get('FLASK_ENV')

def is_test():
  return run_env() == 'test'

def is_ci():
  return is_test() and os.environ.get('CI')

def is_ci_keep():
  return os.environ.get("CI") == 'keep'

def is_dev():
  return run_env() == 'development'

def is_prod():
  return run_env() == 'production'

def is_non_trivial(dict_array):
  if not dict_array:
    return False
  return [e for e in dict_array if e]

def is_either_hash_in_hash(big_hash, little_hashes):
  little_tuples = [list(h.items())[0] for h in little_hashes]
  for _tuple in (big_hash or {}).items():
    if _tuple in little_tuples:
      return True
  return False

def try_or(lam, fallback=None):
  try:
    return lam()
  except:
    return fallback

def dict_to_eq_str(_dict):
  return ",".join(
    ["=".join([k, str(v)]) for k, v in _dict.items()]
  )

def parse_dict_array(_string):
  parts = _string.split(',')
  return [parse_dict(part) for part in parts]

def parse_dict(encoded_dict):
  result_dict = {}
  for encoded_kv in encoded_dict.split(','):
    key, value = encoded_kv.split(':')
    result_dict[key] = value
  return result_dict

def rand_str(string_len=10):
  letters = string.ascii_lowercase
  return ''.join(random.choice(letters) for i in range(string_len))

def fqcn(o):
  module = o.__class__.__module__
  if module is None or module == str.__class__.__module__:
    return o.__class__.__name__
  else:
    return module + '.' + o.__class__.__name__

def coerce_cmd_format(cmd):
  if isinstance(cmd, str):
    return cmd.split(" ")
  else:
    return cmd

def flatten(l):
  return [item for sublist in l for item in sublist]
