
# *******************************************************************************
# *                              Template Testcases
# * ----------------------------------------------------------------------------
# * ABOUT THIS TEMPLATE - Please read
# *
# * - Any comments with "#*" in front of them (like this entire comment box) are
# *   for template clarifications only and should be removed from the final
# *   product.
# *
# * - Anything enclosed in <> must be replaced by the appropriate text for your
# *   application
# *
# * Author:
# *    Pawan Singh
# *
# * Support:
# *    pawansi@cisco.com
# *
# * Description:
# *  This file contains some  testcases used by dnac test
# *
# * Note Also:
# *   the use of testcase files, and its ideas, are software development
# *   methodologies, and an optional use-case of pyATS testscripts.
# *
# * Read More:
# *   For the complete and up-to-date user guide on AEtest template, visit:
# *   URL= http://wwwin-pyats.cisco.com/documentation/html/aetest/index.html
# *
# *******************************************************************************
'''solution_longitivity_test.py
This script perform secure fabirc usecase test
Arguments:
    testbed: testbed.yaml file
Testcases:
    < provide examples on how to use this test script. >
References:
    < provide references here. >
Notes:
    < provide notes if needed >
'''
# optional author information
__author__ = ' Pawan Singh <pawansi@cisco.com>'
__copyright__ = 'Copyright 2022, Cisco Systems'
__credits__ = []
__maintainer__ = 'DNAC Solution test team'
__email__ = ' pawansi@cisco.com'
__date__ = 'Jun 14, 2022'
__version__ = 1.0

import logging
import json
import time
import traceback
from pyats import aetest
from pyats.aetest.steps import Steps
from sgtpolicysdk import DNACenterSGTPolicyAPI

# initiate Logger
logger = logging.getLogger(__name__)

class CommonSetup(aetest.CommonSetup):
    @aetest.subsection
    def setup_dnac_center(self, cluster_inputs, test_inputs):
        with open(cluster_inputs) as fh_c:
            dnac_config = json.load(fh_c)

        with open(test_inputs) as fh_t:
            testinput = json.load(fh_t)
        dnac_obj = DNACenterSGTPolicyAPI(server=dnac_config\
                   ['server'],username=dnac_config['username'],password=dnac_config\
                   ['password'],version=dnac_config['version'])
        dnac_obj.testinput = testinput
        self.parent.parameters['dnac_obj'] = dnac_obj

class Test_get_sgts_groupcount(aetest.Testcase):
    @aetest.test
    def test_get_sgts_groupcount(self, dnac_obj):
        logging.info("Get Total SGT group count")
        totalsgtcount = dnac_obj.securitygroups.getSecurityGroupCount()
        logging.info(totalsgtcount)
