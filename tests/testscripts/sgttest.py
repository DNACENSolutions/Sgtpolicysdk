
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
        dnac_obj = DNACenterSGTPolicyAPI(server=dnac_config['server'],username=dnac_config['username'],
        							 password=dnac_config['password'],version=dnac_config['version'])
        dnac_obj.testinput = testinput
        self.parent.parameters['dnac_obj'] = dnac_obj

class Test_all_sgts(aetest.Testcase):
    @aetest.test
    def test1_create_sgts(self, dnac_obj):
        logging.info("Creating all SGTs from the input")
        steps=Steps()
        for sgtitem in dnac_obj.testinput["SGTINPUTS"]["CREATESGTLIST"]:
            with steps.start("Creating SGT with SGT inputs",continue_= True) as step:
                with step.start("Creating SGT: {}".format(sgtitem['sgName']),continue_= True):
                    if not dnac_obj.securitygroups.createSecurityGroup(sgtitem["sgName"],sgtitem["sgTag"])['status']:
                        step.failed("Failed creating sgt:{}".format(sgtitem['sgName']))
                    else: 
                        dnac_obj.securitygroups.pushAndVerifySecurityGroups()
                        logging.info("Created SGT: {}".format(sgtitem['sgName']))     

    @aetest.test
    def test2_create_sgts_with_vn(self, dnac_obj):
        logging.info("Creating all SGTs from the input")
        steps=Steps()
        for sgtitem in dnac_obj.testinput["SGTINPUTS"]["CREATESGTVNLIST"]:
            with steps.start("Creating SGT with SGT inputs",continue_= True) as step:
                with step.start("Creating SGT: {}".format(sgtitem['sgName']),continue_= True):
                    if not dnac_obj.securitygroups.createSecurityGroup(sgtitem["sgName"],
                                sgtitem["sgTag"],virtualNetworks=(sgtitem["virtualNetworks"]))['status']:
                        step.failed("Failed creating sgt:{}".format(sgtitem['sgName']))
                    else:
                        dnac_obj.securitygroups.pushAndVerifySecurityGroups()
                        logging.info("Created SGT: {}".format(sgtitem['sgName']))

    @aetest.test
    def test3_get_sgts_groupid(self, dnac_obj):
        logging.info("Get all SGTs group ID details from the input")
        steps=Steps()
        for sgtitem in dnac_obj.testinput["SGTINPUTS"]["GETSGTLIST"]:
            with steps.start("Getting SGT group ID with SGT inputs",continue_= True) as step:
                with step.start("Getting SGT group ID details: {}".format(sgtitem["sgName"]),continue_= True):
                    if not dnac_obj.securitygroups.getSecurityGroupIdByName(sgtitem["sgName"])['status']:
                        step.failed("Failed getting sgt group ID details:{}".format(sgtitem["sgName"]))
                    else:
                        logging.info("Got SGT group ID details: {}".format(sgtitem['sgName']))
                        logging.info(dnac_obj.securitygroups.getSecurityGroupIdByName(sgtitem["sgName"]))

    @aetest.test
    def test4_get_sgts_grouptag(self, dnac_obj):
        logging.info("Get all SGTs group tag details from the input")
        steps=Steps()
        for sgtitem in dnac_obj.testinput["SGTINPUTS"]["GETSGTLIST"]:
            with steps.start("Getting SGT group tag with SGT inputs",continue_= True) as step:
                with step.start("Getting SGT group tag details: {}".format(sgtitem["sgName"]),continue_= True):
                    if not dnac_obj.securitygroups.getSecurityGroupIdByName(sgtitem["sgName"])['status']:
                        step.failed("Failed getting sgt group tag details:{}".format(sgtitem["sgName"]))
                    else:
                        logging.info("Got SGT group tag details: {}".format(sgtitem['sgName']))
                        logging.info(dnac_obj.securitygroups.getSecurityGroupTagByName(sgtitem["sgName"]))

    @aetest.test
    def test5_get_sgts_groupcount(self, dnac_obj):
        logging.info("Get Total SGT group count")
        totalsgtcount = dnac_obj.securitygroups.getSecurityGroupCount()
        logging.info(totalsgtcount)

    @aetest.test
    def test6_check_sgts_exist_in_dnac(self, dnac_obj):
        logging.info("Verify SGTs from the input present in DNAC")
        result = dnac_obj.securitygroups.checkSecurityGroupsExistingInDnac((dnac_obj.testinput["SGTINPUTS"]["SECURITYGROUPLIST"]))
        logging.info(result)

    @aetest.test
    def test7_update_virtualnetworks_sgts(self, dnac_obj):
        logging.info("Update all SGTs Virtual networks from the input")
        steps=Steps()
        for sgtitem in dnac_obj.testinput["SGTINPUTS"]["UPDATESGTVNLIST"]:
            with steps.start("Updating SGT Virtual Networks with SGT inputs",continue_= True) as step:
                with step.start("Updating SGT Virtual Networks: {}".format(sgtitem['sgName']),continue_= True):
                    if not dnac_obj.securitygroups.updateSecurityGroup(sgtitem["sgName"],
                                virtualNetworks=(sgtitem["virtualNetworks"]))['status']:
                        step.failed("Failed updating sgt VN:{}".format(sgtitem['sgName']))
                    else:    
                        dnac_obj.securitygroups.pushAndVerifySecurityGroups()
                        logging.info("Updated SGT VN : {}".format(sgtitem['sgName']))
        
    @aetest.test
    def test8_update_sgts_tag(self, dnac_obj):
        logging.info("Update all SGTs tag from the input")
        steps=Steps()
        for sgtitem in dnac_obj.testinput["SGTINPUTS"]["UPDATESGTTAGLIST"]:
            with steps.start("Updating SGT Tag with SGT inputs",continue_= True) as step:
                with step.start("Updating SGT Tag: {}".format(sgtitem["sgName"]),continue_= True):
                    if not dnac_obj.securitygroups.updateSecurityGroup(sgtitem["sgName"],sgtitem["sgTag"])['status']:
                        step.failed("Failed creating sgt tag: {}".format(sgtitem["sgName"]))
                    else:
                        dnac_obj.securitygroups.pushAndVerifySecurityGroups()
                        logging.info("Updated SGT Tag: {}".format(sgtitem['sgName']))

    @aetest.test
    def test9_update_sgts_description(self, dnac_obj):
        logging.info("Update all SGTs description from the input")
        steps=Steps()
        for sgtitem in dnac_obj.testinput["SGTINPUTS"]["UPDATESGTDESLIST"]:
            with steps.start("Updating SGT description with SGT inputs",continue_= True) as step:
                with step.start("Updating SGT description: {}".format(sgtitem["sgName"]),continue_= True):
                    if not dnac_obj.securitygroups.updateSecurityGroup(sgtitem["sgName"],description=sgtitem["description"])['status']:
                        step.failed("Failed creating sgt description: {}".format(sgtitem["sgName"]))
                    else:
                        dnac_obj.securitygroups.pushAndVerifySecurityGroups()
                        logging.info("Updated SGT description: {}".format(sgtitem['sgName']))

    @aetest.test
    def test10_delete_sgts(self, dnac_obj):
        logging.info("Deleting all SGTs from the input")
        steps=Steps()
        for sgtitem in dnac_obj.testinput["SGTINPUTS"]["DELETESGTLIST"]:
            with steps.start("Deleting SGT with SGT inputs",continue_= True) as step:
                with step.start("Deleting SGT: {}".format(sgtitem["sgName"]),continue_= True):
                    if not dnac_obj.securitygroups.deleteSecurityGroupByName(sgtitem["sgName"])['status']:
                        step.failed("Failed deleting sgt:{}".format(sgtitem["sgName"]))
                    else:
                        dnac_obj.securitygroups.pushAndVerifySecurityGroups()
                        logging.info("Deleted SGT: {}".format(sgtitem['sgName']))

    @aetest.test
    def test11_get_sgtsummary(self, dnac_obj):
        logging.info("Getting SGTs summary details")
        logging.info(dnac_obj.securitygroups.get_securityGroup_summary())

