=============
sgtpolicysdk
=============

*Work with the DNA Center SGT/Policy configuration in native Python!*

-------------------------------------------------------------------------------

**sgtpolicysdk** is a *cisco community developed* Python library for working with the DNA Center APIs security groups, access contracts and policies.  Our goal is to make working with DNA Center in Python a *native* and *natural* experience!

.. code-block:: python

    from sgtpolicysdk import DNACenterSGTPolicyAPI

Introduction_


Installation
------------

Installing and upgrading sgtpolicysdk is easy:
**Install through downloaded/cloned from github**

1. Checkout code.

.. code-block:: bash
    $ git clone git@github.com:DNACENSolutions/Sgtpolicysdk.git

2. Move to code directory

.. code-block:: bash
    $ cd Sgtpolicysdk

3. Install in your python environment
.. code-block:: bash
    $ python3 setup.py install

**Install via PIP**

.. code-block:: bash

    $ pip3 install sgtpolicysdk

**Upgrading to the latest Version**

.. code-block:: bash

    $ pip3 install sgtpolicysdk --upgrade


QuickUsageExample:
.. code-block:: bash
    shell$ python3
    Python 3.7.9 (v3.7.9:13c94747c7, Aug 15 2020, 01:31:08) 
    [Clang 6.0 (clang-600.0.57)] on darwin
    Type "help", "copyright", "credits" or "license" for more information.

    >>> from sgtpolicysdk import DNACenterSGTPolicyAPI
serverip="xx.xx.xx.xx"
username="xxxxxxxx"
password="xxxxxxxx"
version="2.2.3"
        
    >>> dnac = DNACenterSGTPolicyAPI(server=serverip,username=username,password=password)
    /Users/pawansingh/Library/Python/3.7/lib/python/site-packages/urllib3/connectionpool.py:1050: InsecureRequestWarning: Unverified HTTPS request is being made to host '...'. Adding certificate verification is strongly advised. See: https://urllib3.readthedocs.io/en/1.26.x/advanced-usage.html#ssl-warnings
      InsecureRequestWarning,

    >>> dnac.securitygroups.getSecurityGroupIdByName("Auditors")
    {'status': True, 'id': '6ed523e7-91e4-4600-b6ba-62b822e7f609'}

    >>> dnac.securitygroups.updateSecurityGroup("Auditors",virtualNetworks=["WiredVNFBLayer2"])
    {'status': True}

    >>> dnac.securitygroups.pushAndVerifySecurityGroups(verifyNoRequest=True)
    {'status': True}

    >>> dnac.securitygroups.updateSecurityGroup("Auditors",virtualNetworks=["VN1"])
    {'status': False, 'failureReason': 'Not all virtualNetworks provided, exist in DNAC, Create VirtualNetwork in DNAC first'}


Documentation
-------------

Security Group Functions Available:
===================================

1. createSecurityGroup(sgName, sgTag, sgDescription="", virtualNetworks=[])
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
 .. code-block:: bash
    >>> dnac.securitygroups.createSecurityGroup("SampleSGT1",1001,sgDescription="Sample SGT", virtualNetworks=["DEFAULT_VN", "testvn"])
    {'status': True}
    >>> 
    
2. updateSecurityGroup(name, securityGroupTag=None, description="",propagateToAci=None, virtualNetworks=[]):
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
 .. code-block:: bash
    >>> dnac.securitygroups.updateSecurityGroup("SampleSGT1",securityGroupTag=1002)
    {'status': True}
    
3. addSecurityGroupToVirtualNetwork(sg_name, virtualNetworks):
        '''
            Function: addSecurityGroupToVirtualNetwork
            INPUTs:
                virtualNetworks : List of Virtual Network Names
                sg_name : Security Group Name
            OUTPUT:
                When Success: {"status":True, "failureReason":""}
                {"status":False, "failureReason":"<Failure expanation>"
        ''')
 .. code-block:: bash
    >>> dnac.securitygroups.addSecurityGroupToVirtualNetwork("SampleSGT1",virtualNetworks=["DEFAULT_VN","testvn"])
    {'status': True}
    >>> dnac.securitygroups.addSecurityGroupToVirtualNetwork("SampleSGT1",virtualNetworks=["nonexistingvn"])
    {'status': False, 'failureReason': 'Not all virtualNetworks provided, exist in DNAC, Create VirtualNetwork in DNAC first'}

4. checkSecurityGroupsExistingInDnac(securityGroupList, expect=True):
        '''
            Function: checkSecurityGroupsExistingInDnac
            Description: Check sg name and tag in dnac
            Input: List of Security Groups, expect = True/False
            Output: Success -> True
                    Failure -> False
        ''' 
5. getSecurityGroupIdByName(name):
        '''
            getSecurityGroupIdByName
            INPUT: Security Group name
            OUTPUT:
                if Security Group Found: {status:True, 'id':<id>}
                if Security Group not Found: {status:False, 'id':'', 'errorReason':''}
        '''

6. getSecurityGroupTagByName(name):
        '''
            getSecurityGroupTagByName
            INPUT: Security Group name
            OUTPUT:
                if Security Group Found: {status:True, 'securityGroupTag':<securityGroupTag>}
                if Security Group not Found: {status:False, 'securityGroupTag':'', 'errorReason':''}
        '''

7. getSecurityGroupCount():
        '''
            getSecurityGroupCount
            description: Return the count of SecurityGroups in DNAC
            INPUT: NA
            OUTPUT:
                status:True
                count: Total SGT count
        '''
 .. code-block:: bash
    >>> dnac.securitygroups.getSecurityGroupCount()
    {'status': True, 'count': 36}

8. deleteSecurityGroupByName(name):
        '''
            deleteSecurityGroupByName
            description: Delete a give security group
            INPUT: name
            OUTPUT:
                status:True 
                status:False, failureReason: <reason> 
        '''

 9. deploy(verifyDone=False, verifyNoRequest=False, retries=1, timeout=DEFAULT_SGT_TIMEOUT):
        '''
            Function: deployAndVerifySecurityGroups
            INPUT: 
                verifyDone = True/False  : To validate if the SGT push is complete.
                verifyNoRequest = True/False  : To validate there was no pending deploy action.
            OUTPUT:
                For Success: {'status':True}
                For Faillure: {'status':False, 'failureReason': "<reason string>"}
        '''

 10. push(verifyDone=False, verifyNoRequest=False, timeout=DEFAULT_SGT_TIMEOUT):
        '''
            Function: pushAndVerifySecurityGroups
            INPUT: 
                verifyDone = True/False  : To validate if the SGT push is complete.
                verifyNoRequest = True/False  : To validate there was no pending deploy action.
            OUTPUT:
                For Success: {'status':True}
                For Faillure: {'status':False, 'failureReason': "<reason string>"}
        '''
  11. get_securityGroup_summary(**kwargs):
        '''
            Function: get_securityGroup_summary
            Description: GET request for security group summary
            INPUT: kwargs
            OUTPUT: Returns response
        '''
   .. code-block:: bash
      >>> dnac.securitygroups.get_securityGroup_summary()
    {'id': 'cd1a5a24-7f83-4a5b-a358-f08d97dc2a78', 'response': [{'instanceId': 0, 'instanceVersion': 0, 'totalSGCount': 36, 'acaScalableGroupSummary': []}

AccessContract Functions Available:
===================================
1. createNewContract()
2. dnac.accesscontracts.get_contractAccessSummary()
3. dnac.accesscontracts.put_acaControllerServiceDeploy()
4. dnac.accesscontracts.delete_contractAccessByName()
5. dnac.accesscontracts.getAllContractName()
6. dnac.accesscontracts.put_contractAccess()
7. dnac.accesscontracts.deploy()
8. dnac.accesscontracts.getContractCount()
9. dnac.accesscontracts.updateAccessContract()
10. dnac.accesscontracts.get_contractAccess()
11. dnac.accesscontracts.verifyContractExistInDnac()     
12. dnac.accesscontracts.get_contractAccessByName()
13. dnac.accesscontracts.post_contractAccess()  

AccessPolicy Functions Available:
===================================
1. dnac.sgtpolicy.createSecurityGroupPolicy()
2. dnac.sgtpolicy.updatePolicyStatusContract()
3. dnac.sgtpolicy.deploy()
4. dnac.sgtpolicy.createSecurityGroupPolicyFromDestinationToSources()
5. dnac.sgtpolicy.createSecurityGroupPolicyFromSourceToDestinations()
6. dnac.sgtpolicy.get_policyaccess()
7. dnac.sgtpolicy.getPolicyCount()
8. dnac.sgtpolicy.get_policyaccess_summary()
9. dnac.sgtpolicy.post_policyaccess()
10. dnac.sgtpolicy.put_policyaccess()
11. dnac.sgtpolicy.getPolicyFromSGToDG()
12. dnac.sgtpolicy.getAllPolicyNameContractList()


Release Notes
-------------

Please see the releases_ page for release notes on the incremental functionality and bug fixes incorporated into the published releases.


Questions, Support & Discussion
-------------------------------

sgtpolicysdk is a *community developed* and *community supported* project.  If you experience any issues using this package, please report them using the issues_ page.


Contribution
------------

sgtpolicysdk_ is a community development projects.  Feedback, thoughts, ideas, and code contributions are welcome!  Please see the `Contributing`_ guide for more information.


Inspiration
------------

This library is inspired by the webexteamssdk_  library


Changelog
---------

All notable changes to this project will be documented in the CHANGELOG_ file.

The development team may make additional name changes as the library evolves with the Cisco DNA Center APIs.


*Copyright (c) 2021-2022 Cisco Systems.*
