import json
from pathlib import Path
from datetime import datetime

class Store:

    def __init__(self, cfg, app):
        self.log = app.log
        self.log.debug(f'cfg: {cfg}')
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
        self.log.debug(f'path: {path}')
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            json.dump(point, f, indent=4, sort_keys=True)