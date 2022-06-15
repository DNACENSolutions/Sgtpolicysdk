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
import uuid
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
POLICY_COUNT_PATH = "/data/customer-facing-service/count/policy/access"
ACACONTROLLERPATH = "/v1/aca-controller-service"

class SGTPolicy(object):
    """Cisco DNA Center Security Group Based Policy API (version: 2.3.3.0).
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
        super(SGTPolicy, self).__init__()
        self._session = session._session
        self._task = session.task
        self._contract = session.accesscontracts
        self._securitygroup = session.securitygroups
        self.log = logger

    def createSecurityGroupPolicyFromSourceToDestinations(self, srcSGName, dstSGNames, accessContract, isEnabled=True, priority=65535):
        '''
            Description: Create a SG Policy from a Single source to single or Multiple Destination
            Inputs:  
                srcSGName (String) : Name of thr source security group.
                dstSGNames (list)  : List of names/name of destination security group.
                accessContract (String): Accesscontract name to be used for policy.
                isEnabled (boolean) : Policy status (default enabled)
                priority (int) :    Policy Priority (default Value 65535)
            Return:
                {status: True}  : When polic is successfully created.
                {status: False, 'failureReason':"<failure description>"} When policy failed to be created with failure reason.
        '''
        check_type(srcSGName,basestring)
        check_type(dstSGNames,list)
        for dstSGName in dstSGNames:
            status = self.createSecurityGroupPolicy(srcSGName,dstSGName,accessContract,isEnabled=isEnabled,priority=priority)
            if not status['status']:
                self.log.error("Failed to create policy")
                return status
        return {'status': True} 

    def createSecurityGroupPolicyFromDestinationToSources(self, srcSGNames, dstSGName, accessContract, isEnabled=True, priority=65535):
        '''
            Description: Create a SG Policy from a Single or Multiple source to single Destination Security Group
            Inputs:  
                srcSGNames (list) :  : List o security name/names of the source security group(s).
                dstSGNames (String)  : Names of destination security group.
                accessContract (String): Accesscontract name to be used for policy.
                isEnabled (boolean) : Policy status (default enabled)
                priority (int) :    Policy Priority (default Value 65535)
            Return:
                {status: True}  : When polic is successfully created.
                {status: False, 'failureReason':"<failure description>"} When policy failed to be created with failure reason.
        '''
        check_type(dstSGName,basestring)
        check_type(srcSGNames,list)
        for srcSGName in srcSGNames:
            status = self.createSecurityGroupPolicy(srcSGName,dstSGName,accessContract,isEnabled=isEnabled,priority=priority)
            if not status['status']:
                self.log.error("Failed to create policy")
                return status
        return {'status': True} 

    def createSecurityGroupPolicy(self, srcSGName, dstSGName, accessContract, isEnabled=True, priority=65535):
        '''
            Description: Create a SG Policy from a Single/Multiple source to single/multiple destination security groups
            Inputs:  
                srcSGName (String)      : Source security group(s).
                dstSGName (String)      : Destination security group(s).
                accessContract (String) : Accesscontract name to be used for policy.
                isEnabled (boolean)     : Policy status (default enabled)
                priority (int)          :    Policy Priority (default Value 65535)
            Return:
                {status: True}                                           : When polic is successfully created.
                {status: False, 'failureReason':"<failure description>"} : When policy failed to be created with failure reason.
        '''
        policy_name = str(uuid.uuid4())
        check_type(policy_name,basestring)
        check_type(srcSGName,basestring)
        check_type(dstSGName,basestring)
        check_type(accessContract,basestring)

        if not dstSGName:
            return {'status':False, "failureReason":"Provide Source Security Group/Groups"}
        if not dstSGName:
            return {'status':False, "failureReason":"Provide Destination Security Group/Groups"}
        if not accessContract:
            return {'status':False, "failureReason":"Provide valid access contract"}
        self.log.info("Start to create policy:{} from {} to {} with contract {}".format(policy_name, dstSGName, dstSGName, accessContract))
        srcSGIDRef=[]
        src_sg = self._securitygroup.getSecurityGroupIdByName(srcSGName)
        if src_sg['status']:
            srcSGIDRef.append({"idRef": src_sg['id']})
        else:
            self.log.error("Could not create policy {}, as Source Security Group:{} is not found".format(policy_name,srcSGName))
            return src_sg
        dstSGIDRef=[]
        dst_sg = self._securitygroup.getSecurityGroupIdByName(dstSGName)
        if dst_sg['status']:
            dstSGIDRef.append({"idRef": dst_sg['id']})
        else:
            self.log.error("Could not create policy {}, as Destination Security Group:{} is not found".format(policy_name,dstSGName))
            return dst_sg
        self.log.info("get contract info")
        contract_id=None
        contract_response = self._contract.get_contractAccessByName(accessContract)
        for response in contract_response["response"]:
            if response["name"] == accessContract:
                contract_id = str(response["id"])
        if contract_id:
            access_policy_response = self.get_policyaccess()
            policy_scope_id = access_policy_response["response"][0]["policyScope"]
            self.log.info("Inside create new policy the Idref of the contract is: {0}".format(contract_id))
            sgtpolicy_data = [{
                "isEnabled": isEnabled,
                "contract": {
                    "idRef": contract_id
                },
                "producer": {
                    "scalableGroup": srcSGIDRef
                },
                "consumer": {
                    "scalableGroup": dstSGIDRef
                },
                "policyScope": policy_scope_id,
                "priority": priority,
                "name": policy_name
                }]
            policy_response = self.post_policyaccess(json=sgtpolicy_data)
            taskStatus = self._task.wait_for_task_complete(policy_response, timeout=DEFAULT_TASK_COMPLETION_TIMEOUT)
            self.log.info(taskStatus)
            if (taskStatus['isError']):
                self.log.error("Creating policy failed:{0}".format(taskStatus['failureReason']))
                return {'status':False, "failureReason":"Creating Policy {} failed:{}".format(taskStatus['failureReason'])}
            self.log.info("######################################################################################################")
            self.log.info("#----SUCCESSFULLY CREATED TRUSTSEC POLICY from {} to {} with contract {}----#".format(srcSGName, dstSGName, accessContract))
            self.log.info("######################################################################################################")
            return {'status':True, 'taskStatus': taskStatus}
        else:
            self.log.error("Could not create policy {}, as access contract:{} is not found".format(policy_name,accessContract))
            return {'status':False, "failureReason": "Access contract: {} is not found".format(accessContract)}

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
            self.log.error("Deploy policy failed:{0}".format(taskStatus['failureReason']))
            return {'status':False, "failureReason":"Deploy policy failed: {}".format(taskStatus['failureReason'])}
        self.log.info("######################################################################################################")
        self.log.info("#----SUCCESSFULLY DEPLOYED TRUSTSEC POLICY----#")
        self.log.info("######################################################################################################")
        return {'status':True, 'taskStatus': taskStatus}

    def deleteSecurityGroupPolicy(self, srcSGName, dstSGName):
        """
        Delete deleteSecurityGroupPolicy
        Args:
            srcSGName(str): Source security group name
            dstSGName(str): Destination security group name
        Raise:
            TypeError: If the parameter types are incorrect.
        Return:
            {'stats': True, }         : If policy is found and deleted successfully
            {'status': False, 'failureReason': "<A reason explaing why policy deletion is failed.>"}  
        """
        check_type(srcSGName,basestring)
        check_type(dstSGName,basestring)
        if not srcSGName:
            return {'status':False, "failureReason":"Provide Valid Source Security Group"}
        if not dstSGName:
            return {'status':False, "failureReason":"Provide Valid Destination Security Group"}

        self.log.info("Delete policy from {} to {}".format(srcSGName, dstSGName))
        delete_id = ""
        src_sg_id = ""
        dst_sg_id = ""
        
        src_sg = self._securitygroup.getSecurityGroupIdByName(srcSGName)
        if src_sg['status']:
            src_sg_id= src_sg['id']
        else:
            self.log.error("Could not delete policy as Source Security Group:{} is not found".format(srcSGName))
            return src_sg

        dst_sg = self._securitygroup.getSecurityGroupIdByName(dstSGName)
        if dst_sg['status']:
            dst_sg_id= dst_sg['id']
        else:
            self.log.error("Could not delete policy as Destination Security Group:{} is not found".format(dstSGName))
            return dst_sg

        policy_response = self.get_policyaccess()
        if src_sg_id == '' or dst_sg_id == '' :
            self.log.error("The source or destination security group is not found")
            return {'status':False, 'failureReason': "The source or destination security group is not found"}

        for aca in policy_response["response"]:
            if dst_sg_id == aca["consumer"]["scalableGroup"][0]["idRef"] and src_sg_id == aca["producer"]["scalableGroup"][0]["idRef"]:
                delete_id = aca["id"]
                self.log.info("Policy id {} found n between source SG {} to destination SG {}".format(delete_id,srcSGName,dstSGName))

        if delete_id == '':
            self.log.error("No policy found in between source SG {} to destination SG {}".format(srcSGName,dstSGName))
            return {'status':False, 'failureReason': "No policy found in between source SG {} to destination SG {}".format(srcSGName,dstSGName)}

        delete_response = self.delete_policyaccessById(delete_id)
        self.log.info(delete_response)
        taskStatus = self._task.wait_for_task_complete(delete_response, timeout=DEFAULT_TASK_COMPLETION_TIMEOUT)
        self.log.info(taskStatus)
        if (taskStatus['isError']):
            self.log.error("Deleting policy failed:{0}".format(taskStatus['failureReason']))
            return {'status':False, "failureReason":"Deleting Policy {} failed:{}".format(taskStatus['failureReason'])}
        self.log.info("###############################################################################################")
        self.log.info("#----SUCCESSFULLY DELETED TRUSTSEC POLICY from {} to {}----#".format(src_sg_name, dst_sg_name))
        self.log.info("###############################################################################################")
        return {'status':True, 'taskStatus': taskStatus}

    def getPolicyCount(self):
        """
        Get Total policy count
        """
        self.log.info("Start to count policies in DNAC")
        policy_response = self.get_policyaccess_count()
        count = policy_response["response"]
        self.log.info("##Policies count on DNAC {}".format(count))
        return {'status': True, 'count': count}

    def getPolicyFromSGToDG(self, srcSGName, dstSGName):
        """
        Returns a policy detail from a source SG to destination SG
        Args:
            srcSGName(str): Source security group name
            dstSGName(str): Destination security group name
        Raises:
            TypeError: If the parameter types are incorrect.  
        Retrun:
            {'status':True, 'response': response}
            {'status':False, 'failureReason':"<Failure reason>"}
        """
        check_type(srcSGName,basestring)
        check_type(dstSGName,basestring)
        if not srcSGName:
            return {'status':False, "failureReason":"Provide Valid Source Security Group"}
        if not dstSGName:
            return {'status':False, "failureReason":"Provide Valid Destination Security Group"}

        self.log.info("Delete policy from {} to {}".format(srcSGName, dstSGName))
        policy_data = None
        src_sg_id = ""
        dst_sg_id = ""
        
        src_sg = self._securitygroup.getSecurityGroupIdByName(srcSGName)
        if src_sg['status']:
            src_sg_id= src_sg['id']
        else:
            self.log.error("Could not get policy details as source security group:{} is not found".format(srcSGName))
            return src_sg

        dst_sg = self._securitygroup.getSecurityGroupIdByName(dstSGName)
        if dst_sg['status']:
            dst_sg_id= dst_sg['id']
        else:
            self.log.error("Could not get policy detail as destination security group:{} is not found".format(dstSGName))
            return dst_sg

        policy_response = self.get_policyaccess()
        if src_sg_id == '' or dst_sg_id == '' :
            self.log.error("The source or destination security group is not found")
            return {'status':False, 'failureReason': "The source or destination security group is not found"}

        for aca in policy_response["response"]:
            if dst_sg_id == aca["consumer"]["scalableGroup"][0]["idRef"] and src_sg_id == aca["producer"]["scalableGroup"][0]["idRef"]:
                policy_data = aca
                self.log.info("Policy id {} found in between source SG {} to destination SG {}".format(aca['id'],srcSGName,dstSGName))

        if not policy_data:
            self.log.error("No policy found in between source SG {} to destination SG {}".format(srcSGName,dstSGName))
            return {'status':False, 'failureReason': "No policy found in between source SG {} to destination SG {}".format(srcSGName,dstSGName)}
        return {'status':True, 'response':policy_data}

    def updatePolicyStatusContract(self, src_sg_name, dst_sg_name, mode=None, new_contract_name=None):
        """
        Update policy details
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
        src_sg_id = ""
        dst_sg_id = ""
        
        src_sg = self._securitygroup.getSecurityGroupIdByName(srcSGName)
        if src_sg['status']:
            src_sg_id= src_sg['id']
        else:
            self.log.error("Could not get policy details as source security group:{} is not found".format(srcSGName))
            return src_sg

        dst_sg = self._securitygroup.getSecurityGroupIdByName(dstSGName)
        if dst_sg['status']:
            dst_sg_id= dst_sg['id']
        else:
            self.log.error("Could not get policy detail as destination security group:{} is not found".format(dstSGName))
            return dst_sg
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
            return {"status": False, 'failureReason': "No Policy found with source SG:{} and destination SG:{}".format(src_sg_name,dst_sg_name)}

        if mode is not None:
            policy_status = mode

        if new_contract_name is not None:
            contract_response = self._contract.get_contractAccess()
            for contract in contract_response["response"]:
                if contract["name"] == new_contract_name:
                    contract_id = str(contract["id"])
                    break
            if contract_id == '':
                self.log.error('The new contract {} is not found'.format(new_contract_name))
                return {"status": False,'failureReason': 'The new contract {} is not found'.format(new_contract_name)}
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
                    'failureReason':'Failed in updating Policy with reason: {}'.format(taskStatus['failureReason'])}
        self.log.info("###############################################################################################")
        self.log.info("#----SUCCESSFULLY UPDATED TRUSTSEC POLICY for {} to {}----#".format(src_sg_name, dst_sg_name))
        self.log.info("###############################################################################################")
        return {"status": True}

    def get_policyaccess(self,**kwargs):
        """ GET Policy access details
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

    def getAllPolicyNameContractList(self):
        """
        GET all Policy name list
        Return :
            {'status':True, 'response':policylist}
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
        return {'status':True, 'response':policylist}

    #=====================================================
    #============= Internal APIs  ========================
    #============Avoid using directly=====================
    #============Use Wrappers as above====================
    def get_policyaccess_summary(self):
        """ GET Policy access summary details

        Args:
            kwargs (dict): additional parameters to be passed

        Returns:
            dict: response of api call

        Raises:
            ApiClientException: when unexpected query parameters are passed.
        """
        url = '/'+ DEFAULT_VERSION + POLICY_SUMMARY_PATH
        method = 'GET'
        params={'defaultPolicy':True}
        response = self._session.api_switch_call(method=method,
                                                      resource_path=url,
                                                      params=params)
        self.log.info("Method {} \nURL {} \nData {}".format(method, url, kwargs))
        self.log.info("Response {}".format(response))
        return response

    def get_policyaccess_count(self):
        url = '/'+ DEFAULT_VERSION + POLICY_COUNT_PATH
        method = 'GET'
        response = self._session.api_switch_call(method=method,
                                                    resource_path=url)
        self.log.info("Response {}".format(response))
        return response

    def post_policyaccess(self, **kwargs):
        '''
            Function: post request for policy access
            Description: POST request for policy access
            INPUT: kwargs
            OUTPUT: response
        '''
        url = '/'+ DEFAULT_VERSION + POLICY_PATH
        method = 'POST'
        response = self._session.api_switch_call(method=method,
                                                      resource_path=url,
                                                      **kwargs)
        self.log.info("Method {} \nURL {} \nData {}".format(method, url, kwargs))
        self.log.info("Response {}".format(response))
        return response

    def put_policyaccess(self,**kwargs):
        """ Update request for Policy access

        Args:
            kwargs (dict): additional parameters to be passed

        Returns:
            dict: response of api call

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
        
    def delete_policyaccessById(self,ref_id,**kwargs):
        """ 
        Delete request for Policy access

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


