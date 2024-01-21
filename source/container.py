import re
import sys
import subprocess

class Source:

    # Use KB as size default unit
    KB_UNIT = {
        'TiB': 1073741824,
        'GiB': 1048576,
        'MiB': 1024,
        'TB': 1000000000,
        'GB': 1000000,
        'MB': 1000,
        'kB': 1,
        'KiB': 1, # use KiB or kB as basic unit
        'B': 0.001
    }

    def __init__(self, cfg, app):
        self.log = app.log
        self.log.debug(f'Init source: {cfg}')
        self.container = cfg['container']
        if 'java' in cfg:
            self.java = cfg['java']
        else:
            self.java = False
        if 'swap' in cfg:
            self.swap = cfg['swap']
        else:
            self.swap = False

    def sample(self):
        point = {}
        self.sample_cont(point)
        if self.java:
            self.sample_swap(point)
        if self.java:
            self.sample_java(point)
        return point

    def run(self, cmdline):
        self.log.debug(cmdline)
        b = subprocess.check_output(cmdline, shell=True)
        s = bytes.decode(b).strip()
        self.log.debug(s)
        return s

    def sample_cont(self, point):
        self.log.debug(f'Get cpu/memory/netio/diskio in container {self.container} ...')
        cmdline = 'docker stats --no-stream --format "{{.CPUPerc}} {{.MemUsage}} {{.NetIO}} {{.BlockIO}}" ' + self.container
        output = self.run(cmdline)
        match = re.search('(\S+)%\s+([\d\.]+)([TGMKki]*?B).+?([\d\.]+)([TGMKki]*?B)\s+([\d\.]+)([TGMk]?B).+?([\d\.]+)([TGMk]?B)\s+([\d\.]+)([TGMk]?B).+?([\d\.]+)([TGMk]?B)', output)
        cpu = float(match.group(1)) / 100
        memory = float(match.group(2)) * self.KB_UNIT[match.group(3)]
        neti = float(match.group(6)) * self.KB_UNIT[match.group(7)]
        neto = float(match.group(8)) * self.KB_UNIT[match.group(9)]
        diski = float(match.group(10)) * self.KB_UNIT[match.group(11)]
        disko = float(match.group(12)) * self.KB_UNIT[match.group(13)]
        self.log.debug(f'cpu%: {cpu}, memory: {memory} (KiB), net I/O: {neti} / {neto} (KB), disk I/O: {diski} / {disko} (KB)')
        point['cpu'] = cpu
        point['memory'] = memory
        point['neti'] = neti
        point['neto'] = neto
        point['diski'] = diski
        point['disko'] = disko

    def sample_java(self, point):
        self.log.debug(f'Get heap/metaspace in container {self.container} ...')
        pid = self.run_in_cont('pgrep java')
        self.log.debug(f'pid: {pid}')
        output = self.run_in_cont(f'jcmd {pid} GC.heap_info')
        match = re.search('heap.+?used\s+(\d+)K', output)
        heap = int(match.group(1))
        match = re.search('Metaspace.+?used\s+(\d+)K', output)
        metaspace = int(match.group(1))
        point['heap'] = heap
        point['metaspace'] = metaspace

    def sample_swap(self, point):
        self.log.info(f'Get swap used ...')
        cmdline = "free -k | grep -i swap | awk '{print $3}'"
        output = self.run(cmdline)
        point['swap'] = int(output)
