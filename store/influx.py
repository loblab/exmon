import json
from datetime import datetime
from influxdb import InfluxDBClient

class Store:

    def __init__(self, cfg, app):
        self.log = app.log
        self.log.debug(f'cfg: {cfg}')
        host = cfg['host']
        port = cfg['port']
        user = cfg['user']
        pswd = cfg['password']
        data = cfg['data']
        self.log.info("Connect to local InfluxDB (%s:%d)...", host, port)
        self.db = InfluxDBClient(host, port, user, pswd, data, timeout=5)

    def save(self, points):
        self.db.write_points(points)
