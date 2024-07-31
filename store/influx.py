import json
from datetime import datetime
#from influxdb_client import InfluxDBClient
from influxdb import InfluxDBClient
from .base import BaseVisitor

class Visitor(BaseVisitor):

    def __init__(self, cfg, app):
        super().__init__(cfg, app)
        host = cfg['host']
        port = cfg['port']
        user = cfg['user']
        pswd = cfg['password']
        data = cfg['data']
        self.measurement = cfg['measurement']
        self.log.info(f'Connect to InfluxDB ({host}:{port}) {data}/{self.measurement}')
        self.db = InfluxDBClient(host, port, user, pswd, data, timeout=5)

    def visit(self, points):
        pdst = points.copy()
        for pt in pdst:
            pt['measurement'] = self.measurement
            pt['time'] = int(pt['time'] * 1e9)
        self.log.debug(pdst)
        self.db.write_points(pdst)
