import traceback
import time
import logging
from past.builtins import basestring
logger = logging.getLogger("TaskManager")
TASK_COMPLETION_POLL_INTERVAL=2
GLOBAL_TASK_TIMEOUT = 360
from ...utils import (
    apply_path_params,
    check_type,
    dict_from_items_with_values,
    dict_of_str,
)

class Task(object):
    def __init__(self, session):
        self._session = session
        self.log = logger

    def wait_for_task_complete(self, response, timeout=GLOBAL_TASK_TIMEOUT, count=2):
        '''
            Function: wait_for_task_complete
            Input: response containing task details.
                timeout: Max time the Task considered completed.
                retry count
            Result:  True or False
        '''
        check_type(response,dict)
        check_type(timeout,int)
        check_type(count,int)
        self.log.info("Starting Task wait for task:{}".format(response))
        try:
            return self.__wait_for_task_complete(task_id=response['response']['taskId'], timeout=timeout)
        except TimeoutError:  # TODO: shouldn't this be a TimeoutError?
            traceback.print_exc()
            self.log.error(traceback.format_exc())
            if count <= 1:
                self.log.error("Timer Exceeded")
                return False
            return self.wait_for_task_complete(response, timeout=timeout, count=count-1)
        except:
            traceback.print_exc()
            self.log.error(traceback.format_exc())
            raise

    def get_task_details(self, task_id):
        """ Returns a high-level summary of the specified Grapevine task.

        Args:
            task_id (str): task id of the job
        """
        check_type(task_id,basestring)
        resource_path = "/v1/task/{}/tree".format(task_id)
        method = "GET"
        return self._session.api_switch_call(method=method,resource_path= resource_path)
    #--------------------------------------------------------------------------
    #helper for handling task status
    #--------------------------------------------------------------------------
    def task_handle(self, response, task_status="Complete", msg="Task Completion:",timeout=GLOBAL_TASK_TIMEOUT, count=2):
        '''helper for handling task status'''
        check_type(response,dict)
        check_type(task_status,basestring)
        check_type(timeout,int)
        check_type(count,int)
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
        check_type(task_id_result,basestring)
        assert task_id_result is not None
        task_id_response = task_id_result["response"]
        assert task_id_response is not None
        task_id = task_id_response["taskId"]
        assert task_id is not None
        return task_id

    def wait_for_task_success(self, task_id_result=None, timeout=None):
        """ Waits for a task to be a success. """
        check_type(task_id_result,basestring)
        check_type(timeout,int)
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
        check_type(task_id_result,basestring)
        check_type(timeout,int)
        if timeout is None:
            timeout = self.TASK_DEFAULT_TIMEOUT
        task_id = self.get_task_id_from_task_id_result(task_id_result)
        return self.__wait_for_task_failure(task_id=task_id, timeout=timeout)

    def get_task_by_id(self,task_id):
        check_type(task_id,basestring)
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
        '''
            Internal Function
        '''
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

