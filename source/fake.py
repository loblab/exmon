import random
from .base import BaseSource

class Source(BaseSource):

    def __init__(self, cfg, app):
        super().__init__(cfg, app)

    def sample(self):
        point = {}
        point['foo'] = random.randint(0, 100)
        point['bar'] = random.randint(0, 100)
        return point
