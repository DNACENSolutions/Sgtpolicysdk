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

    >>> dnac = DNACenterSGTPolicyAPI(server=serverip,username=username,password=password)
    /Users/pawansingh/Library/Python/3.7/lib/python/site-packages/urllib3/connectionpool.py:1050: InsecureRequestWarning: Unverified HTTPS request is being made to host '...'. Adding certificate verification is strongly advised. See: https://urllib3.readthedocs.io/en/1.26.x/advanced-usage.html#ssl-warnings
      InsecureRequestWarning,

    >>> dnac.securitygroups.getSecurityGroupIdByName("Auditors")
    {'status': True, 'id': '6ed523e7-91e4-4600-b6ba-62b822e7f609'}

    >>> dnac.securitygroups.updateSecurityGroup("sampleSGT",virtualNetworks=["WiredVNFBLayer2"])
    {'status': True}

    >>> dnac.securitygroups.pushAndVerifySecurityGroups(verifyNoRequest=True)
    {'status': True}

    >>> dnac.securitygroups.updateSecurityGroup("sampleSGT",virtualNetworks=["VN1"])
    {'status': False, 'failureReason': 'Not all virtualNetworks provided, exist in DNAC, Create VirtualNetwork in DNAC first'}


Documentation
-------------

Check out the Quickstart_ to dive in and begin using sgtpolicysdk.


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
