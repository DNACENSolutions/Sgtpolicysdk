# -*- coding: utf-8 -*-
"""Cisco DNA Center Devices API wrapper.
Copyright (c) 2019-2021 Cisco Systems.
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
from __future__ import absolute_import, division, print_function, unicode_literals

from builtins import *

from past.builtins import basestring

from ...client_manager import DnacClientManager
from ...utils import (
    apply_path_params,
    check_type,
    dict_from_items_with_values,
    dict_of_str,
)

import logging
logger = logging.getLogger("accessContracts")

DEFAULT_AC_TIMEOUT=60
DEFAULT_TASK_COMPLETION_TIMEOUT=120
DEFAULT_SUMMARY_TIMEOUT=240

DEFAULT_VERSION = "v2"
CONTRACT_URL_PATH = "/data/customer-facing-service/contract/access"
CONTRACT_URL_PATH2 = "/data/cfs-intent/contract/access"
CONTRACT_URL_SUMMARY_PATH = "/data/customer-facing-service/summary/contract/access"
DEFAULT_HEADERS = {'Content-Type': 'application/json'}
ACACONTROLLERPATH = "/v1/aca-controller-service"

class AccessContracts(object):
    """Cisco DNA Center AccessContracts API (version: 2.3.4.0).
    Wraps the DNA Center Devices
    API and exposes the API as native Python
    methods that return native Python objects.
    """
    def __init__(self, session):
        """Initialize a new Devices
        object with the provided RestSession.
        Args:
            session(RestSession): The RESTful session object to be used for
                API calls to the DNA Center service.
        Raises:
            TypeError: If the parameter types are incorrect.
        """
        check_type(session._session, DnacClientManager)
        super(AccessContracts, self).__init__()
        self._session = session._session
        self._task = session.task
        self.log = logger


    def createNewContract(self,contract_name,description=None,contract_data = []):
        """
        Create access contract
        Args:
            contract_name(str): Contract name
            description(str): Description of the contract
            contract_data(list): 
                [{"access'(Mandatory): "DENY", 
                  "applicationName"(Mandatory):"wap-vcal-s",
                  "dstNetworkIdentities"(Mandatory):[{"protocol":"UDP","ports":"9207"},
                                          {"protocol":"TCP","ports":"9207"}], 
                  "logging"(Mandatory): "OFF"}]
            
        Raises:
            TypeError: If the parameter types are incorrect.
        """
        check_type(contract_name,basestring)
        check_type(description,basestring)
        check_type(contract_data,list)
        
        self.log.info("Start to create new contract {} in DNAC".format(contract_name))
        new_contract = [
            {
                "name" : contract_name,
                "description" : description,
                "type": "contract",
                "clause": [{ "access": "PERMIT", "logging": "OFF"}],
                "contractClassifier" : contract_data
            }
        ]
        contract_response = self.post_contractAccess(json=new_contract, timeout=DEFAULT_AC_TIMEOUT)
        taskStatus = self._task.wait_for_task_complete(contract_response, timeout=DEFAULT_TASK_COMPLETION_TIMEOUT)
        self.log.info(taskStatus)
        if (taskStatus['isError']):
            self.log.error("creating new contract failed:{0}".format(taskStatus['failureReason']))
            return {'status':False, "failureReason":"Creating access contract {} failed:{}".format(taskStatus['failureReason'])}
        else:
            self.log.info("##################################################################################")
            self.log.info("#----SUCCESSFULLY CREATED NEW CONTRACT {}----#".format(contract_name))
            self.log.info("##################################################################################")
            return {'status':True}

    def getAllContractName(self):
        """
        GET all contract name list
        Function name: getAllContractName
        Input: 
        Output: List of names of all available contracts in DNAC.
        """
        self.log.info("Start to get all contract names in DNAC")
        contractlist = []
        params = {'offset': 0, 'limit': 5000, 'contractSummary': 'true'}
        contract_response = self.get_contractAccessSummary(params=params,timeout=DEFAULT_SUMMARY_TIMEOUT)
        contract_response_sum = contract_response["response"][0]
        for response in contract_response_sum["acaContractSummary"]:
            name = response["name"]
            contractlist.append(name)
        return {'status':True, 'contracts' : contractlist}
            
    def getContractCount(self):
        """
        Function: 
        GET total access contract count
        """
        self.log.info("Start to count contract in DNAC")
        params = {'offset': 0, 'limit': 5000, 'contractSummary': 'true'}
        contract_response = self.get_contractAccessSummary(params=params,timeout=DEFAULT_SUMMARY_TIMEOUT)
        self.log.info(contract_response)
        contract_response_sum = contract_response["response"][0]
        count = contract_response_sum["totalContractCount"]
        return {'status':True, 'count': count}

    def verifyContractExistInDnac(self, contract_list, expect=True):
        """
        Verify access contract present in DNAC.
        Args:
            contract_list(list): Provide contract name list
            expect(bool): True/False
        Raises:
            TypeError: If the parameter types are incorrect.
        """
        check_type(contract_list,list)
        check_type(expect,bool)

        self.log.info("Start to check contract list in DNAC")
        missing_list= []
        exist_list = []
        contractlist_aca = self.getAllContractName()
        for name in contract_list:
            if name in contractlist_aca:
                exist_list.append(name)
                continue
            else:
                missing_list.append(name)
        self.log.info("Contracts to check {}".format(contract_list))
        self.log.info("All contract names in DNAC {}".format(contractlist_aca))

        if expect:
            if len(missing_list)==0:
                self.log.info("#####################################################")
                self.log.info("#----Contracts exists in DNAC {}----#".format(contract_list))
                self.log.info("#####################################################")
                return {'status':True}
            else:
                self.log.error("Some Contracts do not exist in DNAC "
                                    "or have different information".format(missing_list))
                return {'status':False, 'failureReason':"Some contracts do not exist in DNAC"}
        else:
            if len(missing_list)==len(contract_list):
                self.log.info("#####################################################")
                self.log.info("#----as expected Contracts list doesn't exists in DNAC {}----#".format(contract_list))
                self.log.info("#####################################################")
                return {'status':True}
            else:
                self.log.error("Some contracts still exist in DNAC "
                                    "or have different information".format(exist_list))
                return {'status':True, 'failureReason':"Some contracts still exist in DNAC."}

    def updateAccessContract(self, contract_name,description=None,contract_data=None,clause=None,**kwargs):
        """
        Update access contract
        Args:
            contract_name(str): Contract name
            description(str): Description of the contract
            contract_data(list): 
                [{"access'(Mandatory): "DENY", 
                  "applicationName"(Mandatory):"wap-vcal-s",
                  "dstNetworkIdentities"(Mandatory):[{"protocol":"UDP","ports":"9207"},
                                          {"protocol":"TCP","ports":"9207"}], 
                  "logging"(Mandatory): "OFF"}]
            clause(list): Global parameter for contract data 
        Raises:
            TypeError: If the parameter types are incorrect.
        """
        check_type(contract_name,basestring)
        check_type(description,basestring)
        check_type(contract_data,list)
        check_type(clause,list)

        self.log.info("Start to update contract {}".format(contract_name))
        self.log.info("Update contract")
        params = {"name" : contract_name}
        contract_response = self.get_contractAccess(params=params)
        ac_data = {
            "id": contract_response['response'][0]['id'],
            "name":contract_response['response'][0]['name'],
            "type":contract_response['response'][0]['type'],
            "description" : contract_response['response'][0]['description'],
            "clause": contract_response['response'][0]['clause'],
            "contractClassifier" : contract_response['response'][0]['contractClassifier']                  
        }
        if contract_name:
            ac_data["name"] = contract_name
        if description:
            ac_data["description"] = description
        if contract_data:
            ac_data["contractClassifier"] = contract_data
        if clause:
            ac_data["clause"] = clause
       
        contract_response = self.put_contractAccess(json=[ac_data], timeout=DEFAULT_SUMMARY_TIMEOUT)
        taskStatus = self._task.wait_for_task_complete(contract_response, timeout=DEFAULT_SUMMARY_TIMEOUT)
        self.log.info(taskStatus)
        if (taskStatus['isError']):
            self.log.error("Updating contract failed:{0}".format(taskStatus['failureReason']))
            return {'status':False,'failureReason':"Updating contract failed:{0}".format(taskStatus['failureReason'])}
        else:
            self.log.info("###################################################################")
            self.log.info("#----SUCESSFULLY updated CONTRACT {}----#".format(contract_name))
            self.log.info("###################################################################")
            return {'status':True}

    def delete_contractAccessByName(self, contract_name, **kwargs):
        """ delete a single contract with the given instance uuid

        Args:
            contract_name(str): Access Contract name
            kwargs (dict): additional parameters to be passed

        Returns:
            dict: response of api call

        Raises:

            ApiClientException: when unexpected query parameters are passed.
        """
        check_type(contract_name,basestring)

        url = '/'+ DEFAULT_VERSION + CONTRACT_URL_PATH2
        contract_response = self.get_contractAccessSummary()
        delete_list = [ac['id'] for i,ac in enumerate((contract_response['response'][0]['acaContractSummary'])) if ac['name'] == contract_name]
        if len(delete_list) == 0:
            self.log.error("No contract name exist to delete it")
            return {"status" : False}
        else:
            self.log.info("Contract exist for deletion") 
            ac_data = {
                "deleteList": delete_list,   
            }
        
        delete_response = self.post_contractAccess(url=url,json=ac_data)
        self.log.debug(delete_response)
        taskStatus = self._task.wait_for_task_complete(delete_response)
        self.log.info(taskStatus)
        if (taskStatus['isError']):
            self.log.error("Deleting access contract failed:{0}".format(taskStatus['failureReason']))
            return {"status" : False, 'failureReason':'Deleting access contract {} failed:{}'.format(contract_name,taskStatus['failureReason'])}
        self.log.info("#----SUCCESSFULLY DELETED access contract {}----#".format(contract_name))
        return { "status" : True }

    def deploy(self,timeout=DEFAULT_TASK_COMPLETION_TIMEOUT):
        """
            Deploy the policy and sync with ISE
            Input: 
            Result:
                {status: True}                                           : When policy deploy is success..
                {status: False, 'failureReason':"<failure description>"} : When policy failed to be deployed with failure reason.
        """
        response = self.put_acaControllerServiceDeploy()
        taskStatus = self._task.wait_for_task_complete(response, timeout=timeout)
        self.log.info(taskStatus)
        if (taskStatus['isError']):
            self.log.error("Deploy access contracts failed:{0}".format(taskStatus['failureReason']))
            return {'status':False, "failureReason":"Deploy access contracts failed: {}".format(taskStatus['failureReason'])}
        self.log.info("######################################################################################################")
        self.log.info("#----SUCCESSFULLY DEPLOYED ACCESS CONTRACTS----#")
        self.log.info("######################################################################################################")
        return {'status':True, 'taskStatus': taskStatus}

    #==========================================================================================================
    #=========================================      Base APIs     =============================================
    #==========================================================================================================
    def get_contractAccess(self, **kwargs):
        """ GET contract Access details
        Args:
            kwargs (dict): additional parameters to be passed
        Returns:
            dict: response of api call
        Raises:
            ApiClientException: when unexpected query parameters are passed.
        """
        url = '/'+ DEFAULT_VERSION + CONTRACT_URL_PATH
        method = 'GET'
        response = self._session.api_switch_call(method=method,
                                                      resource_path=url,
                                                      **kwargs)
        self.log.info("Method {} \nURL {} \nData {}".format(method, url, kwargs))
        self.log.info("Response {}".format(response))
        return response

    def get_contractAccessSummary(self, **kwargs):
        """ GET contract access summary details

        Args:
            kwargs (dict): additional parameters to be passed

        Returns:
            dict: response of api call

        Raises:
            ApiClientException: when unexpected query parameters are passed.
        """
        url = '/'+ DEFAULT_VERSION + CONTRACT_URL_SUMMARY_PATH
        method = 'GET'
        response = self._session.api_switch_call(method=method,
                                                      resource_path=url,
                                                      **kwargs)
        self.log.info("Method {} \nURL {} \nData {}".format(method, url, kwargs))
        self.log.info("Response {}".format(response))
        return response

    def _get_contractAccessById(self, instance_uuid,**kwargs):
        """ GET contract access by Instace ID

        Args:
            instance_uuid(str): additional parameters to be passed

        Returns:
            dict: response of api call

        Raises:
            ApiClientException: when unexpected query parameters are passed.
        """
        check_type(instance_uuid,basestring)

        url = '/'+ DEFAULT_VERSION + CONTRACT_URL_PATH+'/'+instance_uuid
        method = 'GET'
        response = self._session.api_switch_call(method=method,
                                                      resource_path=url,
                                                      **kwargs)
        self.log.info("Method {} \nURL {} \nData {}".format(method, url, kwargs))
        self.log.info("Response {}".format(response))
        return response

    def get_contractAccessByName(self, contract_name):
        """ get_contractAccess by name
        Args:
            contract_name: Provide contract access name 
        Returns:
            dict: response of api call
        Raises:
            ApiClientException: when unexpected query parameters are passed.
        """
        check_type(contract_name,basestring)

        params = { "name" : contract_name }
        return self.get_contractAccess(params=params)

    def post_contractAccess(self,url =None,**kwargs):
        '''
            Function: Create request for contract access
            Description: POST request for creating access contract
            INPUT: kwargs
            OUTPUT: response
        '''
        if url == None:
            url = '/'+ DEFAULT_VERSION + CONTRACT_URL_PATH
        method = 'POST'
        response = self._session.api_switch_call(method=method,
                                                      resource_path=url,
                                                      **kwargs)
        self.log.info("Method {} \nURL {} \nData {}".format(method, url, kwargs))
        self.log.info("Response {}".format(response))
        return response

    def put_contractAccess(self, **kwargs):
        '''
            Function: UPDATE request for contract access
            Description: UPDATE request for updating params in access contract
            INPUT: kwargs
            OUTPUT: response
        '''
        url = '/'+ DEFAULT_VERSION + CONTRACT_URL_PATH
        method = 'PUT'
        response = self._session.api_switch_call(method=method,
                                                      resource_path=url,
                                                      **kwargs)
        self.log.info("Method {} \nURL {} \nData {}".format(method, url, kwargs))
        self.log.info("Response {}".format(response))
        return response

    def _delete_contractAccessById(self, instance_uuid, **kwargs):
        """ delete a single contract with the given instance uuid

        Args:
            instance_uuid(str): ID of contract access
            kwargs (dict): additional parameters to be passed

        Returns:
            dict: response of api call

        Raises:

            ApiClientException: when unexpected query parameters are passed.
        """
        check_type(instance_uuid,basestring)

        url = '/'+ DEFAULT_VERSION + CONTRACT_URL_PATH+'/'+instance_uuid
        method = 'DELETE'
        response = self._session.api_switch_call(method=method,
                                                      resource_path=url,
                                                      **kwargs)
        self.log.info("Method {} \nURL {} \nData {}".format(method, url, kwargs))
        self.log.info("Response {}".format(response))
        return response
       
    def put_acaControllerServiceDeploy(self, **kwargs):
        '''
            Function: put_acaControllerServiceDeploy
            Description: Update request for Deploy now action
            INPUT: kwargs
            OUTPUT: Returns response

        '''
        url = ACACONTROLLERPATH + "/deploy"
        method = 'PUT'
        response = self._session.api_switch_call(method=method,
                                                      resource_path=url,
                                                      **kwargs)
        self.log.info("Method {} \nURL {} \nData {}".format(method, url, kwargs))
        self.log.info("Response {}".format(response))
        return response 
