#
from Products.CMFCore.interfaces import ISiteRoot
from opencore.interfaces.adding import IAddProject
from topp.clockqueue import ClockQueue
from opencore.interfaces.adding import IAddProject
from zope.component import adapts


class RootClockQueue(ClockQueue):
    adapts(ISiteRoot)
    
class ProjectClockQueue(ClockQueue):
    adapts(IAddProject)
