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

DEFAULT_VERSION = "v2"
CONTRACT_URL_PATH = "/data/customer-facing-service/contract/access"
CONTRACT_URL_PATH2 = "/data/cfs-intent/contract/access"
CONTRACT_URL_SUMMARY_PATH = "/data/customer-facing-service/summary/contract/access"
ACACONTROLLERPATH = "/v1/aca-controller-service"
DEFAULT_HEADERS = {'Content-Type': 'application/json'}

class AccessContracts(object):
    """Cisco DNA Center AccessContracts API (version: 2.3.3.0).
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


    def createNewContract(self,condition):
        """
        Create access contract
        Args:
            condition(dict): Parameters for creating contract
        Raises:
            TypeError: If the parameter types are incorrect.
        """
        check_type(condition,dict)

        self.log.info("Start to create new contract {} in DNAC".format(condition[0]['name']))
        try:
            contract_response = self.services.post_contractAccess(json=condition, timeout=60)
            taskStatus = self._task.wait_for_task_complete(contract_response, timeout=240)
            self.log.info(taskStatus)
            if (taskStatus['isError']):
                self.log.error("creating new contract failed:{0}".format(taskStatus['failureReason']))
                raise Exception("creating new contract failed:{0}".format(taskStatus['failureReason']))
            self.log.info("##################################################################################")
            self.log.info("#----SUCCESSFULLY CREATED CONTRACT {}----#".format(condition[0]['name']))
            self.log.info("##################################################################################")
        except Exception as e:
            self.log.error("#################################################################################")
            self.log.error("#!!!FAILED TO CREATE NEW CONTRACT IN DNAC. ERROR: {}----#".format(e))
            self.log.error("#################################################################################")
            raise Exception(e)


    def getAllContractName(self):
        """
        Get all contract Name list
        """
        self.log.info("Start to get all contract names in DNAC")
        try:
            contractlist = []
            params = {'offset': 0, 'limit': 5000, 'contractSummary': 'true'}
            contract_response = self.get_contractAccessSummary(params=params,timeout=240)
            contract_response_sum = contract_response["response"][0]

            for response in contract_response_sum["acaContractSummary"]:
                name = response["name"]
                contractlist.append(name)
            return contractlist
        except Exception as e:
            self.log.error("#################################################################################")
            self.log.error("#!!!FAILED TO GET ALL CONTRACT NAMES IN DNAC. ERROR: {}----#".format(e))
            self.log.error("#################################################################################")
            raise Exception(e)

    def getContractCount(self):
        """     
        GET total contract count
        """
        self.log.info("Start to count contract in DNAC")
        try:
            params = {'offset': 0, 'limit': 5000, 'contractSummary': 'true'}
            contract_response = self.get_contractAccessSummary(params=params,timeout=240)
            contract_response_sum = contract_response["response"][0]
            count = contract_response_sum["totalContractCount"]
            return count
        except Exception as e:
            self.log.error("#################################################################################")
            self.log.error("#!!!FAILED TO GET CONTRACT COUNT IN DNAC. ERROR: {}----#".format(e))
            self.log.error("#################################################################################")
            raise Exception(e)

    def verifyContractExistInDnac(self, contract_list, expect=True):
        """
        Function to Verify Contract exist in DNAC
        Args:
          contract_list(list): Contract name or list of contract names
          expect(bool): True or False.Default is True.
        
        """
        check_type(contract_list,list)
        check_type(expect,bool)

        self.log.info("Start to check contract list in DNAC")
        try:
            # Check contract name only for now
            # Todo check contract aces too
            missing_list= []
            exist_list = []
            contractlist_aca = self.get_all_contract_name()
            for acl in contract_list:
                if acl in contractlist_aca:
                    exist_list.append(acl)
                    continue
                else:
                    missing_list.append(acl)
            self.log.info("Contracts to check {}".format(contract_list))
            self.log.info("All conotracts in DNAC {}".format(contractlist_aca))

            if expect:
                if len(missing_list)==0:
                    self.log.info("#####################################################")
                    self.log.info("#----Contracts exists in DNAC {}----#".format(contract_list))
                    self.log.info("#####################################################")
                else:
                    raise Exception("Some Contracts dont' exist in DNAC "
                                    "or have different information".format(missing_list))
            else:
                if len(missing_list)==len(contract_list):
                    self.log.info("#####################################################")
                    self.log.info("#----Contract list don't exists in DNAC {}----#".format(contract_list))
                    self.log.info("#####################################################")
                else:
                    raise Exception("Some Contracts still exist in DNAC "
                                    "or have different information".format(exist_list))
        except Exception as e:
            self.log.error("#################################################################################")
            self.log.error("#!!!FAILED TO CHECK CONTRACT LIST IN DNAC. ERROR: {}----#".format(e))
            self.log.error("#################################################################################")
            raise Exception(e)

    def updateAccessContract(self, contract_name, condition):
        """
        Update  access contract by name
        Args:
        contract_name(str): Provide the contract name
        condition(dict): Parameters to be updated      
        Raises:
            TypeError: If the parameter types are incorrect.
        """
        check_type(contract_name,basestring)
        check_type(condition,dict)

        self.log.info("Start to update contract {}".format(contract_name))
        try:
            self.log.info("Update contract")
            contract_response = self.get_contractAccess(timeout=60)
            for response in contract_response["response"]:
                if response["name"] == contract_name:
                    contract_id = str(response["id"])
                    condition[0]["id"] = contract_id
                    break
            else:
                raise Exception("The contract {} isnot found".format(contract_name))
            contract_response = self.put_contractAccess(json=condition, timeout=240)
            taskStatus = self._task.wait_for_task_complete(contract_response, timeout=240)
            self.log.info(taskStatus)
            if (taskStatus['isError']):
                self.log.error("Updating contract failed:{0}".format(taskStatus['failureReason']))
                raise Exception("Updating contract failed:{0}".format(taskStatus['failureReason']))
            self.log.info("###################################################################")
            self.log.info("#----SUCCESSFULLY updated CONTRACT {}----#".format(contract_name))
            self.log.info("###################################################################")
        except Exception as e:
            self.log.error("#################################################################################")
            self.log.error("#!!!FAILED TO UPDATE CONTRACT {} IN DNAC. ERROR: {}----#".format(contract_name,e))
            self.log.error("#################################################################################")
            raise Exception(e)

    def deleteAccessContract(self, contract_name, expect=True):
        """
        Delete access contract by name
        Args:
        contract_name(str): Provide the contract name
        expect(bool):True or False        
        Raises:
            TypeError: If the parameter types are incorrect.
        """
        check_type(contract_name,basestring)
        check_type(expect,bool)

        self.log.info("Start to delete contract {} in DNAC".format(contract_name))
        try:
            contract_response = self.get_contractAccess(timeout=60)
            for response in contract_response["response"]:
                if response["name"] == contract_name:
                    contract_id = str(response["id"])
                    condition = {"deleteList":[contract_id]}
                    break
            else:
                raise Exception("The contract {} isnot found".format(contract_name))
            for contractid in condition["deleteList"]:
                contract_response = self.services.delete_contractAccess(contractid, timeout=60)
                if expect:
                    taskStatus = self._task.wait_for_task_complete(contract_response, timeout=240)
                    self.log.info(taskStatus)
                    if (taskStatus['isError']):
                        self.log.error("Deleting contract failed:{0}".format(taskStatus['failureReason']))
                        raise Exception("Deleting contract failed:{0}".format(taskStatus['failureReason']))
                    self.log.info("###################################################################")
                    self.log.info("#----SUCCESSFULLY deleted CONTRACT {}----#".format(contract_name))
                    self.log.info("###################################################################")
                else:
                    taskStatus = self._task.wait_for_task_complete(contract_response, timeout=240)
                    self.log.info(taskStatus)
                    if not (taskStatus['isError']):
                        self.log.error("Deleting contract successfully although expected failure")
                        raise Exception("Deleting contract successfully although expected failure")
                    self.log.info("#########################################################################")
                    self.log.info("#----COULDNOT DELETE CONTRACT {} AS EXPECTED----#".format(contract_name))
                    self.log.info("#########################################################################")
        except Exception as e:
            self.log.error("#################################################################################")
            self.log.error("#!!!FAILED TO DELETE CONTRACT {} IN DNAC. ERROR: {}----#".format(contract_name, e))
            self.log.error("#################################################################################")
            raise Exception(e)
    #=========================================Base APIs==================
    #====================================================================
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

    def get_contractAccessById(self, instance_uuid):
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

        url = '/'+ DEFAULT_VERSION + CONTRACT_URL_PATH+'/'+contract_name
        method = 'GET'
        response = self._session.api_switch_call(method=method,
                                                      resource_path=url,
                                                      **kwargs)
        self.log.info("Method {} \nURL {} \nData {}".format(method, url, kwargs))
        self.log.info("Response {}".format(response))
        return response

    def delete_allContractAccess(self, **kwargs):
        """ Delete All non-reserved Contracts.

        If you pass an array of names to be excluded from deletion in the kwargs called 'exclusions',
        these will not be deleted either

        Args:
            kwargs (dict): additional parameters to be passed

        Returns:
            dict: response of api call

        Raises:
            ApiClientException: when unexpected query parameters are passed.
        """
        # Reserved Contract Entities
        exclusions = ['Deny IP', 'Deny_IP_Log', 'Permit IP', 'Permit_IP_Log']
        # If any names are specified to exclude, then don't delete them
        if 'exclusions' in kwargs.keys() and len(kwargs['exclusions']) > 0:
            for exclusions_name in kwargs['exclusions']:
                exclusions.append(exclusions_name)

        contracts = self.get_contractAccess()
        for contract in contracts:
            try:
                if contract['name'] not in exclusions:
                    self.delete_contractAccess(contract['id'])
            except:
                print('Could not delete the given contract')

    def delete_contractAccess(self, instance_uuid, **kwargs):
        """ Delete a single contract with the given instance uuid

        Args:
            kwargs (dict): additional parameters to be passed

        Returns:
            dict: response of api call

        Raises:

            ApiClientException: when unexpected query parameters are passed.
        """

        version = kwargs.pop("version", self.VERSION)
        resource_path = "/" + version + self.PATH + "/" + instance_uuid
        headers = self.HEADERS

        kwargs['headers'] = headers

        params = []

        if "params" in kwargs:
            for key in kwargs["params"]:
                if key not in params:
                    raise ApiClientException(
                        "Unrecognized parameter: '{}' for API endpoint: '{}'"
                        .format(key, resource_path))

        method = 'DELETE'

        return self._session.call_api(method, resource_path, **kwargs)

    def post_contractAccess(self, **kwargs):
        """ POST request for access contract

        Args:
            kwargs (dict): additional parameters to be passed

        Returns:
            dict: response of api call

        Raises:
            ApiClientException: when unexpected query parameters are passed.
        """

        version = kwargs.pop("version", self.VERSION)
        resource_path = "/" + version + self.PATH + ""
        headers = self.HEADERS

        kwargs['headers'] = headers

        params = []

        if "params" in kwargs:
            for key in kwargs["params"]:
                if key not in params:
                    raise ApiClientException(
                        "Unrecognized parameter: '{}' for API endpoint: '{}'"
                        .format(key, resource_path))

        method = 'POST'

        return self._session.call_api(method, resource_path, **kwargs)

    def put_contractAccess(self, **kwargs):
        """ Update contract access

        Args:
            kwargs (dict): additional parameters to be passed

        Returns:
            dict: response of api call

        Raises:

            ApiClientException: when unexpected query parameters are passed.
        """

        version = kwargs.pop("version", self.VERSION)
        resource_path = "/" + version + self.PATH + ""
        headers = self.HEADERS

        kwargs['headers'] = headers

        params = []

        if "params" in kwargs:
            for key in kwargs["params"]:
                if key not in params:
                    raise ApiClientException(
                        "Unrecognized parameter: '{}' for API endpoint: '{}'"
                        .format(key, resource_path))

        method = 'PUT'

        return self._session.call_api(method, resource_path, **kwargs)
        
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

