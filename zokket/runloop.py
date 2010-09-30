import select

class DefaultRunloop(object):
    @classmethod
    def set_runloop(cls, rl):
        cls._runloop = rl()
    
    @classmethod
    def run(cls):
        return cls.default().run()
    
    @classmethod
    def default(cls):
        if not hasattr(cls, '_runloop'):
            cls.set_runloop(Runloop)
        
        return cls._runloop

class Runloop(object):
    def __init__(self):
        self.poll = poll_select
        self.sockets = []
        self.timers = []
        self.running = False
    
    def timeout(self):
        try:
            runtimes = [timer.timeout() for timer in self.timers]
            runtimes.sort()
            timeout = runtimes.pop(0)
            if timeout < 0.0:
                return 0
            return timeout
        except:
            return 180
    
    def run(self):
        self.running = True
        
        try:
            while self.running:
                self.poll(self.sockets, self.timeout())
                [timer.execute() for timer in self.timers if timer.timeout() <= 0.0]
        except KeyboardInterrupt:
            self.running = False
        
        [s.close() for s in self.sockets if s.socket]

def poll_select(sockets, timeout=30):
    r = filter(lambda x: x.readable(), sockets)
    w = filter(lambda x: x.writable(), sockets)
    e = filter(lambda x: x.socket != None, sockets)
    
    (rlist, wlist, xlist) = select.select(r, w, e, timeout)
    
    for s in xlist:
        s.handle_except_event()
    
    for s in rlist:
        s.handle_read_event()
    
    for s in wlist:
        s.handle_write_event()
