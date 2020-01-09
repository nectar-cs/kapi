import os
from k8_kat.base.kube_broker import broker

os.environ['FLASK_ENV'] = 'test'
os.environ['KAT_ENV'] = 'test'
broker.connect_or_raise()