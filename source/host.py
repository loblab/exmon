import os
import sys
import time
import psutil
import GPUtil

class Source:

    def __init__(self, cfg, app):
        self.log = app.log
        self.log.debug(f'Init source: {cfg}')

    def sample(self):
        point = {}

        t1 = time.time()
        self.sample_host(point)
        t2 = time.time()
        dur = t2 - t1
        self.log.debug(f'sample_host takes {dur:.3f} seconds')

        self.sample_disk(point)
        t3 = time.time()
        dur = t3 - t2
        self.log.debug(f'sample_disk takes {dur:.3f} seconds')
        return point

    def get_disk_space(self, path):
        s = os.statvfs(path)
        return s.f_bavail * s.f_bsize / 1e9  # GB

    def sample_host(self, point):
        cpuload = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory()
        temp = psutil.sensors_temperatures()
        if 'coretemp' in temp:
            cputemp = temp['coretemp'][0].current
        elif 'k10temp' in temp:
            cputemp = temp['k10temp'][0].current
        else:
            cputemp = 0
        point['cpuload'] = cpuload
        point['memload'] = mem.percent
        point['cputemp'] = cputemp
        self.log.debug("CPU load: %.1f%%, CPU memory usage: %.1f%%, CPU temp: %.1f'C", cpuload, mem.percent, cputemp)

        gpus = GPUtil.getGPUs()
        if len(gpus) > 0:
            gpu = gpus[0]
            gpuload = gpu.load * 100
            gpumem = gpu.memoryUtil * 100
            fields = points[0]["fields"]
            point["gpuload"] = round(gpuload, 2)
            point["gpumem"] = round(gpumem, 2)
            self.log.debug("GPU load: %.1f%%, GPU memory usage: %.1f%%", gpuload, gpumem)

    def sample_disk(self, point):
        root = self.get_disk_space('/')
        home = self.get_disk_space('/home')
        self.log.debug("root: %.4f(GB); home: %.4f(GB)", root, home)
        point['diskroot'] = root
        point['diskhome'] = home
