class BaseStore:

    def __init__(self, cfg, app):
        self.log = app.log
        self.log.debug(f'Init store: {cfg}')
        self.name = cfg['module']

    def write_point(self, point):
        raise NotImplementedError

    def save(self, points):
        for pt in points:
            self.write_point(pt)
