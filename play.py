from k8_kat.base.k8_kat import *
from k8_kat.base.kube_broker import *
from k8_kat.dep.kat_dep import *


def main():
  print(f"Running shell in {Utils.run_env()}")
  broker.connect()


if __name__ == '__main__':
  main()
