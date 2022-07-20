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
import pdb

# compute the script path from this location
BASE_RUN_PATH = os.path.dirname("./")
#Read DNAC server parameters
clusterinput=os.path.join(BASE_RUN_PATH,"clusterInput/cluster.json")
#Read test specific parameters
testinputs=os.path.join(BASE_RUN_PATH,'tests/testinputs/testinputs_1000_1657558394.json')

MAX_TASK_WAIT_TIME=86400
def main():
    '''job file entrypoint'''

    job_list=[]
    script_name4 = os.path.join(BASE_RUN_PATH,'tests/testscripts/sgt_accesscontract_teardown.py')

    task1 = Task(testscript = script_name4,
                    cluster_inputs=clusterinput,
                    test_inputs=testinputs,
                    taskid = 'sgt_ac_teardown-{}'.format(script_name4.split('/')[-1]))
    job_list.append(task1)
    # start the task1
    task1.start()
    time.sleep(1)
    for task1 in job_list:
        result1 = task1.wait(MAX_TASK_WAIT_TIME)
        print(result1)
