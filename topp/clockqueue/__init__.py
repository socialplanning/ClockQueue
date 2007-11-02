from BTrees.IOBTree import IOBTree
from Products.Five import BrowserView
from StringIO import StringIO
from interfaces import IClockQueue
from zope.dottedname.resolve import resolve
from zope.interface import implements
import logging
import time

try:
    from zope.annotation import IAnnotations
except ImportError:
    from zope.app.annotation import IAnnotations

log = logging.getLogger('topp.clockqueue')

class AnnotationQueue(object):
    key = None

    def __init__(self, context):
        self.context = context

    @property
    def queue(self):
        queue = getattr(self, '_queue', None)
        if queue is None:
            annotations = IAnnotations(self.context)
            if not annotations.has_key(self.key):
                annotations[self.key] = IOBTree()
            self._queue = annotations[self.key]
        return self._queue

    def __delitem__(self, key):
        del self.queue[key]

    def __getitem__(self, key):
        return self.queue[key]
    
    def __iter__(self):
        return (x for x in self.queue.items())


class ClockQueue(AnnotationQueue):
    key = 'opencore.jobqueue'
    implements(IClockQueue)
    
    def add_job(self, func, *args, **kw):
        job = Job.from_func(func, *args, **kw)
        self.queue[job.id] = job
        return job.id



def sanitize(data):
    if isinstance(data, list) or isinstance(data, tuple):
        data = [sanitize(datum) for datum in data]
        return tuple(data)
    if isinstance(data, dict):
        data = [(sanitize(key), sanitize(val)) for key, val in data.items()]
        return tuple(data)
    if isinstance(data, set):
        return frozenset(data)
    return data

def sane_hash(data):
    """
    braindead hashing::
    
    >>> from topp import clockqueue 
    >>> clockqueue.sanitize(dict(mom=[dict(joe=1)], joe=set))
    (('joe', <type 'set'>), ('mom', ((('joe', 1),),)))
    >>> clockqueue.sane_hash(dict(mom=[dict(joe=1)], joe=set))
    (('joe', <type 'set'>), ('mom', ((('joe', 1),),)))
    >>> reload(clockqueue)
    <module 'topp.clockqueue' from '/Users/whit/dev/nui2/src/ClockQueue/topp/clockqueue/__init__.py'>
    >>> clockqueue.sane_hash(dict(mom=[dict(joe=1)], joe=set))
    -326468521
    >>> clockqueue.sane_hash(dict(mom=[dict(joe=1), set()], joe=set()))
    -2047399017

    >>> clockqueue.sane_hash(({}, [], set))
    """
    return hash(sanitize(data))
    

class QueueMaster(BrowserView):
    def __init__(self, context, request):
        self.context, self.request = context, request
        self.output = StringIO()

    def do_a_job(self, name, job):
        jobout = job(self.context, self.request)
        out = StringIO()
        print >> out, '%s ::' %name
        print >> out, 'queued: %s' %(time.ctime(job.start_time))
        print >> out, 'start time: %s' %(time.ctime(job.start_time))
        print >> out, 'elapsed: %d' %(time.time() - job.start_time)
        print >> out, jobout 
        print >> out, '----'
        out = out.getvalue()
        log.info(out)
        print >> self.output, out
        
    def empty_queue(self):
        queue = IClockQueue(self.context)
        for name, job in queue:
            self.do_a_job(name, job)
            del queue[name]
        return self.output.getvalue()


class Job(object):
    """a job"""
    def __init__(self, name, *args, **kwargs):
        self.kwargs = kwargs
        self.args = args
        self.name = name
        self.start_time = time.time()

    @property
    def id(self):
        return sane_hash((self.name, self.args, self.kwargs))

    def do_job(self, context, request):
        func = resolve(self.name)
        return func(context, request, *self.args, **self.kwargs)

    __call__ = do_job
        
    @classmethod
    def from_func(cls, func, *args, **kwargs):
        dottedname = func.__module__ + '.' + func.__name__
        return cls(dottedname, *args, **kwargs)

    @property
    def __dottedname__(self):
        return self.__module__ + '.' + self.__class__.__name__
    
    def __repr__(self):
        return "<%s '%s'  args:%s kw:%s>" %(self.__dottedname__, self.name, self.args, self.kwargs)
