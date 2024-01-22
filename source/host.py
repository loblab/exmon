import os
import sys
import time
import socket
from .base import BaseSource

def get_lan_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #s.connect(("8.8.8.8", 80))
    #s.connect(("114.114.114.114", 80))
    s.connect(("1.2.3.4", 56))
    ip_address = s.getsockname()[0]
    s.close()
    return ip_address

class Source(BaseSource):

    def __init__(self, cfg, app):
        super().__init__(cfg, app)

    def sample(self):
        point = {}
        self.sample_loadavg(point)
        self.sample_meminfo(point)
        self.sample_cpu_temp(point)
        self.sample_gpuinfo(point)
        self.sample_disk(point)
        self.sample_net(point)
        return point

    def get_disk_space(self, path):
        s = os.statvfs(path)
        return s.f_bavail * s.f_bsize / 1e9  # GB

    def sample_loadavg(self, point):
        with open('/proc/loadavg', 'r') as f:
            line = f.readline()
            cpuload = float(line.split()[0])
            point['cpu_load'] = cpuload
            #self.log.debug("CPU load: %.1f%%", cpuload)

    def sample_meminfo(self, point):
        # get memory usage from /proc/meminfo
        with open('/proc/meminfo', 'r') as f:
            line = f.readline()
            memtotal = int(line.split()[1])
            line = f.readline()
            memfree = int(line.split()[1])
            memused = (memtotal - memfree) / 1e6  # GB
            point['mem_used'] = memused
            memload = (memtotal - memfree) / memtotal * 100
            point['mem_load'] = memload
            #self.log.debug("CPU memory usage: %.1f%%", memload)

    def sample_cpu_temp(self, point):
        file='/sys/class/thermal/thermal_zone0/temp'
        if not os.path.exists(file):
            return
        with open(file, 'r') as f:
            temp = int(f.readline()) / 1000
            point['cpu_temp'] = temp
            #self.log.debug("CPU temp: %.1f'C", temp)

    def sample_gpuinfo(self, point):
        # get gpu load and memory usage from nvidia-smi
        gpuload = 0
        gpumem = 0
        if not os.path.exists('/usr/bin/nvidia-smi'):
            return
        cmd = '/usr/bin/nvidia-smi --query-gpu=utilization.gpu,utilization.memory --format=csv,noheader,nounits'
        with os.popen(cmd) as f:
            line = f.readline()
            gpuload = float(line.split(',')[0])
            gpumem = float(line.split(',')[1])
            point['gpu_load'] = gpuload
            point['gpu_mem'] = gpumem
            #self.log.debug("GPU load: %.1f%%, GPU memory usage: %.1f%%", gpuload, gpumem)

    def sample_disk(self, point):
        root = self.get_disk_space('/')
        home = self.get_disk_space('/home')
        #self.log.debug("root: %.4f(GB); home: %.4f(GB)", root, home)
        point['disk_root'] = root
        point['disk_home'] = home

    def sample_net(self, point):
        ip = get_lan_ip()
        point['lan_ip'] = ip
