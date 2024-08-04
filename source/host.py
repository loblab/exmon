import os
import sys
import time
import socket
from .base import BaseSource

def get_lan_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("1.2.3.4", 56))
    ip = s.getsockname()[0]
    s.close()
    return ip

def get_wan_ip():
    ip = os.popen('curl -sL ip.sb').read()
    return ip.strip()

class Source(BaseSource):

    def __init__(self, cfg, app):
        super().__init__(cfg, app)
        if 'hostname' in cfg:
            self.hostname = cfg['hostname']
        else:
            self.hostname = socket.gethostname()
        self.nproc = 1

    def sample(self):
        self.tags = {
            'host': self.hostname
        }
        self.fields = {}
        if self.full:
            self.get_sysinfo()
        self.sample_loadavg()
        self.sample_meminfo()
        self.sample_cpu_temp()
        self.sample_gpuinfo()
        self.sample_disk()
        self.sample_uptime()
        return {
            'tags': self.tags,
            'fields': self.fields
        }

    def get_cpuinfo(self):
        with open('/proc/cpuinfo', 'r') as f:
            lines = f.readlines()
            for line in lines:
                if line.startswith('model name'):
                    cpu_model = line.split(':')[1].strip()
                    self.fields['cpu_model'] = cpu_model
                    self.tags['cpu_model'] = cpu_model
                elif line.startswith('cpu MHz'):
                    cpu_mhz = float(line.split(':')[1].strip())
                    self.fields['cpu_mhz'] = cpu_mhz
                elif line.startswith('cpu cores'):
                    cpu_cores = int(line.split(':')[1].strip())
                    self.fields['cpu_cores'] = cpu_cores
                elif line.startswith('siblings'):
                    cpu_threads = int(line.split(':')[1].strip())
                    self.fields['cpu_threads'] = cpu_threads
                    self.nproc = cpu_threads
                elif line.startswith('cache size'):
                    cpu_cache = line.split(':')[1].strip()
                    self.fields['cpu_cache'] = cpu_cache

    def get_osver(self):
        if os.path.exists('/etc/os-release'):
            with open('/etc/os-release', 'r') as f:
                lines = f.readlines()
                for line in lines:
                    if line.startswith('PRETTY_NAME='):
                        osv = line.split('=')[1].strip().strip('"')
                        self.fields['os'] = osv
                        self.tags['os'] = osv
                        break
        kernel = os.uname().release
        self.fields['kernel'] = kernel
        self.tags['kernel'] = kernel

    def get_sysinfo(self):
        self.get_cpuinfo()  # get threads/nproc first, used later
        self.get_osver()
        lan_ip = get_lan_ip()
        wan_ip = get_wan_ip()
        self.fields['lan_ip'] = lan_ip
        self.fields['wan_ip'] = wan_ip
        self.tags['wan_ip'] = wan_ip

    def get_disk_space(self, path, name):
        if not os.path.exists(path):
            return
        s = os.statvfs(path)
        avail = s.f_bavail * s.f_bsize # bytes
        self.fields['disk_avail_' + name] = avail
        if self.full:
            total = s.f_blocks * s.f_bsize # bytes
            self.fields['disk_total_' + name] = total

    def sample_loadavg(self):
        with open('/proc/loadavg', 'r') as f:
            line = f.readline()
            words = line.split()
            load1 = float(words[0])
            load5 = float(words[1])
            load15 = float(words[2])
            procinfo = words[3].split('/')
            proc_run = int(procinfo[0])
            proc_total = int(procinfo[1])
            pid = int(words[4])
            self.fields['cpu_load1'] = load1
            self.fields['cpu_load5'] = load5
            self.fields['cpu_load15'] = load15
            self.fields['proc_run'] = proc_run
            self.fields['proc_total'] = proc_total
            self.fields['proc_pid'] = pid

    def sample_meminfo(self):
        # get memory usage from /proc/meminfo
        with open('/proc/meminfo', 'r') as f:
            lines = f.readlines()
            for line in lines:
                words = line.split()
                if len(words) < 2:
                    continue
                if words[0] == 'MemAvailable:':
                    memavail = int(words[1]) * 1024
                    self.fields['mem_avail'] = memavail
                elif words[0] == 'MemTotal:':
                    if self.full:
                        memtotal = int(words[1]) * 1024
                        self.fields['mem_total'] = memtotal

    def sample_cpu_temp(self):
        thermal_zones = os.listdir('/sys/class/thermal/')
        for zone in thermal_zones:
            if zone.startswith('thermal_zone'):
                with open(f'/sys/class/thermal/{zone}/temp') as temp_file:
                    temp_mC = int(temp_file.read())
                    temp_C = temp_mC / 1000
                    self.fields['cpu_temp'] = temp_C
                    return temp_C

    def sample_gpuinfo(self):
        # get gpu load and memory usage from nvidia-smi
        gpuload = 0
        gpumem = 0
        if not os.path.exists('/usr/bin/nvidia-smi'):
            return
        if self.full:
            cmd = 'nvidia-smi --query-gpu=name,memory.total --format=csv,noheader,nounits'
            with os.popen(cmd) as f:
                line = f.readline()
                words = line.split(',')
                if len(words) < 2:
                    return
                model = words[0].strip()
                memtotal = int(words[1].strip()) * 1024 * 1024
                self.fields['gpu_model'] = model
                self.fields['gpu_mem_total'] = memtotal
                self.tags['gpu_model'] = model
        cmd = 'nvidia-smi --query-gpu=utilization.gpu,temperature.gpu,memory.free --format=csv,noheader,nounits'
        with os.popen(cmd) as f:
            line = f.readline()
            words = line.split(',')
            if len(words) < 3:
                return
            gpuload = float(words[0]) / 100
            gputemp = float(words[1])
            memfree = int(words[2]) * 1024 * 1024
            self.fields['gpu_load'] = gpuload
            self.fields['gpu_temp'] = gputemp
            self.fields['gpu_mem_free'] = memfree

    def sample_disk(self):
        self.get_disk_space('/', 'root')
        self.get_disk_space('/home', 'home')
        self.get_disk_space('/hdd', 'hdd')
        self.get_disk_space('/nas', 'hdd')

    def sample_net(self):
        ip = get_lan_ip()
        self.fields['lan_ip'] = ip

    def sample_uptime(self):
        with open('/proc/uptime', 'r') as f:
            words = f.readline().split()
            uptime = float(words[0])
            idletime = float(words[1]) / self.nproc
            self.fields['uptime'] = uptime
            self.fields['cpu_idle'] = idletime
