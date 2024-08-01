import os
import sys
import time
import redis
import socket
from .base import BaseSource

class Source(BaseSource):

    def __init__(self, cfg, app):
        super().__init__(cfg, app)
        host = cfg['host']
        port = cfg['port']
        db = cfg['db']
        self.cfg = cfg.copy()

        self.log.info("Connect to Redis (%s:%d:%d)...", host, port, db)
        self.rds = redis.StrictRedis(host=host,
                port=port,
                db=db,
                decode_responses=True,
                health_check_interval=30)
        ping = self.rds.ping()
        self.log.info("Connect to Redis... OK")
        if 'hostname' in cfg:
            self.hostname = cfg['hostname']
        else:
            self.hostname = socket.gethostname()

    def sample_items(self, name, op):
        if not name in self.cfg:
            return
        items = self.cfg[name]
        values = self.rds.mget(items.values())
        values = map(op, values)
        keys = items.keys()
        self.fields.update(dict(zip(keys, values)))

    def sample(self):
        self.tags = {
            'host': self.hostname
        }
        self.fields = {}
        self.sample_items('num_items', int)
        return {
            'tags': self.tags,
            'fields': self.fields
        }
