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
logger = logging.getLogger("SecurityGroupsPolicy")

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
        super(SecurityGroups, self).__init__()
        self._session = session._session
        self._task = session.task
        self._sg = session._session
        self._contract = session.task
        self.log = logger

    @library_wrapper
    def createSecurityGroupPolicy(self, policy_name, producer_name, consumer_name, contract_name):
        self.log.info("Start to create policy from {} to {} with contract {}".format(producer_name, consumer_name, contract_name))
        try:
            self.log.info("get contract info")

            contract_response = self.services.get_contract_access(timeout=60)
            for response in contract_response["response"]:
                if response["name"] == contract_name:
                    contract_id = str(response["id"])

            sg_response = self.services.get_scalableGroup(timeout=60)

            for SG in sg_response["response"]:
                if SG["name"] == producer_name:
                    producer_id = str(SG["id"])
                if SG["name"] == consumer_name:
                    consumer_id = str(SG["id"])

            access_policy_response = self.services.get_policyaccess(timeout=60)
            for policyscope in access_policy_response["response"]:
                policy_scope_id = str(policyscope["policyScope"])

            self.log.info("Inside create new policy the Idref of the contract is: {0}".format(contract_id))

            condition = [{
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
            policy_response = self.services.post_policy_access(json=condition, timeout=60)
            taskStatus = self.services.wait_for_task_complete(policy_response, timeout=240)
            self.log.info(taskStatus)
            if (taskStatus['isError']):
                self.log.error("Creating policy failed:{0}".format(taskStatus['failureReason']))
                raise Exception("Creating policy failed:{0}".format(taskStatus['failureReason']))
            self.log.info("######################################################################################################")
            self.log.info("#----SUCESSFULLY CREATED TRUSTSEC POLICY from {} to {} with contract {}----#".format(producer_name, consumer_name, contract_name))
            self.log.info("######################################################################################################")
        except Exception as e:
            self.log.error("#################################################################################")
            self.log.error("#!!!FAILED TO CREATE NEW POLICY from {} to {} with contract {}. ERROR {}----#".format(producer_name, consumer_name, contract_name, e))
            self.log.error("#################################################################################")
            raise Exception(e)

    @library_wrapper
    def is_policy_exist_in_dnac(self, policy_list, expect=True):
        self.log.info("Start to check policy list in DNAC")
        try:
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
                else:
                    raise Exception("Some Policies don't exist in ACA DNAC"
                                    "or have different information: {}".format(missing_list))
            else:
                if len(missing_list)==len(policy_list):
                    self.log.info("#####################################################")
                    self.log.info("#----Policy list don't exists in DNAC as expected {}----#".format(policy_list))
                    self.log.info("#####################################################")
                else:
                    raise Exception("Some Contracts still exist in DNAC "
                                    "or have different information".format(exist_list))
        except Exception as e:
            self.log.error("#################################################################################")
            self.log.error("#!!!FAILED TO CHECK POLICY IN DNAC. ERROR: {}----#".format(e))
            self.log.error("#################################################################################")
            raise Exception(e)

    @library_wrapper
    def delete_policy(self, src_sg_name, dst_sg_name):
        self.log.info("Start to delete policy from {} to {}".format(src_sg_name, dst_sg_name))
        try:
            delete_id = ""
            src_sg_id = ""
            dst_sg_id = ""
            sg_response = self.services.get_scalableGroup(timeout=60)

            for sg in sg_response["response"]:
                if(sg["name"] == src_sg_name):
                    src_sg_id = str(sg["id"])
                    print(src_sg_id)
                if(sg["name"] == dst_sg_name):
                    dst_sg_id = str(sg["id"])
                    print(dst_sg_id)

            policy_response = self.services.get_policyaccess(timeout=60)
            # print(json.dumps(policy_response, sort_keys=True, indent=4, separators=(',', ': ')))
            if src_sg_id == '' or dst_sg_id == '' :
                raise Exception("The source or destination sg arenot found")
            for aca in policy_response["response"]:
                if dst_sg_id in aca["consumer"]["scalableGroup"][0]["idRef"] and src_sg_id in aca["producer"]["scalableGroup"][0]["idRef"]:
                    delete_id = aca["id"]
                    print(delete_id)

            if delete_id == '':
                raise Exception("The policy isnot found")


            delete_response = self.services.delete_policy_access_by_id(delete_id, timeout=60)
            self.log.info(delete_response)
            taskStatus = self.services.wait_for_task_complete(delete_response, timeout=240)
            self.log.info(taskStatus)
            if (taskStatus['isError']):
                self.log.error("Deleting policy failed:{0}".format(taskStatus['failureReason']))
                raise Exception("Deleting policy failed:{0}".format(taskStatus['failureReason']))

            self.log.info("###############################################################################################")
            self.log.info("#----SUCESSFULLY DELETED TRUSTSEC POLICY from {} to {}----#".format(src_sg_name, dst_sg_name))
            self.log.info("###############################################################################################")
        except Exception as e:
            self.log.error("#################################################################################")
            self.log.error("#!!!FAILED TO DELETE POLICY from {} to {} IN DNAC. ERROR: {}----#".format(src_sg_name, dst_sg_name, e))
            self.log.error("#################################################################################")
            raise Exception(e)

    @library_wrapper
    def get_policy_count(self):
        self.log.info("Start to count policies in DNAC")
        try:
            params = {'gbpSummary': 'true'}
            policy_response = self.services.get_policyaccess_summary(params=params, timeout=240)
            policy_response_summary = policy_response["response"][0]
            count = len(policy_response_summary["acaGBPSummary"])
            self.log.info("##Policies count on DNAC {}".format(count))
            return count
        except Exception as e:
            self.log.error("#################################################################################")
            self.log.error("#!!!FAILED TO GET POLICY COUNT IN DNAC. ERROR: {}----#".format(e))
            self.log.error("#################################################################################")
            raise Exception(e)

    @library_wrapper
    def update_policy(self, src_sg_name, dst_sg_name, mode=None, new_contract_name=None):
        self.log.info("Start to update policy from {} to {} in DNAC".format(src_sg_name, dst_sg_name))
        try:
            policy_id = ""
            contract_id = ""

            sg_response = self.services.get_scalableGroup(timeout=60)

            for sg in sg_response["response"]:
                if(sg["name"] == src_sg_name):
                    src_sg_id = str(sg["id"])
                    self.log.info(src_sg_id)
                if(sg["name"] == dst_sg_name):
                    dst_sg_id = str(sg["id"])
                    self.log.info(dst_sg_id)

            policy_response = self.services.get_policyaccess(timeout=60)
            self.log.info(json.dumps(policy_response, sort_keys=True, indent=4, separators=(',', ': ')))
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
                raise Exception('Policy isnot found')

            if mode is not None:
                policy_status = mode

            if new_contract_name is not None:
                contract_response = self.services.get_contract_access(timeout=60)
                for contract in contract_response["response"]:
                    if contract["name"] == new_contract_name:
                        contract_id = str(contract["id"])
                        break
                if contract_id == '':
                    raise Exception('The contract is not found')


            condition = [{
                "id": policy_id,
                "policyScope": policy_scope,
                "priority": policy_priority,
                "name": policy_name,
                "policyStatus": policy_status,
                "contract": {"idRef": contract_id},
                "producer": {"scalableGroup": [{"idRef":src_sg_id}]},
                "consumer": {"scalableGroup": [{"idRef":dst_sg_id}]}
                }]


            policy_response = self.services.put_policy_access(json=condition, timeout=60)
            taskStatus = self.services.wait_for_task_complete(policy_response, timeout=240)
            self.log.info(taskStatus)
            if (taskStatus['isError']):
                self.log.error("Updating policy failed:{0}".format(taskStatus['failureReason']))
                raise Exception("Updating policy failed:{0}".format(taskStatus['failureReason']))

            self.log.info("###############################################################################################")
            self.log.info("#----SUCESSFULLY UPDATED TRUSTSEC POLICY for {} to {}----#".format(src_sg_name, dst_sg_name))
            self.log.info("###############################################################################################")
        except Exception as e:
            self.log.error("#################################################################################")
            self.log.error("#!!!FAILED TO UPDATE POLICY FROM {} TO {} IN DNAC. ERROR: {}----#".format(src_sg_name, dst_sg_name, e))
            self.log.error("#################################################################################")
            raise Exception(e)


    def get_all_policy(self):
        self.log.info("Start to get all policies in DNAC")
        try:
            policylist = []

            # access_policy_response = self.services.get_policyaccess(timeout=60)
            params = {'gbpSummary': 'true'}
            policy_response = self.services.get_policyaccess_summary(params=params)
            policy_response_summary = policy_response["response"][0]

            # response_sg = self.services.get_scalableGroup(timeout=60)
            # params = {'offset': 0, 'limit': 5000, 'scalableGroupSummary': 'true'}
            # response_sg = self.services.get_scalableGroup_summary(params=params)
            # response_sg_sum = response_sg["response"][0]

            for policy in policy_response_summary["acaGBPSummary"]:
                # consumer_id = policy["consumer"]["scalableGroup"][0]["idRef"]
                # producer_id = policy["producer"]["scalableGroup"][0]["idRef"]
                # producer_name = ""
                # consumer_name = ""
                # for sg in response_sg_sum['acaScalableGroupSummary']:
                #     if sg["id"]==consumer_id:
                #         consumer_name = sg["name"]
                #     if sg["id"]==producer_id:
                #         producer_name = sg["name"]
                #     if consumer_name != "" and producer_name != "":
                #         break
                # name= producer_name + "-" + consumer_name
                #
                # contract_id = policy["contract"]["idRef"]
                # contract_res = self.services.get_contract_access_by_id(instance_uuid=contract_id)
                # contract_name = contract_res["response"][0]["name"]
                producer_name = policy["producerName"]
                consumer_name = policy["consumerName"]
                contract_name = policy["contractName"]
                name= producer_name + "-" + consumer_name
                policy_dict = {"name":name, "contract":contract_name}
                policylist.append(policy_dict)
            return policylist
        except Exception as e:
            self.log.error("#################################################################################")
            self.log.error("#!!!FAILED TO GET ALL POLICIES IN DNAC. ERROR: {}----#".format(e))
            self.log.error("#################################################################################")
            raise Exception(e)