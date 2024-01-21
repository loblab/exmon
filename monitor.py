#!/usr/bin/env python3
import os
import sys
import json
import time
import logging
import argparse
import importlib
from pathlib import Path

DESCRIPTION = 'Extensible monitor by Python'
VERSION = "pymon ver 0.0.6 (1/21/2024)"

class Monitor:

    LOG_LEVEL = {
        'err': logging.ERROR,
        'error': logging.ERROR,
        'warn': logging.WARNING,
        'info': logging.INFO,
        'debug': logging.DEBUG
    }

    def __init__(self, desc, ver):
        argps = argparse.ArgumentParser(description=desc)
        argps.add_argument('-V', '--version', action='version', version=ver)
        argps.add_argument('-L', '--log', dest='logLevel', type=str,
            default='info',
            choices=Monitor.LOG_LEVEL.keys(),
            help='log level, default: info')
        argps.add_argument('-c', '--config', dest='config', type=Path,
            required=True, action='append',
            help="config files, json format, can be multiple: -c 1.json -c 2.json")
        self.args = argps.parse_args()
        self.init_logger()

        self.log.info(desc)
        self.log.info(ver)
        self.log.info(f'Log level: {self.args.logLevel}')

        self.progPath = Path(sys.argv[0]).resolve()
        self.progDir = self.progPath.parent

        self.log.debug(f'ProgDir: {self.progDir}')
        self.log.debug(f'ProgPath: {self.progPath}')
        self.log.info(f'Command line: {sys.argv}')
        self.log.debug(self.args)

    def init_logger(self):
        self.log = logging.getLogger('monitor')
        self.log.setLevel(Monitor.LOG_LEVEL[self.args.logLevel])

        ch = logging.StreamHandler(sys.stdout)
        #ch.setLevel(logging.DEBUG)
        logfmt = f'%(asctime)s.%(msecs)03d - %(levelname)s - %(message)s'
        formatter = logging.Formatter(logfmt, datefmt='%Y/%m/%d %H:%M:%S')
        ch.setFormatter(formatter)
        self.log.addHandler(ch)

    def load_cfgfile(self, cfgfile):
        self.log.debug(f'Load config file: {cfgfile} ...')
        try:
            with open(cfgfile, 'r') as f:
                cfg = json.load(f)
        except Exception as e:
            self.log.error(f'Load config file {cfgfile} failed: {e}')
            return None
        return cfg

    @staticmethod
    def merge_dict(cfg, c):
        for k in c:
            if k in cfg:
                if isinstance(cfg[k], list):
                    cfg[k].extend(c[k])
                elif isinstance(cfg[k], dict):
                    cfg[k].update(c[k])
                else:
                    cfg[k] = c[k]
            else:
                cfg[k] = c[k]

    def load_config(self):
        cfg = None
        for cfgfile in self.args.config:
            c = self.load_cfgfile(cfgfile)
            if cfg is None:
                cfg = c
            else:
                self.merge_dict(cfg, c)
        self.log.debug(json.dumps(cfg, sort_keys=True, indent=4))
        return cfg

    def init_source(self, cfg):
        module = importlib.import_module(cfg['module'])
        return module.Source(cfg, self)

    def init_store(self, cfg):
        module = importlib.import_module(cfg['module'])
        return module.Store(cfg, self)

    def init_sources(self, cfgs):
        sources = []
        for cfg in cfgs:
            sources.append(self.init_source(cfg))
        return sources

    def init_stores(self, cfgs):
        stores = []
        for cfg in cfgs:
            stores.append(self.init_store(cfg))
        return stores

    def sample_points(self):
        points = []
        for source in self.sources:
            pts = source.sample()
            if not isinstance(pts, list):
                pts = [pts]
            for pt in pts:
                if 'time' not in pt:
                    pt['time'] = time.time()
            points.extend(pts)
        return points

    def save_point(self, point):
        for store in self.stores:
            store.save(point)

    def save_points(self, points):
        if not isinstance(points, list):
            points = [points]
        for point in points:
            self.save_point(point)

    def main(self):
        self.cfg = self.load_config()
        self.log.debug(self.cfg)
        self.sources = self.init_sources(self.cfg['source'])
        self.stores = self.init_stores(self.cfg['store'])
        points = self.sample_points()
        self.save_points(points)
        return 0

if __name__ == '__main__':
    app = Monitor(DESCRIPTION, VERSION)
    sys.exit(app.main())
