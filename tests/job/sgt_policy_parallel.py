import os
import json
from pyats.easypy import run
from pyats.easypy import Task
import time
import pprint

def map_usecases_to_scripts(usecase_directory):
    ''' **   Function to generate usecase vs Script mapping based give usecase path ** '''
    current_path = os.getcwd()
    os.chdir(usecase_directory)
    if os.getcwd().find(usecase_directory) == -1:
        print("Error not able to change directory")
        return False
    scripts = {}
    for uc in os.walk("./", topdown=True, onerror=None, followlinks=False):
        usecase = uc[0].split('/')[1]
        if usecase not in scripts.keys():
            scripts[usecase] = []
        for script in uc[2]:
            if script.find(".py") != -1 and script.find(".pyc") == -1:
                scripts[usecase].append(usecase_directory+uc[0][1:]+'/'+script )
    keys = list(scripts.keys())
    for key in keys:
        if not scripts[key]: del(scripts[key])
    os.chdir(current_path)
    return scripts

def generatestrlistfromrange(strlist):
    ''' ****   Function to make string list from a range string *** '''
    a=strlist.split('-')
    resultlist=[]
    if int(a[0]) > int(a[1]):
        for i in range(int(a[1]), int(a[0])+1,1):
            resultlist.append(str(i))
    else:
        for i in range(int(a[0]), int(a[1])+1,1):
            resultlist.append(str(i))
    return resultlist

## Workspace dir
HERE = os.getcwd()
## Read Env variable for usecase dir
usecase_directory = "{0}/{1}".format(os.path.join(BASE_RUN_PATH,os.environ.get('USECASE_DIRECTORY')) if os.environ.get('USECASE_DIRECTORY') else "{0}/test/sanityusecases".format(HERE)
## Generate Script maps with usecase.
scripts_map = (map_usecases_to_scripts(usecase_directory))
print("\n======Script lists available in usecases")
pprint.pprint(scripts_map)
print("\n========================================")
## Usecases execution order defined here or imported from premapped files.
paralleltestsets = {
    "1" : [
        {
            "1" : ["dnacCleanup","testbedTopologyGenerate"],
            "blocker_uc": []
        }
    ],
    "2" : [
        {
            "1" : ["ISECleanupGoldenConfig", "systemSWMgmtPackagesInstall","goldenConfigoverlayConfigCleanup"],
            "blocker_uc": ["systemSWMgmtPackagesInstall","goldenConfigoverlayConfigCleanup"]
        }
    ],
    
    "3" : [
        {
            "1" : ["systemUserAndRoleback","ISEIntegration"],
            "blocker_uc": ["systemUserAndRoleback","ISEIntegration"]
        }
    ]
}

#==============================================================================
## Test Execution control order of execution: Usecasegroups->Usecases->Testcases
testcase_run_data1 = {
                        "exec_groups_list": json.loads(os.environ.get('EXEC_UCGROUP_NUMBERS_LIST')) if os.environ.get('EXEC_UCGROUP_NUMBERS_LIST') else [],
                        "exec_uc_list": json.loads(os.environ.get('EXEC_UC_LIST')) if os.environ.get('EXEC_UC_LIST') else [],
                        "skip_groups_list": json.loads(os.environ.get('SKIP_GROUPS_LIST')) if os.environ.get('SKIP_GROUPS_LIST') else [],
                        "skip_uc_list": json.loads(os.environ.get('SKIP_UC_LIST')) if os.environ.get('SKIP_UC_LIST') else [],
                        "exec_tc_list": json.loads(os.environ.get('EXECUTE_TC_LIST')) if os.environ.get('EXECUTE_TC_LIST') else [],
                        "skip_tc_list": json.loads(os.environ.get('SKIP_TC_LIST')) if os.environ.get('SKIP_TC_LIST') else [],
                        "break_on_fail": json.loads(os.environ.get('BREAK_ON_FAIL')) if os.environ.get('BREAK_ON_FAIL') else True
                     }
#Update if there is any range items in the jenkins inputs
pprint.pprint(testcase_run_data1)
for item in ["exec_groups_list","skip_groups_list"]:
    newlist=[]
    for i in testcase_run_data1[item]:
        if isinstance(i,int):
            newlist.append(str(i))
        if isinstance(i,str) and i.find("-") != -1:
           newlist = newlist + generatestrlistfromrange(i)
        else:
            newlist.append(i)
    testcase_run_data1[item] = newlist
print("######################################################")
print("Test Execution Control:\n")
pprint.pprint(testcase_run_data1)
print("######################################################")
print("\n\nRunning the script from here:{0}\n\n".format(HERE))
#===========================================================================


# compute the script path from this location
BASE_RUN_PATH = os.path.dirname("./")
#Read DNAC server parameters
clusterinput=os.path.join(BASE_RUN_PATH,"clusterInput/cluster.json")
#Read test specific parameters
testinputs=os.path.join(BASE_RUN_PATH,'tests/testinputs/testinputs.json')

MAX_TASK_WAIT_TIME=86400
def main():
    '''
        Main execution , tasks launch, and tasks converge.
    '''
    # run the testscript
    keys=list(paralleltestsets.keys())
    #keys.sort()
    for k in keys:
        run_status=True
        k2=0
        if k in testcase_run_data1["skip_groups_list"] or int(k) in testcase_run_data1["skip_groups_list"] or (
            testcase_run_data1["exec_groups_list"] and (k not in testcase_run_data1["exec_groups_list"])):
            continue
        #for scriptlist in paralleltestsets[k]:
        scriptlist = paralleltestsets[k][0]
        blocker_uc_list = paralleltestsets[k][0]["blocker_uc"]
        print("Usecase list:")
        print(scriptlist)
        print("Blocker Usecase list:")
        print(blocker_uc_list)
        task_list = []
        k1 = "1"
        for usecase in scriptlist[k1]:
            print("Processing usecase:{}".format(usecase))
            if usecase in testcase_run_data1["skip_uc_list"] or (testcase_run_data1["exec_uc_list"] != []
                and (usecase not in testcase_run_data1["exec_uc_list"])):
                print("Skipping usecase:{} due to being part of skip list or not part of exec list".format(usecase))
                continue
            script_name = scripts_map[usecase][0]
            k2=k2+1
            task_1 = Task(testscript = script_name,
                            testcase_run_data=testcase_run_data1,
                            taskid = 'Task-{}-{}{}-{}'.format(script_name.split('/')[-1],k,k2,usecase))
            task_list.append(dict(task=task_1,uc= usecase))
            # start the task
            task_1.start()
            time.sleep(1)
        # wait for a max runtime of 60*5 seconds = 5 minutes
        for task_1 in task_list:
            task_1['task'].wait(3*60*60)
            result = task_1['task'].result
            print("Result of Usecase:{} is {}".format(task_1['uc'],result))
            if task_1['uc'] in blocker_uc_list:
                if str(result) != "passed":
                    run_status =  False
        print("Overall usecase group status:")            
        print(run_status)
        if testcase_run_data1['break_on_fail'] and not run_status:
            print("Breaking execution as BREAK_ON_FAIL is set to True and run status is failed for this usecase group.")
            break
        else:
            print("No Blocker failure,launching next set of usecases.")
