import os, sys, unittest
from zope.testing import doctest
from Testing import ZopeTestCase
from Testing.ZopeTestCase import PortalTestCase 
from Testing.ZopeTestCase import FunctionalDocFileSuite
from Products.OpenPlans.tests.openplanstestcase import OpenPlansTestCase
from opencore.testing.layer import OpenPlansLayer
from opencore.tasktracker.tests import readme_setup
from opencore.testing import *


#optionflags = doctest.REPORT_ONLY_FIRST_FAILURE | doctest.ELLIPSIS
optionflags = doctest.ELLIPSIS

import warnings; warnings.filterwarnings("ignore")

def hello_world(context, howdy=False):
    return "Hello world: %s howdy=%s" %(context, howdy)

def test_suite():
    import pdb
    from Products.PloneTestCase import setup
    from Products.PloneTestCase.PloneTestCase import FunctionalTestCase
    from Testing.ZopeTestCase import FunctionalDocFileSuite, installProduct
    
    from opencore.testing import noLongerProvides
    from pprint import pprint
    from zope.component import getMultiAdapter, getUtility
    from zope.interface import alsoProvides
    import transaction as txn
    from interfaces import IClockQueue
    
    setup.setupPloneSite()
    def base_setup(tc):
        readme_setup(tc)
        tc._refreshSkinData()
        tc.request = tc.app.REQUEST
        tc.response = tc.request.RESPONSE
        tc.homepage = getattr(tc.portal, 'site-home')
        tc.projects = tc.portal.projects

    globs = locals()

    clockq = FunctionalDocFileSuite("clock-queue.txt",
                                    optionflags=optionflags,
                                    package='sputnik',
                                    test_class=OpenPlansTestCase,
                                    globs = globs,
                                    setUp=base_setup
                                    )

    clockq.layer = OpenPlansLayer
    return unittest.TestSuite((delete, clockq))


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
