from zope.interface.common.mapping import IEnumerableMapping
from zope.interface import Attribute


class IClockQueue(IEnumerableMapping):
    """map of jobs, no order expected"""
    queue = Attribute("A object representing the queue of jobs to do")
    
