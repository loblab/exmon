import re
import sys
import subprocess

class BaseSource:

    def __init__(self, cfg, app):
        self.log = app.log
        self.log.debug(f'Init source: {cfg}')
        self.name = cfg['module']
        self.full = False # full mode or quick mode

    def run(self, cmdline):
        self.log.debug(cmdline)
        b = subprocess.check_output(cmdline, shell=True)
        s = bytes.decode(b).strip()
        self.log.debug(s)
        return s
