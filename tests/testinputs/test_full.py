import json
import pdb
import time
import re

time = time.time()
res_time = str(re.search("(\d+).(\d+)",(str(time))).group(1))
range_num = int(input("Enter scale number:"))
jfile = "testinputs.json"
file_name = "testinputs_"+str(range_num)+"_"+res_time+".json"
with open(jfile,'r+') as jfile_new:
    sf=json.load(jfile_new)
    sgt_create_list = []
    for i in range(1,range_num):
        cg={}
        cg["sgName"] ="SGNAME"+ "500"+str(i)
        cg["sgTag"] = 500+ i
        sgt_create_list.append(cg)
    (sf["SGTINPUTS"]["CREATESGTLIST"]).extend(sgt_create_list)
    sgt_create_list_vn = []
    for i in range(1,range_num):
        ch = {}
        ch["sgName"] = "SGNAME"+ "6000"+str(i)
        ch["sgTag"] = 6000 + i
        ch["virtualNetworks"] = ["test1234"]
        sgt_create_list_vn.append(ch)
    (sf["SGTINPUTS"]["CREATESGTVNLIST"]).extend(sgt_create_list_vn)
    sgt_get_list = []
    for i in range(1,range_num):
        cj={}
        cj["sgName"] ="SGNAME"+ "500"+str(i)
        sgt_get_list.append(cj)
    (sf["SGTINPUTS"]["GETSGTLIST"]).extend(sgt_get_list)
    sgt_check_list = []
    for i in range(1,range_num):
        ce ="SGNAME"+ "500"+str(i)
        sgt_check_list.append(ce)    
    (sf["SGTINPUTS"]["SECURITYGROUPLIST"]).extend(sgt_check_list)
    sgt_updatetag_list = []
    for i in range(1,range_num):
        ck={}
        ck["sgName"] ="SGNAME"+ "500"+str(i)
        ck["sgTag"] = 2000 + i
        sgt_updatetag_list.append(ck)
    (sf["SGTINPUTS"]["UPDATESGTTAGLIST"]).extend(sgt_updatetag_list)
    sgt_updatedes_list = []
    for i in range(1,range_num):
        cl={}
        cl["sgName"] ="SGNAME"+ "6000"+str(i)
        cl["description"] = "Update description of "+"6000"+str(i)
        sgt_updatedes_list.append(cl)
    (sf["SGTINPUTS"]["UPDATESGTDESLIST"]).extend(sgt_updatedes_list)
    sgt_updatevn_list = []
    for i in range(1,range_num):
        cq={}
        cq["sgName"] ="SGNAME"+ "500"+str(i)
        cq["virtualNetworks"] = ["test123456"]
        sgt_updatevn_list.append(cq)
    (sf["SGTINPUTS"]["UPDATESGTVNLIST"]).extend(sgt_updatevn_list)
    sgt_delete_list = []
    for i in range(1,range_num):
        cw={}
        cw["sgName"] ="SGNAME"+ "500"+str(i)
        sgt_delete_list.append(cw)
    (sf["SGTINPUTS"]["DELETESGTLIST"]).extend(sgt_delete_list)
    sgt_delete2_list = []
    for i in range(1,range_num):
        cr={}
        cr["sgName"] ="SGNAME"+ "6000"+str(i)
        sgt_delete2_list.append(cr)
    (sf["SGTINPUTS"]["DELETESGTLIST"]).extend(sgt_delete2_list)

    contract_create_list = []
    for i in range(1,range_num):
        dq={}
        dq["contract_name"] ="CONTRACT"+ "6000"+str(i)
        dq["description"] = "SAMPLE Contract"+ str(i)
        dq["contract_data"] = [{"access": "PERMIT","applicationName":"lockd","dstNetworkIdentities":[{"protocol":"UDP","ports":"4045"},{"protocol":"TCP","ports":"4045"}],"logging": "OFF"}]
        contract_create_list.append(dq)
    (sf["CONTRACTINPUTS"]["CREATECONTRACTLIST"]).extend(contract_create_list)

    contract_updatedes_list = []
    for i in range(1,range_num):
        dw={}
        dw["contract_name"] ="CONTRACT"+ "6000"+str(i)
        dw["description"] = "Update descr SAMPLE Contract"+ str(i)
        contract_updatedes_list.append(dw)
    (sf["CONTRACTINPUTS"]["UPDATECONTRACTLISTDES"]).extend(contract_updatedes_list)

    contract_updatedata_list = []
    for i in range(1,range_num):
        de={}
        de["contract_name"] ="CONTRACT"+ "6000"+str(i)
        de["contract_data"] = [{"access": "PERMIT","applicationName":"softpc","dstNetworkIdentities":[{"protocol":"UDP","ports":"271"},{"protocol":"TCP","ports":"271"}],"logging": "OFF"}]
        contract_updatedata_list.append(de)
    (sf["CONTRACTINPUTS"]["UPDATECONTRACTLISTDATA"]).extend(contract_updatedata_list)

    contract_check_list = []
    for i in range(1,range_num):
        dy="CONTRACT"+ "6000"+str(i)
        contract_check_list.append(dy)
    (sf["CONTRACTINPUTS"]["CONTRACTCHECKLIST"]).extend(contract_check_list)

    contract_get_list = []
    for i in range(1,range_num):
        du={}
        du["contract_name"] ="CONTRACT"+ "6000"+str(i)
        contract_get_list.append(du)
    (sf["CONTRACTINPUTS"]["GETCONTRACTLIST"]).extend(contract_get_list)

    contract_del_list = []
    for i in range(1,range_num):
        di={}
        di["contract_name"] ="CONTRACT"+ "6000"+str(i)
        contract_del_list.append(di)
    (sf["CONTRACTINPUTS"]["DELETECONTRACTLIST"]).extend(contract_del_list)

    policy_create_list = []
    for i in range(1,range_num):
        pq={}
        pq["policy_name"] ="test"+ "800"+str(i)
        pq["srcSGName"] = "SGNAME"+ "500"+str(i)
        pq["dstSGName"] = "SGNAME"+ "6000"+str(i)
        pq["accessContract"] = "CONTRACT"+"6000"+str(i)     
        policy_create_list.append(pq)
    (sf["POLICYINPUTS"]["CREATEPOLICYLIST"]).extend(policy_create_list)        

    policy_update_list = []
    for i in range(1,range_num):
        pw={}
        pw["srcSGName"] = "SGNAME"+ "500"+str(i)
        pw["dstSGName"] = "SGNAME"+ "6000"+str(i)
        pw["accessContract"] = "test"
        policy_update_list.append(pw)
    (sf["POLICYINPUTS"]["UPDATEPOLICYLIST"]).extend(policy_update_list)

    policy_check_list = []
    for i in range(1,range_num):
        pd={}
        pd["name"] = ("SGNAME"+ "500"+str(i))+"-"+("SGNAME"+ "6000"+str(i))
        pd["contract"] = "test"
        policy_check_list.append(pd)
    (sf["POLICYINPUTS"]["POLICYCHECKLIST"]).extend(policy_check_list)

    policy_delete_list = []
    for i in range(1,range_num):
        pe={}
        pe["srcSGName"] = "SGNAME"+ "500"+str(i)
        pe["dstSGName"] = "SGNAME"+ "6000"+str(i)
        policy_delete_list.append(pe)
    (sf["POLICYINPUTS"]["DELETEPOLICYLIST"]).extend(policy_delete_list)    
    
    with open(file_name, 'w') as f:
        json.dump(sf,f,indent=8)
