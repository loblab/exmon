import json
from datetime import datetime
from elasticsearch import Elasticsearch
from .base import BaseVisitor

class Visitor(BaseVisitor):

    def __init__(self, cfg, app):
        super().__init__(cfg, app)
        url = cfg['url']
        user = cfg['user']
        password = cfg['password']
        self.log.info(f'Connect Elasticsearch {url} ...')
        self.es = Elasticsearch(url, basic_auth=(user, password))
        self.index = cfg['index']

    def save(self, point):
        self.log.info(f'Save results to database {self.index} ...')
        ts1 = point['time']
        ts2 = datetime.fromtimestamp(ts1)
        id_ts = ts2.timestamp()
        point['@timestamp'] = ts2.strftime("%Y-%m-%dT%H:%M:%SZ")
        self.log.debug(f'Point: {point}')
        resp = self.es.index(index=self.index, id=id_ts, document=point)
        resp = self.es.get(index=self.index, id=id_now)
        self.log.debug(f'Response: {resp}')
        #self.log.debug(resp['_source'])
