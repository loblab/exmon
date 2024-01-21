import random

class Source:

    def __init__(self, cfg, app):
        self.log = app.log
        self.log.debug(f'Init source: {cfg}')

    def sample(self):
        point = {}
        point['foo'] = random.randint(0, 100)
        point['bar'] = random.randint(0, 100)
        return point
