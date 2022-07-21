
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
        dnac_obj = DNACenterSGTPolicyAPI(server=dnac_config['server'],\
                   username=dnac_config['username'],password=dnac_config\
                   ['password'],version=dnac_config['version'])
        dnac_obj.testinput = testinput
        self.parent.parameters['dnac_obj'] = dnac_obj

class Test_all_sgt_policy(aetest.Testcase):
    @aetest.test
    def test1_create_sgtpolicy(self, steps, dnac_obj):
        logging.info("Creating SGT Policies")
        for sgtpolicy_data in dnac_obj.testinput["POLICYINPUTS"]["CREATEPOLICYLIST"]:
            with steps.start("Creating SGT Policy {}-{},contract:{}".format\
                            (sgtpolicy_data["srcSGName"],sgtpolicy_data["dstSGName"]\
                            ,sgtpolicy_data["accessContract"]),continue_= True) as step:
                if not dnac_obj.sgtpolicy.createSecurityGroupPolicy(sgtpolicy_data\
                             ["policy_name"],sgtpolicy_data["srcSGName"],sgtpolicy_data\
                             ["dstSGName"],sgtpolicy_data["accessContract"])['status']:
                    step.failed("Failed creating SGT Policy:{}".format\
                                                       (sgtpolicy_data["policy_name"]))
                else:
                    step.passed("Created SGT Policy: {}".format\
                                                       (sgtpolicy_data["policy_name"]))
        logging.info("Deploy after Test 3 create policy")
        dnac_obj.sgtpolicy.put_acaControllerServiceDeploy()

    @aetest.test
    def test2_update_sgtpolicy(self, steps, dnac_obj):
        logging.info("Updating SGT Policy from the input")
        for sgtpolicy_data in dnac_obj.testinput["POLICYINPUTS"]["UPDATEPOLICYLIST"]:
            with steps.start("Updating SGT Policy {}-{}".format(sgtpolicy_data["srcSGName"]\
                                     ,sgtpolicy_data["dstSGName"]),continue_= True) as step:
                if not dnac_obj.sgtpolicy.update_policy(sgtpolicy_data["srcSGName"],\
                         sgtpolicy_data["dstSGName"],new_contract_name=sgtpolicy_data\
                                                         ["accessContract"])['status']:
                    step.failed("Failed Updating Policy {}-{}".format(sgtpolicy_data\
                                                 ["srcSGName"],sgtpolicy_data["dstSGName"]))
                else:
                    step.passed("Updated SGT Policy {}-{}".format(sgtpolicy_data\
                                                 ["srcSGName"],sgtpolicy_data["dstSGName"])) 
        logging.info("Deploy after Test 4 update policy")
        dnac_obj.sgtpolicy.put_acaControllerServiceDeploy()

    @aetest.test
    def test3_get_sgtpolicy_count(self, dnac_obj):
        logging.info("Get Total SGT Policy count")
        totalpolicycount = dnac_obj.sgtpolicy.getPolicyCount()
        logging.info(totalpolicycount)
        
    @aetest.test
    def test4_check_policy_exist_in_dnac(self, dnac_obj):
        logging.info("Verify all policy from the input present in DNAC")
        result = dnac_obj.sgtpolicy.is_policy_exist_in_dnac(dnac_obj.testinput\
                                          ["POLICYINPUTS"]["POLICYCHECKLIST"])
        logging.info(result)
        if not result['status']:
            assert False

    @aetest.test
    def test5_get_all_policy_names(self, dnac_obj):
        logging.info("Get all Policy names present in DNAC")
        result = dnac_obj.sgtpolicy.getAllPolicyName()
        logging.info(result)
        
    @aetest.test
    def test6_get_sgtpolicysummary(self, dnac_obj):
        logging.info("Getting SGT Policy summary details")
        result = dnac_obj.sgtpolicy.get_policyAccessSummary()
        logging.info(result)
