"""
Cisco DNA Center Devices API wrapper.
Copyright (c) 2022-2024 Cisco Systems.
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
logger = logging.getLogger("SecurityGroupsPolicy")

DEFAULT_TIMEOUT=60
DEFAULT_TASK_COMPLETION_TIMEOUT=120
DEFAULT_SUMMARY_TIMEOUT=240

DEFAULT_VERSION = "v2"
POLICY_PATH = "/data/customer-facing-service/policy/access"
POLICY_SUMMARY_PATH = "/data/customer-facing-service/summary/policy/access"
SCALABLE_GROUP_SUMMARY_PATH = "/data/customer-facing-service/summary/scalablegroup/access"
ACACONTROLLERPATH = "/v1/aca-controller-service"

class SGTPolicy(object):
    """
    Cisco DNA Center Security Group Based Policy API (version: 2.3.4).
    Wraps the DNA Center Devices
    API and exposes the API as native Python
    methods that return native Python objects.
    """

    def __init__(self, session):
        """
        Initialize a new Devices
        object with the provided RestSession.
        Args:
            session(RestSession): The RESTful session object to be used for
                                  API calls to the DNA Center service.
        Raises:
            TypeError: If the parameter types are incorrect.
        """
        check_type(session._session, DnacClientManager)

        super(SGTPolicy, self).__init__()
        self._session = session._session
        self._task = session.task
        self._contract = session.accesscontracts
        self._securitygroup = session.securitygroups
        self.log = logger

    def createSecurityGroupPolicy(self, policy_name, producer_name, consumer_name, contract_name):
        """
        Create policy for group based access control

        Args:
            policy_name(str) : Policy name
            producer_name(str): Policy source name
            consumer_name(str): Policy Destination name
            contract_name(str): contract name to be associated to policy
        Returns:
            dict: response of api call
        Raises:
            ApiClientException: when unexpected query parameters are passed.        
        """
        check_type(policy_name,basestring)
        check_type(producer_name,basestring)
        check_type(consumer_name,basestring)
        check_type(contract_name,basestring)
        
        self.log.info("Start to create policy from {} to {} with contract {}".format(producer_name, consumer_name, contract_name))
        self.log.info("get contract info")
        contract_response = self._contract.get_contractAccessByName(contract_name)
        for response in contract_response["response"]:
            if response["name"] == contract_name:
                contract_id = str(response["id"])

        sg_response = self._securitygroup.get_securityGroup()
        for SG in sg_response["response"]:
            if SG["name"] == producer_name:
                producer_id = str(SG["id"])
            if SG["name"] == consumer_name:
                consumer_id = str(SG["id"])

        access_policy_response = self.get_policyaccess()
        policy_scope_id = access_policy_response["response"][0]["policyScope"]

        self.log.info("Inside create new policy the Idref of the contract is: {0}".format(contract_id))

        sgtpolicy_data = [{
            "isEnabled": "true",
            "contract": {
                "idRef": contract_id
            },
            "producer": {
                "scalableGroup": [{
                    "idRef": producer_id
                    }]
            },
            "consumer": {
                "scalableGroup": [{
                    "idRef": consumer_id
                }]
            },
            "policyScope": policy_scope_id,
            "priority": 65535,
            "name": policy_name
            }]
        policy_response = self.post_policyaccess(json=sgtpolicy_data)
        taskStatus = self._task.wait_for_task_complete(policy_response, timeout=DEFAULT_TASK_COMPLETION_TIMEOUT)
        self.log.info(taskStatus)
        if (taskStatus['isError']):
            self.log.error("Creating policy failed:{0}".format(taskStatus['failureReason']))
            return {'status':False, "failureReason":"Creating Policy {} failed:{}".format(taskStatus['failureReason']),'TaskStatus': taskStatus}
        self.log.info("######################################################################################################")
        self.log.info("#----SUCCESSFULLY CREATED TRUSTSEC POLICY from {} to {} with contract {}----#".format(producer_name, consumer_name, contract_name))
        self.log.info("######################################################################################################")
        return {'status':True,'TaskStatus': taskStatus}

    def update_policy(self, src_sg_name, dst_sg_name, mode=None, new_contract_name=None):
        """
        Update policy details for Group Based Access Control

        Args:
            src_sg_name(str): Source security group name
            dst_sg_name(str): Destination security group name
            mode(str): Mode of policy
            new_contract_name(str): contract name to be updated
        Raises:
            TypeError: If the parameter types are incorrect.        
        """
        check_type(src_sg_name,basestring)
        check_type(dst_sg_name,basestring)
        check_type(mode,basestring)
        check_type(new_contract_name,basestring)

        self.log.info("Start to update policy from {} to {} in DNAC".format(src_sg_name, dst_sg_name))
        policy_id = ""
        contract_id = ""

        sg_response = self._securitygroup.get_securityGroup()
        for sg in sg_response["response"]:
            if(sg["name"] == src_sg_name):
                src_sg_id = str(sg["id"])
                self.log.info(src_sg_id)
            if(sg["name"] == dst_sg_name):
                dst_sg_id = str(sg["id"])
                self.log.info(dst_sg_id)
        policy_response = self.get_policyaccess()
        for aca in policy_response["response"]:
            if dst_sg_id in aca["consumer"]["scalableGroup"][0]["idRef"] and src_sg_id in aca["producer"]["scalableGroup"][0]["idRef"]:
                policy_id = aca["id"]
                policy_scope = aca['policyScope']
                policy_name = aca['name']
                policy_status = aca['policyStatus']
                contract_id = aca['contract']['idRef']
                policy_priority = aca['priority']
                self.log.info(policy_id)
                break
        if policy_id == '':
            self.log.error('Policy isnot found')
            return {"status": False}

        if mode is not None:
            policy_status = mode

        if new_contract_name is not None:
            contract_response = self._contract.get_contractAccess()
            for contract in contract_response["response"]:
                if contract["name"] == new_contract_name:
                    contract_id = str(contract["id"])
                    break
            if contract_id == '':
                self.log.error('The contract is not found')
                return {"status": False}
        sgtpolicy_data = [{
                "id": policy_id,
                "policyScope": policy_scope,
                "priority": policy_priority,
                "name": policy_name,
                "policyStatus": policy_status,
                "contract": {"idRef": contract_id},
                "producer": {"scalableGroup": [{"idRef":src_sg_id}]},
                "consumer": {"scalableGroup": [{"idRef":dst_sg_id}]}
                }]

        policy_response = self.put_policyaccess(json=sgtpolicy_data)
        taskStatus = self._task.wait_for_task_complete(policy_response, timeout=DEFAULT_TASK_COMPLETION_TIMEOUT)
        self.log.info(taskStatus)
        if (taskStatus['isError']):
            self.log.error("Updating policy failed:{0}".format(taskStatus['failureReason']))
            return {'status':False,
                    'failureReason':'Failed in updating Policy with reason: {}'.format(taskStatus['failureReason']),'TaskStatus': taskStatus}
        self.log.info("###############################################################################################")
        self.log.info("#----SUCCESSFULLY UPDATED TRUSTSEC POLICY for {} to {}----#".format(src_sg_name, dst_sg_name))
        self.log.info("###############################################################################################")
        return {"status": True,'TaskStatus': taskStatus}
       
    def delete_policy(self, src_sg_name, dst_sg_name):
        """
        Delete Policy for Group Based Access Control

        Args:
            src_sg_name(str): Source security group name
            dst_sg_name(str): Destination security group name
        Raises:
            TypeError: If the parameter types are incorrect.        
        """
        check_type(src_sg_name,basestring)
        check_type(dst_sg_name,basestring)

        self.log.info("Start to delete policy from {} to {}".format(src_sg_name, dst_sg_name))
        delete_id = ""
        src_sg_id = ""
        dst_sg_id = ""
        sg_response = self._securitygroup.get_securityGroup()
        for sg in sg_response["response"]:
            if(sg["name"] == src_sg_name):
                src_sg_id = str(sg["id"])
                self.log.info("Source name ref id {}".format(src_sg_id))
            if(sg["name"] == dst_sg_name):
                dst_sg_id = str(sg["id"])
                self.log.info("Destination name ref id {}".format(dst_sg_id))

        policy_response = self.get_policyaccess()
        if src_sg_id == '' or dst_sg_id == '' :
            self.log.error("The source or destination security group is not found")
        for aca in policy_response["response"]:
            if dst_sg_id in aca["consumer"]["scalableGroup"][0]["idRef"] and src_sg_id in aca["producer"]["scalableGroup"][0]["idRef"]:
                delete_id = aca["id"]
                self.log.info("Delete ref id {}".format(delete_id))

        if delete_id == '':
            self.log.error("The policy is not found")
            return {'status':False}

        delete_response = self.delete_policyaccessById(delete_id)
        self.log.info(delete_response)
        taskStatus = self._task.wait_for_task_complete(delete_response, timeout=DEFAULT_TASK_COMPLETION_TIMEOUT)
        self.log.info(taskStatus)
        if (taskStatus['isError']):
            self.log.error("Deleting policy failed:{0}".format(taskStatus['failureReason']))
            return {'status':False, "failureReason":"Deleting Policy {} failed:{}".format(taskStatus['failureReason']),'TaskStatus': taskStatus}
        self.log.info("###############################################################################################")
        self.log.info("#----SUCCESSFULLY DELETED TRUSTSEC POLICY from {} to {}----#".format(src_sg_name, dst_sg_name))
        self.log.info("###############################################################################################")
        return {'status':True,'TaskStatus': taskStatus}

    def getPolicyCount(self):
        """
        Get Total policy count for Group Based Access Control

        Returns:
            count of total number of policy present in DNAC.
        Raises:
            ApiClientException: when parameters are passed.        
        """
        self.log.info("Start to count policies in DNAC")
        params = {'gbpSummary': 'true'}
        policy_response = self.get_policyaccess_summary(params=params, timeout=DEFAULT_SUMMARY_TIMEOUT)
        policy_response_summary = policy_response["response"][0]
        count = len(policy_response_summary["acaGBPSummary"])
        self.log.info("Total Policy count in DNAC {}".format(count))
        return {'status':True,'Total Policy Count':count}

    def getAllPolicyName(self):
        """
        GET all Policy name list

        Returns:
            Total Policy name list present in DNAC.
        Raises:
            ApiClientException: when parameters are passed.
        """
        self.log.info("Start to get all policies in DNAC")
        policylist = []
        params = {'gbpSummary': 'true'}
        policy_response = self.get_policyaccess_summary(params=params)
        policy_response_summary = policy_response["response"][0]

        for policy in policy_response_summary["acaGBPSummary"]:
            producer_name = policy["producerName"]
            consumer_name = policy["consumerName"]
            contract_name = policy["contractName"]
            name= producer_name + "-" + consumer_name
            policy_dict = {"name":name, "contract":contract_name}
            policylist.append(policy_dict)
        return {"status": True,'PolicyNameList': policylist}

    def is_policy_exist_in_dnac(self, policy_list, expect=True):
        """
        Find policy list exist in DNAC

        Args:
            policy_list(str): Policy nmae list
            expect(bool): True or False
        Raises:
            TypeError: If the parameter types are incorrect.
        """
        check_type(policy_list,list)
        check_type(expect,bool)

        self.log.info("Start to check policy list in DNAC")
        policylist_aca = self.get_all_policy()

        self.log.info("Policy list to check: {}".format(policy_list))
        self.log.info("Policy list in ACA DNAC: {}".format(policylist_aca))
        missing_list = []
        exist_list = []
        for policy in policy_list:
            if policy in policylist_aca:
                exist_list.append(policy)
                continue
            else:
                missing_list.append(policy)
        if expect:
            if len(missing_list)==0:
                self.log.info("####################################################")
                self.log.info("#----Policies exists in DNAC as expected {} ----#".format(policy_list))
                self.log.info("####################################################")
                return {'status':True, 'PolicyList': policy_list}
            else:
                self.log.error("Some Policies don't exist in ACA DNAC"
                                "or have different information: {}".format(missing_list))
                return {'status':False,'MissingList': missing_list}
        else:
            if len(missing_list)==len(policy_list):
                self.log.info("#####################################################")
                self.log.info("#----Policy list don't exists in DNAC as expected {}----#".format(policy_list))
                self.log.info("#####################################################")
                return {'status':True,'PolicyList': policy_list}
            else:
                self.log.error("Some Contracts still exist in DNAC "
                                "or have different information".format(exist_list))
                return {'status':False,'ExistList': exist_list}
       
    ######################################################################################################
    #######################################  Base APIs  ##################################################
    ######################################################################################################

    def get_policyAccess(self,**kwargs):
        """ 
        GET Policy access details for Group Based Access Control

        Args:
            kwargs (dict): additional parameters to be passed
        Returns:
            dict: response of api call
        Raises:
            ApiClientException: when unexpected query parameters are passed.
        """
        url = '/'+ DEFAULT_VERSION + POLICY_PATH
        method = 'GET'
        response = self._session.api_switch_call(method=method,
                                                 resource_path=url,
                                                 **kwargs)
        self.log.info("Method {} \nURL {} \nData {}".format(method, url, kwargs))
        self.log.info("Response {}".format(response))
        return response

    def get_policyAccessSummary(self,**kwargs):
        """ 
        GET Policy access summary details for Group Based Access Control

        Args:
            kwargs (dict): additional parameters to be passed
        Returns:
            dict: response of api call
        Raises:
            ApiClientException: when unexpected query parameters are passed.
        """
        url = '/'+ DEFAULT_VERSION + POLICY_SUMMARY_PATH
        method = 'GET'
        response = self._session.api_switch_call(method=method,
                                                 resource_path=url,
                                                 **kwargs)
        self.log.info("Method {} \nURL {} \nData {}".format(method, url, kwargs))
        self.log.info("Response {}".format(response))
        return response

    def post_policyAccess(self, **kwargs):
        '''
        POST request for Policy access

        Args:
            kwargs (dict): additional parameters to be passed.
        Returns:
            dict: response of api call.
        Raises:
            ApiClientException: when unexpected query parameters are passed.           
        '''
        url = '/'+ DEFAULT_VERSION + POLICY_PATH
        method = 'POST'
        response = self._session.api_switch_call(method=method,
                                                 resource_path=url,
                                                 **kwargs)
        self.log.info("Method {} \nURL {} \nData {}".format(method, url, kwargs))
        self.log.info("Response {}".format(response))
        return response

    def put_policyAccess(self,**kwargs):
        """ 
        UPDATE request for Policy access

        Args:
            kwargs (dict): additional parameters to be passed.
        Returns:
            dict: response of api call.
        Raises:
            ApiClientException: when unexpected query parameters are passed.
        """
        url = '/'+ DEFAULT_VERSION + POLICY_PATH
        method = 'PUT'
        response = self._session.api_switch_call(method=method,
                                                 resource_path=url,
                                                 **kwargs)
        self.log.info("Method {} \nURL {} \nData {}".format(method, url, kwargs))
        self.log.info("Response {}".format(response))
        return response
        
    def delete_policyAccessById(self,ref_id,**kwargs):
        """ 
        DELETE request for Policy access

        Args:
            kwargs (dict): additional parameters to be passed
        Returns:
            dict: response of api call
        Raises:
            ApiClientException: when unexpected query parameters are passed.
        """
        url = '/'+ DEFAULT_VERSION + POLICY_PATH+'/'+ref_id
        method = 'DELETE'
        response = self._session.api_switch_call(method=method,
                                                 resource_path=url,
                                                 **kwargs)
        self.log.info("Method {} \nURL {} \nData {}".format(method, url, kwargs))
        self.log.info("Response {}".format(response))
        return response

    def put_acaControllerServiceDeploy(self, **kwargs):
        '''
        UPDATE request for acaController service deploy

        Args:
            kwargs (dict): additional parameters to be passed
        Returns:
            dict: response of api call
        Raises:
            ApiClientException: when unexpected query parameters are passed.
        '''
        url = ACACONTROLLERPATH + "/deploy"
        method = 'PUT'
        response = self._session.api_switch_call(method=method,
                                                 resource_path=url,
                                                 **kwargs)
        self.log.info("Method {} \nURL {} \nData {}".format(method, url, kwargs))
        self.log.info("Response {}".format(response))
        return response


