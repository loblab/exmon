class BaseVisitor:

    def __init__(self, cfg, app):
        self.log = app.log
        self.log.debug(f'Init store: {cfg}')
        self.name = cfg['module']

    def save(self, point):
        raise NotImplementedError

    def visit(self, points):
        for pt in points:
            self.save(pt)
