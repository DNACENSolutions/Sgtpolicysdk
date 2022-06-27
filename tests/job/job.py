'''
job.py

This job is to launch the script: sgttest.py, contracttest.py, policytests.py
This should be run in your python environment with pyats installed. 

Run this job from parent directory:
    pyats run job tests/job/job.py

Before running the job setup the environment variables:

Support Platform: Linux/MAC/Ubuntu

'''
# see https://pubhub.devnetcloud.com/media/pyats/docs/easypy/jobfile.html
# for how job files work

# optional author information
# (update below with your contact information if needed)
__author__ = 'Cisco Systems Inc.'
__copyright__ = 'Copyright (c) 2022, Cisco Systems Inc.'
__contact__ = ['pawansi@cisco.com']
__version__ = 1.0

import os
import time
from pyats.easypy import run
from pyats.easypy import Task

# compute the script path from this location
BASE_RUN_PATH = os.path.dirname("./")
#Read DNAC server parameters
clusterinput=os.path.join(BASE_RUN_PATH,"clusterInput/cluster.json")
#Read test specific parameters
testinputs=os.path.join(BASE_RUN_PATH,'tests/testinputs/testinputs.json')

MAX_TASK_WAIT_TIME=3600
def main():
    '''job file entrypoint'''

    
    job_list=[]
    script_name1 = os.path.join(BASE_RUN_PATH,'tests/testscripts/sgttest.py')
    script_name2 = os.path.join(BASE_RUN_PATH,'tests/testscripts/contracttest.py')
    script_name3 = os.path.join(BASE_RUN_PATH,'tests/testscripts/policytest.py')
    
    task1 = Task(testscript = script_name1,
                    cluster_inputs=clusterinput,
                    test_inputs=testinputs,
                    taskid = 'sgttest-{}'.format(script_name1.split('/')[-1]))
    job_list.append(task1)
    # start the task
    task1.start()
    time.sleep(1)

    # wait for a max runtime of 60*5 seconds = 5 minutes
    for task1 in job_list:
        result = task1.wait(MAX_TASK_WAIT_TIME)
        print(result)

    task2 = Task(testscript = script_name2,
                    cluster_inputs=clusterinput,
                    test_inputs=testinputs,
                    taskid = 'Accesscontracttest-{}'.format(script_name2.split('/')[-1]))
    job_list.append(task2)
    # start the task
    task2.start()
    time.sleep(1)

    # wait for a max runtime of 60*5 seconds = 5 minutes    
    for task2 in job_list:
        result = task2.wait(MAX_TASK_WAIT_TIME)
        print(result)
   
    task3 = Task(testscript = script_name3,
                    cluster_inputs=clusterinput,
                    test_inputs=testinputs,
                    taskid = 'SGTPolicytest-{}'.format(script_name3.split('/')[-1]))
    job_list.append(task3)
    # start the task
    task3.start()
    time.sleep(1)

    # wait for a max runtime of 60*5 seconds = 5 minutes    
    for task3 in job_list:
        result = task3.wait(MAX_TASK_WAIT_TIME)
        print(result)    

