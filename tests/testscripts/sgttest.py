from sgtpolicysdk.client_manager import DnacClientManager

d=DnacClientManager("10.195.243.53","admin","Maglev123")

print(d.call_api('GET','/v1/image/task/count?taskType=distribute,activate'))

from sgtpolicysdk.api.