import os
import statistics

class Visitor:

    FMAP = {
        'min': min,
        'max': max,
        'sum': sum,
        'mean': statistics.mean,
        'median': statistics.median,
        'mode': statistics.mode,
        'stdev': statistics.stdev,
        'variance': statistics.variance,
    }

    def __init__(self, cfg, app):
        self.log = app.log
        self.log.debug(f'Init trigger: {cfg}')
        self.name = cfg['module']
        self.qsize = cfg['qsize']
        self.field = cfg['field']
        self.function = cfg['function']
        self.condition = cfg['condition']
        self.action = cfg['action']
        self.queue = []

    def visit(self, points):
        for pt in points:
            self.queue.append(pt)
            if len(self.queue) > self.qsize:
                self.queue.pop(0)
                self.check()

    def check(self):
        a = [pt[self.field] for pt in self.queue]
        func = self.FMAP[self.function]
        val = func(a)
        self.log.debug(f'{self.function}({a}) = {val}')
        expr = f'{val} {self.condition}'
        self.log.debug(f'Eval: {expr}')
        if eval(expr):
            self.log.info(f'Triggered action: {self.action}')
            os.system(self.action)
