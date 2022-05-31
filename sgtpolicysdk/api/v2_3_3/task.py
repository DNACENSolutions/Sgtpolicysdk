import traceback
import time
import logging
logger = logging.getLogger("TaskManager")
#from services.dnaserv.lib.globals import PASS, FAIL, GLOBAL_TASK_TIMEOUT
TASK_COMPLETION_POLL_INTERVAL=2
GLOBAL_TASK_TIMEOUT = 360

class Task(object):
    def __init__(self, session):
        self._session = session
        self.log = logger

    def wait_for_task_complete(self, response, timeout=GLOBAL_TASK_TIMEOUT, count=2):
        self.log.info("Starting Task wait for task:{}".format(response))
        try:
            return self.__wait_for_task_complete(task_id=response['response']['taskId'], timeout=timeout)
        except :  # TODO: shouldn't this be a TimeoutError?
            traceback.print_exc()
            self.log.error(traceback.format_exc())
            if count <= 1:
                self.log.error("Timer Exceeded")
                return False
            return self.wait_for_task_complete(response, timeout=timeout, count=count-1)

    def get_task_details(self, task_id):
        """ Returns a high-level summary of the specified Grapevine task.

        Args:
            task_id (str): task id of the job
        """
        resource_path = "/v1/task/{}/tree".format(task_id)
        method = "GET"
        return self._session.api_switch_call(method=method,resource_path= resource_path)

    def wait_for_task_cfs_to_complete(self, response, timeout=GLOBAL_TASK_TIMEOUT, count=60):
        self.log.info("Waiting for CFS to complete for task:{}".format(response['response']['taskId']))
        try:
            flag=False
            task_detail = self.get_task_details(response['response']['taskId'])
            self.log.info(task_detail)
            for t in task_detail['response']:
                if "data" in t.keys()and "processcfs_complete=true" in t["data"].split(';'):
                    flag=True
                    break
                if "isError" in t.keys():
                    self.log.error("Task has errored")
                    return False
            if flag:
                self.log.info("cfs is complete for task-id:{}, ready to launch another cfs".format(response['response']['taskId']))
                return True
            elif count > 0:
                self.log.info("cfs is not complete for task-id:{}, Waiting for 5 seconds to recheck".format(response['response']['taskId']))
                time.sleep(5)
                return self.wait_for_task_cfs_to_complete(response,count=count-1)
            else:
                self.log.error("cfs is not complete for task-id:{}, Waiting time complete, returning false".format(response['response']['taskId']))
        except:
            traceback.print_exc()
            self.log.error(traceback.format_exc())
        return False
        
    def wait_for_tasks_list_complete(self, response_list,message="Task Message", timeout=GLOBAL_TASK_TIMEOUT, count=2):
        result=True
        for response in response_list:
            taskStatus = self.wait_for_task_complete(response,timeout=timeout)
            if taskStatus and (taskStatus['isError']):
                self.log.error("{0}:{1}".format(message,taskStatus['failureReason']))
                result &= False
            elif not taskStatus:
                result &= False
            else:
                self.log.info("{0} successfuly".format(message))
        return result

    def check_image_task_completion(self, response_list, message="Task Message", timeout=GLOBAL_TASK_TIMEOUT):
        """
        This lib is to check the status of image tasks after getting the taskId.
        Steps:
            1. Wait for task completion wait_for_task_complete
            2. If error, call /image/task to get error details
        wait_for_task_complete does not fetch error details
        :param response_list: list of responses, exp of one response:
            response = { "response" : {"taskId" : "", "imageName": "", "imageFamily": ""}}
        :param message: Message before the stating the API output
        :param timeout:
        :return: True if all the tasks were success
        """
        failures=[]
        result=True
        params = {
            'limit': 1,
            "sortBy": "startTime",
            "sortOrder": "des",
            "taskType": "import"
        }
        for response in response_list:
            self.log.info("Action: check task status!")
            taskStatus = self.wait_for_task_complete(response)
            self.log.info(taskStatus)
            if taskStatus and (taskStatus['isError']):
                url = "/v1/image/task"
                imageName = response["response"]["imageName"]
                imageFamily = response["response"]["imageFamily"]
                params["imageName"] = imageName
                response = self._session.api_switch_call(method="GET", resource_path=url, params=params)
                self.log.info(response)
                if response['response'] and "unitTaskUuid" in response['response'][0]:
                    taskId= response['response'][0]["unitTaskUuid"]
                    resp={"response":{}}
                    resp["response"]["taskId"] = taskId
                    taskStatus = self.services.wait_for_task_complete(resp)
                    if taskStatus and (taskStatus['isError']):
                        if taskStatus['failureReason'].find("Image already exists")!=-1:
                            self.log.warning("{0}".format(taskStatus['failureReason']))
                            self.log.info("\nAction: Trying to mark {0} Golden!!\n".format(imageName))
                            if not self.services.mark_image_golden(image=imageName,family=imageFamily):
                                self.log.error("Image is already exist, but could not mark it gold!!")
                                result &= False
                        else:
                            failures.append("Failed for Image {0}, reason:{1}".format(imageName, taskStatus['failureReason']))
            else:
                self.log.info("{0} successfully".format(message))
        if failures:
            self.log.error(failures)
            result &= False
        return result

    def wait_and_complete_all_active_tasks(self):
        result=True
        task_complte_items=[]
        for task_item in self.services.active_tasks_list:
            try:
                response=task_item['response']
                self.log.info("handling task item: {}".format(task_item))
                #self.log.log(response)
                taskStatus = self.services.wait_for_task_complete(response,timeout=GLOBAL_TASK_TIMEOUT)
                # self.log.debug(taskStatus)
                if(taskStatus['isError']):
                    self.log.debug(taskStatus)
                    self.log.error("Method {0} task failed for reason:{1}".format(task_item['method'],
                                    taskStatus['failureReason']))
                    result = False
                else:
                    self.log.info("Method {0} result for the task item: {1} is  Success".format(task_item['method'],task_item))
                task_complte_items.append(task_item)
            except :  # TODO: shouldn't this be a TimeoutError?
                traceback.print_exc()
                result = False
                task_complte_items.append(task_item)
        for i in task_complte_items:
            self.services.active_tasks_list.remove(i)

        return result


    #--------------------------------------------------------------------------
    #helper for handling task status
    #--------------------------------------------------------------------------
    def task_handle(self, response, task_status="Complete", msg="Task Completion:",timeout=GLOBAL_TASK_TIMEOUT, count=2):
        '''helper for handling task status'''
        try:
            if(task_status=="Complete"):
                taskStatus= self.wait_for_task_complete(response,timeout=timeout)
                self.log.info(taskStatus)
                if(taskStatus['isError']):
                    self.log.error("{0} {1}".format(msg,taskStatus['failureReason']))
                    return False
                else:
                    self.log.info("{0} successful,{1}".format(msg,taskStatus['progress']))
            elif(task_status=="Success"):
                taskStatus= self.wait_for_task_success(response,timeout=timeout)
                self.log.info(taskStatus)
                if(taskStatus['isError']):
                    self.log.error("{0} {1}".format(msg,taskStatus['failureReason']))
                    return False
                else:
                    self.log.info("{0} successful,{1}".format(msg,taskStatus['progress']))
            elif(task_status=="Failure"):
                taskStatus= self.wait_for_task_failure(response,timeout=timeout)
                self.log.info(taskStatus)
                if(taskStatus['isError']):
                    self.log.error("{0} {1}".format(msg,taskStatus['failureReason']))
                else:
                    self.log.info("{0} Expected Failed,{1}".format(msg,taskStatus['progress']))
                    return False
        except AssertionError:  # TODO: shouldn't this be a TimeoutError?
            traceback.print_exc()
            self.log.error(traceback.format_exc())
            if count <= 1:
                self.log.error("Timer Exceeded")
                return False
            self._session.reconnect_clients()  # TODO: move out of services
            return self.task_handle(response, task_status=task_status,msg=msg, timeout=timeout, count=count-1)
        return True
    #-----------------------
    def get_task_id_from_task_id_result(self, task_id_result):
        """ Gets a taskId from a given TaskIdResult. """

        assert task_id_result is not None
        task_id_response = task_id_result["response"]
        assert task_id_response is not None
        task_id = task_id_response["taskId"]
        assert task_id is not None
        return task_id

    def wait_for_task_success(self, task_id_result=None, timeout=None):
        """ Waits for a task to be a success. """

        if timeout is None:
            timeout = self.TASK_DEFAULT_TIMEOUT

        assert task_id_result is not None
        task_id = self.get_task_id_from_task_id_result(task_id_result)
        return self.__wait_for_task_success(task_id=task_id, timeout=timeout)

    def wait_for_task_failure(self, task_id_result, timeout=None):
        """ Waits for the task to be failure for a given task_id

        Args:
            task_id_result (str): task_id is waiting for the failure status.
            timeout (int): time_out value to wait to failure status of the task.

        Returns:
            object: response of the task.
        """

        if timeout is None:
            timeout = self.TASK_DEFAULT_TIMEOUT

        task_id = self.get_task_id_from_task_id_result(task_id_result)
        return self.__wait_for_task_failure(task_id=task_id, timeout=timeout)

    def get_task_by_id(self,task_id):
        return self._session.api_switch_call(method = "GET", resource_path = "/v1/task/{}".format(task_id))['response']

    def __wait_for_task_complete(self, task_id=None, timeout=None):

        if timeout is None:
            timeout = self.GLOBAL_TASK_TIMEOUT

        assert task_id is not None
        task_completed = False

        start_time = time.time()
        task_response = None

        while not task_completed:
            if time.time() > (start_time + timeout):
                assert False, ("Task {0} didn't complete within {1} seconds"
                               .format(task_response, timeout))
            task_response = self.get_task_by_id(task_id)
            self.log.info(task_response)
            if self.__is_task_success(task_response) or self.__is_task_failed(task_response):
                task_completed = True
                return task_response
            else:
                self.log.info("Task not completed yet, waiting:{}".format(task_response))
                time.sleep(TASK_COMPLETION_POLL_INTERVAL)
        return task_response

    def __wait_for_task_success(self, task_id=None, timeout=None):

        if timeout is None:
            timeout = self.GLOBAL_TASK_TIMEOUT

        assert task_id is not None
        task_completed = False

        start_time = time.time()
        task_response = None

        while not task_completed:
            if time.time() > (start_time + timeout):
                assert False, ("Task {0} didn't complete within {1} seconds"
                               .format(task_response, timeout))

            task_response = self.get_task_by_id(task_id)

            if self.__is_task_success(task_response):
                self.log.info("Task Completed, Task Response:{}".format(task_response))
                task_completed = True
                return task_response
            elif self.__is_task_failed(task_response):
                task_completed = True
                assert False, ("Task failed, task response {0}".format(
                    task_response))
            else:
                self.log.info("Task not success yet, waiting:{}".format(task_response))
                time.sleep(TASK_COMPLETION_POLL_INTERVAL)

        return task_response

    def __wait_for_task_failure(self, task_id, timeout=None):
        """ Waits for the task to be failure for a given task_id

        Args:
            task_id (str): task_id is waiting for the failure status.
            timeout (int): time_out value to wait for failure status of the task.

        Returns:
            object: response of the task.
        """

        if timeout is None:
            timeout = self.GLOBAL_TASK_TIMEOUT

        task_completed = False
        task_response = None
        start_time = time.time()

        while not task_completed:
            if time.time() > (start_time + timeout):
                msg = "Task {0} didn't complete within {1} seconds".format(task_response,
                                                                           timeout)
                assert False, msg
            task_response = self.get_task_by_id(task_id)

            self.log.info(task_response)

            if self.__is_task_success(task_response):
                task_completed = True
            elif self.__is_task_failed(task_response):
                task_completed = True
            else:
                self.log.info("Task not failed yet, waiting:{}".format(task_response))
                time.sleep(TASK_COMPLETION_POLL_INTERVAL)
        return task_response

    def __is_task_failed(self, task_response):
        assert task_response is not None
        return task_response["isError"] is True

    def __is_task_success(self, task_response, error_codes=[]):
        """
        :type error_codes: list
        """
        result=True
        assert task_response is not None
        for error_code in error_codes:
            if error_code is not None and hasattr(
                    task_response, 'errorCode') and error_code == task_response["errorCode"]:
                return True
        is_not_error = task_response["isError"] is None or task_response["isError"] is False
        is_end_time_present = task_response.get("endTime") is not None
        result = is_not_error and is_end_time_present
        if result:
            self.log.info("Task completed with result:{}".format(result))
        return result

