#
from BTrees.IOBTree import IOBTree
from Products.CMFCore.interfaces import ISiteRoot
from Products.Five import BrowserView
from StringIO import StringIO
from interfaces import IClockQueue
from opencore.interfaces.adding import IAddProject
from zope.component import adapts
from zope.dottedname.resolve import resolve
from zope.interface import implements
import logging
import time
try:
    from zope.annotation import IAnnotations
except ImportError:
    from zope.app.annotation import IAnnotations


class RootClockQueue(object):
    key = 'opencore.jobqueue'
    implements(IClockQueue)
    adapts(ISiteRoot)

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
    
    def add_job(self, func, *args, **kw):
        job = Job.from_func(func, *args, **kw)
        self.queue[hash(job)] = job

    def __delitem__(self, key):
        del self.queue[key]

    def __getitem__(self, key):
        return self.queue[key]
    
    def __iter__(self):
        return (x for x in self.queue.items())


class ProjectClockQueue(RootClockQueue):
    adapts(IAddProject)


log = logging.getLogger('sputnik.clockqueue')

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

    def do_job(self, context, request):
        func = resolve(self.name)
        return func(context, request, *self.args, **self.kwargs)

    __call__ = do_job
        
    @classmethod
    def from_func(cls, func, **kwargs):
        dottedname = func.__module__ + '.' + func.__name__
        return cls(dottedname, **kwargs)

    def __repr__(self):
        return "<%s obj: %s  %s>" %(self.__class__, self.name, self.kwargs)
