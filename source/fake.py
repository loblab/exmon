import random

class Source:

    def __init__(self, log, cfg):
        self.log = log
        self.cfg = cfg
        self.log.debug(f'Init source: {self.cfg}')

    def sample(self):
        point = {}
        point['foo'] = random.randint(0, 100)
        point['bar'] = random.randint(0, 100)
        return point
