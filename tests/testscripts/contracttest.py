
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

class Test_all_access_contract(aetest.Testcase):
    @aetest.test
    def test1_create_accesscontracts(self, dnac_obj):
        logging.info("Creating Access Contract from the input")
        steps=Steps()
        for ac_data in dnac_obj.testinput["CONTRACTINPUTS"]["CREATECONTRACTLLIST"]:
            with steps.start("Creating Access Contract",continue_= True) as step:
                with step.start("Creating Access Contract: {}".format(ac_data["contract_name"]),continue_= True):
                    if not dnac_obj.accesscontracts.createNewContract(ac_data["contract_name"],description=ac_data["description"],contract_data = (ac_data["contract_data"]))['status']:
                        step.failed("Failed creating Contract:{}".format(ac_data["contract_name"]))
                    else:
                        dnac_obj.accesscontracts.put_acaControllerServiceDeploy()
                        logging.info("Created Access Contract: {}".format(ac_data["contract_name"]))
                        
    @aetest.test
    def test2_update_accesscontracts_des(self, dnac_obj):
        logging.info("Updating Access Contract description from the input")
        steps=Steps()
        for ac_data in dnac_obj.testinput["CONTRACTINPUTS"]["UPDATECONTRACTLISTDES"]:
            with steps.start("Updating Access Contract description",continue_= True) as step:
                with step.start("Updating Access Contract description: {}".format(ac_data["contract_name"]),continue_= True):
                    if not dnac_obj.accesscontracts.updateAccessContract(ac_data["contract_name"],description = ac_data["description"])['status']:
                        step.failed("Failed Updating Contract description:{}".format(ac_data["contract_name"]))
                    else:
                        dnac_obj.accesscontracts.put_acaControllerServiceDeploy()
                        logging.info("Updated Access Contract description: {}".format(ac_data["contract_name"]))       

    @aetest.test
    def test3_update_accesscontracts_data(self, dnac_obj):
        logging.info("Updating Access Contract data from the input")
        steps=Steps()
        for ac_data in dnac_obj.testinput["CONTRACTINPUTS"]["UPDATECONTRACTLISTDATA"]:
            with steps.start("Updating Access Contract data",continue_= True) as step:
                with step.start("Updating Access Contract data: {}".format(ac_data["contract_name"]),continue_= True):
                    if not dnac_obj.accesscontracts.updateAccessContract(ac_data["contract_name"],contract_data = (ac_data["contract_data"]))['status']:
                        step.failed("Failed Updating Contract data:{}".format(ac_data["contract_name"],))
                    else:
                        dnac_obj.accesscontracts.put_acaControllerServiceDeploy()
                        logging.info("Updated Access Contract data: {}".format(ac_data["contract_name"]))       

    @aetest.test
    def test4_get_accesscontracts_byname(self, dnac_obj):
        logging.info("Get all Access contract details")
        steps=Steps()
        for ac_data in dnac_obj.testinput["CONTRACTINPUTS"]["GETCONTRACTLLIST"]:
            with steps.start("Getting Access Contract data",continue_= True) as step:
                with step.start("Getting Access Contract data: {}".format(ac_data["contract_name"]),continue_= True):
                    if not dnac_obj.accesscontracts.get_contractAccessByName(ac_data["contract_name"])['status']:
                        step.failed("Failed getting Contract data:{}".format(ac_data["contract_name"]))
                    else:
                        logging.info("Got Access Contract data: {}".format(ac_data["contract_name"])) 
                        logging.info(dnac_obj.accesscontracts.get_contractAccessByName(ac_data["contract_name"]))

    @aetest.test
    def test5_get_accesscontract_count(self, dnac_obj):
        logging.info("Get Total Access Contract count")
        totalcontractcount = dnac_obj.accesscontracts.getContractCount()
        logging.info(totalcontractcount)
        
    @aetest.test
    def test6_check_contract_exist_in_dnac(self, dnac_obj):
        logging.info("Verify contracts from the input present in DNAC")
        result = dnac_obj.accesscontracts.verifyContractExistInDnac(dnac_obj.testinput["CONTRACTINPUTS"]["CONTRACTCHECKLIST"])
        logging.info(result)

    @aetest.test
    def test7_get_all_contract_names(self, dnac_obj):
        logging.info("Get all contract names present in DNAC")
        result = dnac_obj.accesscontracts.getAllContractName()
        logging.info(result)
        
    @aetest.test
    def test8_get_accesscontractsummary(self, dnac_obj):
        logging.info("Getting Access contract summary details")
        logging.info(dnac_obj.accesscontracts.get_contractAccessSummary())        

    @aetest.test
    def test9_delete_accesscontracts(self, dnac_obj):
        logging.info("Deleting all access contract from the input")
        steps=Steps()
        for ac_data in dnac_obj.testinput["CONTRACTINPUTS"]["DELETECONTRACTLIST"]:
            with steps.start("Deleting access contracts",continue_= True) as step:
                with step.start("Deleting access contract: {}".format(ac_data["contract_name"]),continue_= True):
                    if not dnac_obj.accesscontracts.delete_contractAccessByName(ac_data["contract_name"])['status']:
                        step.failed("Failed deleting access contract:{}".format(ac_data["contract_name"]))
                    else:
                        dnac_obj.accesscontracts.put_acaControllerServiceDeploy()
                        logging.info("Deleted access contract: {}".format(ac_data['contract_name']))

