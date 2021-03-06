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
import pprint
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
logger = logging.getLogger("SecurityGroups")
import json
#Default Timers
DEFAULT_SGT_TIMEOUT=60
DEFAULT_TASK_COMPLETION_TIMEOUT=120

#URLs
PATH_SG = '/v2/data/customer-facing-service/scalablegroup/access'
PATH_SG_SUM = "/v2/data/customer-facing-service/summary/scalablegroup/access"
VIRTUALNETWORKSPATH = '/v2/data/customer-facing-service/virtualnetworkcontext'
ACACONTROLLERPATH = "/v1/aca-controller-service"

class SecurityGroups(object):
    """Cisco DNA Center Security Groups API (version: 2.3.3.0).
    Wraps the DNA Center Devices
    API and exposes the API as native Python
    methods that return native Python objects.
    """
    def __init__(self, 
                 session):
        """Initialize a new Devices
        object with the provided RestSession.
        Args:
            session(RestSession): The RESTful session object to be used for
                API calls to the DNA Center service.
        Raises:
            TypeError: If the parameter types are incorrect.
        """
        check_type(session._session, DnacClientManager)
        super(SecurityGroups, self).__init__()
        self._session = session._session
        self._task = session.task
        self.log = logger

    def createSecurityGroup(self, sgName, sgTag, sgDescription="", virtualNetworks=[], **kwargs):
        '''
            Ceate a security group in DNAC.
            Function: createSecurityGroup
            Input: 
                sgName =  Security Group Name
                sgTag = Security Group Tag
                sgDescription =  Security Group Description
                virtualNetworks =  list of Virtual Networks.
            Output:
                When Success : {'status':True}  
                When Failed  : {status:False, "failureReason":"<failure reason>"}
        '''
        check_type(sgName, basestring)
        check_type(sgTag,int)
        check_type(sgDescription,basestring)
        check_type(virtualNetworks,list)
        security_groups = [
            {
                "description": sgDescription,
                "name": sgName,
                "scalableGroupType": "USER_DEVICE",
                "securityGroupTag": sgTag
            }
        ]
        self.log.info("Creating a new security group {}".format(pprint.pformat(security_groups)))
        sg_response = self.post_securityGroup(json=security_groups, timeout=DEFAULT_SGT_TIMEOUT)
        self.log.info(sg_response)
        taskStatus = self._task.wait_for_task_complete(sg_response, timeout=DEFAULT_TASK_COMPLETION_TIMEOUT)
        self.log.info(taskStatus)
        if (taskStatus['isError']):
            self.log.error("Creating a new security group failed:{0}".format(taskStatus['failureReason']))
            return {'status':False, "failureReason":"Creating security group {} failed:{}".format(taskStatus['failureReason'])}
        else:
            self.log.info("#----SUCCESSFULLY CREATED SCALABLE GROUP //{}//----#".format(sgName))
        if not virtualNetworks:
            virtualNetworks = ['DEFAULT_VN']
        return self.addSecurityGroupToVirtualNetwork(sgName, virtualNetworks)

    def addSecurityGroupToVirtualNetwork(self, sg_name, virtualNetworks):
        '''
            Function: addSecurityGroupToVirtualNetwork
            INPUTs:
                virtualNetworks : List of Virtual Network Names
                sg_name : Security Group Name
            OUTPUT:
                When Success: {"status":True, "failureReason":""}
                {"status":False, "failureReason":"<Failure expanation>"
        '''
        check_type(sg_name,basestring)
        check_type(virtualNetworks,list)

        securityGroup = self.getSecurityGroupIdByName(sg_name)
        self.log.info(securityGroup)
        if securityGroup['status']:
            sg_idref = {"idRef":securityGroup['id']}
        else:
            return {'status':False, 'failureReason':securityGroup['failureReason']}
        self.log.info("Updating virtualNetworks")
        updatedVnData=[]
        vn_list = self.getVirtualNetwork()
        for vndata in vn_list['response']:
            if(vndata['name'] in virtualNetworks):
                if sg_idref not in vndata["scalableGroup"]:
                    vndata["scalableGroup"].append(sg_idref)
                    updatedVnData.append(vndata)

        if len(updatedVnData) != len(virtualNetworks):
            return {'status':False, 'failureReason':'Not all virtualNetworks provided, exist in DNAC, Create VirtualNetwork in DNAC first'}
        response = self.putVirtualNetwork(json=updatedVnData)
        self.log.info(response)
        taskStatus = self._task.wait_for_task_complete(response, timeout=240)
        if (taskStatus['isError']):
            self.log.error("Add sg to vn failed:{0}".format(taskStatus['failureReason']))
            return {'status':False, 
                    'failureReason':'Failed in updating SG in VirtualNetworks: {}'.format(taskStatus['failureReason'])}
        self.log.info("#######################################################################################")
        self.log.info("#----SUCCESSFULLY ADDED SG {} to VN {}----#".format(sg_name, virtualNetworks))
        self.log.info("#######################################################################################")
        return {"status":True}

    def updateSecurityGroup(self, name, securityGroupTag=None, description="",propagateToAci=None, virtualNetworks=[]):
        '''
            Function: updateSecurityGroup
            INPUTs:
                virtualNetworks : List of Virtual Network Names
                name : Security Group Name
                securityGroupTag: optional tag value
                description: Optional Description
            OUTPUT:
                When Success: {"status":True, "failureReason":""}
                {"status":False, "failureReason":"<Failure expanation>"
        '''
        check_type(name,basestring)
        check_type(virtualNetworks,list)
        check_type(description,basestring)
        check_type(securityGroupTag,int)
        check_type(propagateToAci,bool)

        self.log.info("Updating security group")
        params= { "name" : name }
        response_sg = self.get_securityGroup(params=params)
        sgt_data= {
                    "id":response_sg['response'][0]['id'],
                    "resourceVersion":response_sg['response'][0]['resourceVersion'],
                    "name":response_sg['response'][0]['name'],
                    "description":response_sg['response'][0]['description'],
                    "securityGroupTag":response_sg['response'][0]['securityGroupTag'],
                    "scalableGroupType":response_sg['response'][0]['scalableGroupType'],
                    "vnAgnostic":response_sg['response'][0]['vnAgnostic'],
                    "propagateToAci":response_sg['response'][0]['propagateToAci']
                }
        if securityGroupTag:
            sgt_data["securityGroupTag"] = securityGroupTag
        if description:
            sgt_data["description"] = description
        if propagateToAci:
            sgt_data["propagateToAci"] = propagateToAci
        sg_response = self.put_securityGroup(json=[sgt_data])
        taskStatus = self._task.wait_for_task_complete(sg_response, timeout=240)
        self.log.info(taskStatus)
        if (taskStatus['isError']):
            self.log.error("Updating security group failed:{0}".format(taskStatus['failureReason']))
            return {'status':False, 
                    'failureReason':'Failed in updating Security Group with reason: {}'.format(taskStatus['failureReason'])}
        if virtualNetworks:
            return self.addSecurityGroupToVirtualNetwork(name,virtualNetworks)
        return {'status':True}

    def checkSecurityGroupsExistingInDnac(self, securityGroupList, expect=True):
        '''
            Function: checkSecurityGroupsExistingInDnac
            Description: Check sg name and tag in dnac
            Input: List of Security Groups, expect = True/False
            Output: Success -> True
                    Failure -> False
        '''
        check_type(securityGroupList,list)
        check_type(expect,bool) 
        self.log.info("Start to check sg_list in DNAC")
        missing_list=[]
        exist_list=[]
        for sg in securityGroupList:
            params= { "name" : sg }
            response = self.get_securityGroup(params=params)
            if response['response']:
                exist_list.append(sg)
            else:
                missing_list.append(sg)

        if expect and missing_list:
            return {'status':False, 'failureReason':"These expected security groups are missing in DNAC: {}".format(missing_list)}
        elif not expect and exist_list:
            return {'status':False, 'failureReason':"These unexpected security groups are present in DNAC: {}".format(exist_list)}
        else:
            return {'status' : True }

    def getSecurityGroupIdByName(self, name):
        '''
            getSecurityGroupIdByName
            INPUT: Security Group name
            OUTPUT:
                if Security Group Found: {status:True, 'id':<id>}
                if Security Group not Found: {status:False, 'id':'', 'errorReason':''}
        '''
        check_type(name,basestring)

        self.log.info("Fetching security group id for {}".format(name))
        params = { "name" : name }
        response_sg = self.get_securityGroup(params=params)
        self.log.debug(response_sg)
        if response_sg['response']:
            return {"status" : True, 'id':response_sg['response'][0]['id']}
        else:
            self.log.error(response_sg)
            self.log.error('No security group with name {} found in DNAC.'.format(name))
            return {"status" : False, 'id':'', 'failureReason':'No security group with name {} found in DNAC.'.format(name)}

    def getSecurityGroupTagByName(self, name):
        '''
            getSecurityGroupTagByName
            INPUT: Security Group name
            OUTPUT:
                if Security Group Found: {status:True, 'securityGroupTag':<securityGroupTag>}
                if Security Group not Found: {status:False, 'securityGroupTag':'', 'errorReason':''}
        '''
        check_type(name,basestring)

        self.log.info("Fetching security group tag for {}".format(name))
        params = { "name": name}
        response_sg = self.get_securityGroup(params=params)
        self.log.debug(response_sg)
        if response_sg['response']:
            return {"status" : True, 'securityGroupTag':response_sg['response'][0]['securityGroupTag']}
        else:
            self.log.error(response_sg)
            self.log.error('No security group with name {} found in DNAC.'.format(name))
            return {"status" : False, 'securityGroupTag':'', 'failureReason':'No security group with name {} found in DNAC.'.format(name)}

    def getSecurityGroupCount(self):
        '''
            getSecurityGroupCount
            description: Return the count of SecurityGroups in DNAC
            INPUT: NA
            OUTPUT:
                status:True
                count: Total SGT count
        '''
        self.log.info("Return the count of security groups in DNAC")
        params = {'offset': 0, 'limit': 10, 'scalableGroupSummary': 'true'}
        response_sg = self.get_securityGroup_summary(params=params)
        if response_sg["response"]:
            response_sg_sum = response_sg["response"][0]
            sg_count = response_sg_sum["totalSGCount"]
            return {'status':True, "count":sg_count}
        else:
            return {'status':False, "count":0, 'failureReason':"No Summary response from DNAC"}

    def deleteSecurityGroupByName(self, name):
        '''
            deleteSecurityGroupByName
            description: Delete a give security group
            INPUT: name
            OUTPUT:
                status:True 
                status:False, failureReason: <reason> 
        '''
        check_type(name,basestring)

        params= { "name" : name }
        response_sg = self.get_securityGroup(params=params)
        sgt_data= {
                    "id":response_sg['response'][0]['id'],
                    "resourceVersion":response_sg['response'][0]['resourceVersion'],
                    "name":response_sg['response'][0]['name'],
                    "description":response_sg['response'][0]['description'],
                    "securityGroupTag":response_sg['response'][0]['securityGroupTag'],
                    "scalableGroupType":response_sg['response'][0]['scalableGroupType'],
                    "isDeleted":True
                }
        delete_response = self.put_securityGroup(json=sgt_data)
        self.log.debug(delete_response)
        taskStatus = self._task.wait_for_task_complete(delete_response)
        self.log.info(taskStatus)
        if (taskStatus['isError']):
            self.log.error("Deleting security group failed:{0}".format(taskStatus['failureReason']))
            return {"status" : False, 'failureReason':'Deleting security group {} failed:{}'.format(name,taskStatus['failureReason'])}
        self.log.info("#----SUCCESSFULLY DELETED Security Group {}----#".format(sg_name))
        return { "status" : True }

    def deleteSecurityGroupByTag(self, securityGroupTag):
        '''
            deleteSecurityGroupByTag
            description: Delete a give security group
            INPUT: securityGroupTag
            OUTPUT:
                status:True 
                status:False, failureReason: <reason> 
        '''
        check_type(securityGroupTag,int)

        params = { 'securityGroupTag' : securityGroupTag }
        response_sg = self.get_securityGroup(params=params)
        sgt_data= {
                    "id":response_sg['response'][0]['id'],
                    "resourceVersion":response_sg['response'][0]['resourceVersion'],
                    "name":response_sg['response'][0]['name'],
                    "description":response_sg['response'][0]['description'],
                    "securityGroupTag":response_sg['response'][0]['securityGroupTag'],
                    "scalableGroupType":response_sg['response'][0]['scalableGroupType'],
                    "isDeleted":True
                }
        
        delete_response = self.put_securityGroup(json=sgt_data)
        self.log.debug(delete_response)
        taskStatus = self._task.wait_for_task_complete(delete_response)
        self.log.info(taskStatus)
        if (taskStatus['isError']):
            self.log.error("Deleting security group failed:{0}".format(taskStatus['failureReason']))
            return {"status" : False, 'failureReason':'Deleting security group {} failed:{}'.format(name,taskStatus['failureReason'])}
        self.log.info("#----SUCCESSFULLY DELETED Security Group {}----#".format(sg_name))
        return { "status" : True }

    #Deploy Functions
    def push(self, verifyDone=False, verifyNoRequest=False, timeout=DEFAULT_SGT_TIMEOUT):
        '''
            Function: pushAndVerifySecurityGroups
            INPUT: 
                verifyDone = True/False  : To validate if the SGT push is complete.
                verifyNoRequest = True/False  : To validate there was no pending deploy action.
            OUTPUT:
                For Success: {'status':True}
                For Faillure: {'status':False, 'failureReason': "<reason string>"}
        '''
        check_type(verifyDone,bool)
        check_type(verifyNoRequest,bool)
        check_type(timeout,int)

        self.log.info("Start to deploy sg")
        response = self.put_acaControllerServicePush(timeout=timeout)
        response_deploy_sg = self._task.wait_for_task_complete(response)
        self.log.info(response_deploy_sg)
        if verifyDone:
            if (response_deploy_sg['data'] == "deployStatus=DONE"):
                self.log.info("######################################")
                self.log.info("#----SUCCESSFULLY DEPLOYED----#")
                self.log.info("######################################")
                return { 'status' : True }
            else:
                return { 'status' : False, 'failureReason': "Deploy status is not DONE, Reterived status:{}".format(response_deploy_sg ) }
        elif verifyNoRequest:
            if (response_deploy_sg['data'] == 'deployStatus=NO_REQUEST_AVAILABLE'):
                return { 'status' : True }
            else:
                return { 'status' : False, 'failureReason': "Deploy status is not NO_REQUEST_AVAILABLE, Reterived status:{}".format(response_deploy_sg )}
        return {'status' : True }

    def deploy(self, verifyDone=False, verifyNoRequest=False, retries=1, timeout=DEFAULT_SGT_TIMEOUT):
        '''
            Function: deployAndVerifySecurityGroups
            INPUT: 
                verifyDone = True/False  : To validate if the SGT push is complete.
                verifyNoRequest = True/False  : To validate there was no pending deploy action.
            OUTPUT:
                For Success: {'status':True}
                For Faillure: {'status':False, 'failureReason': "<reason string>"}
        '''
        check_type(verifyDone,bool)
        check_type(verifyNoRequest,bool)
        check_type(retries,int)
        check_type(timeout,int)
        try:
            while retries:
                try:
                    retries -=1
                    response = self.put_acaControllerServiceDeploy(timeout=timeout)
                    response_deploy = self._task.wait_for_task_complete(response)

                    self.log.info(response_deploy)
                    self.log.info("Deploy Status : {0}"
                                  .format(json.dumps(response_deploy, sort_keys=True, indent=4, separators=(',', ': '))))
                    if verifyDone:
                        if response_deploy['data'] == "deployStatus=DONE":
                            self.log.info("############################")
                            self.log.info("#----SUCCESSFULLY DEPLOYED----#")
                            self.log.info("############################")
                            return { 'status' : True }
                        else:
                            return { 'status' : False, 'failureReason': "Deploy Status : {0}".format(response_deploy)}
                    elif verifyNoRequest:
                        if response_deploy['data'] == 'deployStatus=NO_REQUEST_AVAILABLE':
                            return { 'status' : True }
                        else:
                            return { 'status' : False, 'failureReason': "Deploy Status : {0}".format(response_deploy)}
                    elif response_deploy['data'] == 'deployStatus=DONE' or response_deploy['data'] == 'deployStatus=NO_REQUEST_AVAILABLE':
                        return { 'status' : True }
                    else:
                        return { 'status' : False, 'failureReason': "Deploy Status : {0}".format(response_deploy)}
                except Exception as e:
                    if retries<1:
                        raise Exception(e)
                    else:
                        self.log.warning(e)
                        self.log.info("Retry again...")
                        time.sleep(10)
        except Exception as e:
            self.log.error("#################################################################################")
            self.log.error("#!!!FAILED TO DEPLOY. ERROR: {}----#".format(e))
            self.log.error("#################################################################################")
            raise Exception(e)
    #===============================================
    # API Calls
    #===============================================
    def post_securityGroup(self, **kwargs):
        '''
            Function: post_securityGroup
            Description: POST request in SGT Group
            INPUT: kwargs
            OUTPUT: response
        '''
        url = PATH_SG
        method = 'POST'
        response = self._session.api_switch_call(method=method,
                                                      resource_path=url,
                                                      **kwargs)
        self.log.info("Method {} \nURL {} \nData {}".format(method, url, kwargs))
        self.log.info("Response {}".format(response))
        return response

    def get_securityGroup(self,**kwargs):
        '''
            Function: get_securityGroup
            Description: GET request in SGT Group
            INPUT: kwargs
            OUTPUT: response
        '''
        url = PATH_SG
        method = 'GET'
        response = self._session.api_switch_call(method=method,
                                                      resource_path=url,
                                                      **kwargs)
        self.log.info("Method {} \nURL {} \nData {}".format(method, url, kwargs))
        self.log.info("Response {}".format(response))
        return response

    def delete_all_securityGroups(self, **kwargs):
        '''
            Function: delete_all_securityGroups
            Description: DELETE request in SGT Group
            INPUT: kwargs
            OUTPUT: response
        '''
        url = PATH_SG
        method = 'DELETE'
        response = self._session.api_switch_call(method=method,
                                                      resource_path=url,
                                                      **kwargs)
        self.log.info("Method {} \nURL {} \nData {}".format(method, url, kwargs))
        self.log.info("Response {}".format(response))
        return response

    def get_securityGroup_by_instance_uuid(self,sgt_instance_uuid,**kwargs):
        '''
            Function: get_securityGroup_by_instance_uuid
            Description: GET request in SGT Group from uuid
            INPUT: kwargs
            OUTPUT: Returns response
        '''
        check_type(sgt_instance_uuid,basestring)

        url = PATH_SG + "/{sgt_instance_uuid}"
        method = 'GET'
        response = self._session.api_switch_call(method=method,
                                                      resource_path=url,
                                                      **kwargs)
        self.log.info("Method {} \nURL {} \nData {}".format(method, url, kwargs))
        self.log.info("Response {}".format(response))
        return response

    def delete_securityGroup_by_instance_uuid(self, instance_uuid,**kwargs):
        '''
            Function: delete_securityGroup_by_instance_uuid
            Description: DELETE request for SGT Group by uuid
            INPUT: kwargs
            OUTPUT: response
        '''
        check_type(instance_uuid,basestring)

        url = PATH_SG + "/" + instance_uuid
        method = 'DELETE'
        response = self._session.api_switch_call(method=method,
                                                      resource_path=url,
                                                      **kwargs)
        self.log.info("Method {} \nURL {} \nData {}".format(method, url, kwargs))
        self.log.info("Response {}".format(response))
        return response

    def put_securityGroup(self, **kwargs):
        '''
            Function: put_securityGroup
            Description: Update request for SGT Group
            INPUT: kwargs
            OUTPUT: Returns response
        '''
        url = PATH_SG
        method = 'PUT'
        response = self._session.api_switch_call(method=method,
                                                      resource_path=url,
                                                      **kwargs)
        self.log.info("Method {} \nURL {} \nData {}".format(method, url, kwargs))
        self.log.info("Response {}".format(response))
        return response

    def get_securityGroup_summary(self,**kwargs):
        '''
            Function: get_securityGroup_summary
            Description: GET request for security group summary
            INPUT: kwargs
            OUTPUT: Returns response
        '''
        url = PATH_SG_SUM
        method = 'GET'
        self.log.info("Method {} \nURL {} \nData {}".format(method, url, kwargs))
        response = self._session.api_switch_call(method=method,resource_path=url,**kwargs)
        self.log.info("Response {}".format(response))
        return response

    def get_securityGroup_byparams(self,**kwargs):
        '''
            Function: get_securityGroup_byparams
            Description: GET request for security group summary by different parameters
            INPUT: kwargs
            OUTPUT: Returns response

        '''
        url = PATH_SG
        method = 'GET'
        response = self._session.api_switch_call(method=method,
                                                      resource_path=url,
                                                      params = kwargs)
        self.log.info("Response {}".format(response))
        sgid = response['response'][0]['id']
        self.log.info(" securityGroup uuid {}".format(sgid))
        return sgid

    #============================Virtual Networks Functions=======================
    def getVirtualNetwork(self, **kwargs):
        '''
            Function: getVirtualNetwork
            Description: GET request for virtual Network details
            INPUT: kwargs
            OUTPUT: Returns response
        '''
        url = VIRTUALNETWORKSPATH
        method = 'GET'
        response = self._session.api_switch_call(method=method,
                                                      resource_path=url,
                                                      **kwargs)
        self.log.info("Method {} \nURL {} \nData {}".format(method, url, kwargs))
        self.log.info("Response {}".format(response))
        return response

    def putVirtualNetwork(self, **kwargs):
        '''
            Function: putVirtualNetwork
            Description: Update request for virtual Network details
            INPUT: kwargs
            OUTPUT: Returns response
            
        '''
        url = VIRTUALNETWORKSPATH
        method = 'PUT'
        response = self._session.api_switch_call(method=method,
                                                      resource_path=url,
                                                      **kwargs)
        self.log.info("Method {} \nURL {} \nData {}".format(method, url, kwargs))
        self.log.info("Response {}".format(response))
        return response
    #=============================ACA Controller Functions=======================
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

    def put_acaControllerServicePush(self, **kwargs):
        '''
            Function: put_acaControllerServiceDeploy
            Description: Update request for controller service push action
            INPUT: kwargs
            OUTPUT: Returns response

        '''
        url = ACACONTROLLERPATH + "/pushSGs"
        method = 'PUT'
        response = self._session.api_switch_call(method=method,
                                                      resource_path=url,
                                                      **kwargs)
        self.log.info("Method {} \nURL {} \nData {}".format(method, url, kwargs))
        self.log.info("Response {}".format(response))
        return response
