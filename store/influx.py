import json
from datetime import datetime
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
        self.log.info("Connect to local InfluxDB (%s:%d)...", host, port)
        self.db = InfluxDBClient(host, port, user, pswd, data, timeout=5)

    def visit(self, points):
        self.db.saves(points)
