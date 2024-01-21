#!/usr/bin/env python
import os
import sys
import json
import time
import logging
import argparse
import importlib
from pathlib import Path

DESCRIPTION = 'Extensible monitor by Python'
VERSION = "pymon ver 0.0.3 (1/21/2024)"

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
            required=True,
            help="config file, json format")
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

    def load_config(self, cfgfile):
        self.log.debug(f'Load config file: {cfgfile} ...')
        try:
            with open(cfgfile, 'r') as f:
                cfg = json.load(f)
        except Exception as e:
            self.log.error(f'Load config file {cfgfile} failed: {e}')
            return None
        self.log.debug(json.dumps(cfg, indent=4))
        return cfg

    def init_source(self):
        cfg = self.cfg['source']
        module = importlib.import_module(cfg['module'])
        self.source = module.Source(self.log, cfg)

    def main(self):
        self.cfg = self.load_config(self.args.config)
        self.init_source()
        points = self.source.sample()
        self.log.debug(f'Points: {points}')
        return 0

if __name__ == '__main__':
    app = Monitor(DESCRIPTION, VERSION)
    sys.exit(app.main())
