import json
from pathlib import Path
from datetime import datetime
from ..base import BaseVisitor

class Visitor(BaseVisitor):

    def __init__(self, cfg, app):
        super().__init__(cfg, app)
        self.rootdir = Path(cfg['dir'])
        self.rootdir.mkdir(parents=True, exist_ok=True)
        self.file = cfg['file']

    def save(self, point):
        ts1 = point['time']
        # ts1 is time.time(), convert it to datetime
        ts2 = datetime.fromtimestamp(ts1)
        # generate the filename by the pattern in self.file and the timestamp
        filename = ts2.strftime(self.file)
        path = self.rootdir / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            json.dump(point, f, indent=4, sort_keys=True)
        self.log.debug(f'saved to: {path}')
