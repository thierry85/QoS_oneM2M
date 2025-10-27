#!/usr/bin/python
##############################################################################
# Goal: oneM2M requests for QoS demonstration
# contributor:
# Thierry Monteil (thierry.monteil@irit.fr)
#
# Based on simple_om2m.py created by:
#   Ahmad Abbas (ahmad.abbas@eglobalmark.com)
#   Thierry Monteil (thierry.monteil@irit.fr)
#
# licence: common creative - Attribution 4.0 International (CC BY 4.0)
#############################################################################

import sys
import requests
import json
import random
import time
#ACME
CSE_URL="http://127.0.0.1:8080/~/id-in/cse-in"
ORIGIN="CAdmin"
CSE_LIST=["http://127.0.0.1:8080/~/id-in/cse-in","http://127.0.0.1:8080/~/id-in/cse-in","http://127.0.0.1:8080/~/id-in/cse-in"]

DEBUG_RESPONSE=0



def handleResponse(r):
    if DEBUG_RESPONSE ==1 :
        print (r.status_code)
        print (r.headers)
        print (r.text)

def createAE(origin,CSEurl,api_value,rn_value):
    payload = '{ \
        "m2m:ae": { \
        "api": "'+api_value+'", \
        "srv":["3"],\
        "rr": true,\
        "rn": "'+rn_value+'"\
        } \
    }'
    _headers =   {'X-M2M-Origin': origin,'X-M2M-RI': 'req1','X-M2M-RVI': '3','Content-Type': 'application/json;ty=2','Accept': 'application/json'}

    json.dumps(json.loads(payload,strict=False), indent=4)
    r = requests.post(CSEurl.strip(),data=payload,headers=_headers)
    handleResponse(r)
    return r;
############################
###    Delete an <AE>    ###
############################
def deleteAE(origin, CSEurl,api_value,rn_value):
    payload = ''
    _headers =   {'X-M2M-Origin': origin ,'X-M2M-RI': 'req1', 'X-M2M-RVI': '3','Content-Type': 'application/json'}
    r = requests.delete((CSEurl+'/'+rn_value).strip(),headers=_headers)
    handleResponse(r)
    return r;

###############################
###	Create a <Container>	###
###############################
def createContainer(origin,AEurl,rn_value):
	payload = '{ \
	    "m2m:cnt": { \
            "rn": "'+rn_value+'" \
	    } \
	}'
	_headers =   {'X-M2M-Origin': origin,'X-M2M-RI': 'req1', 'X-M2M-RVI': '3','Content-Type': 'application/json;ty=3'}
	json.dumps(json.loads(payload,strict=False), indent=4)
	r = requests.post(AEurl.strip(),data=payload,headers=_headers)
	handleResponse(r)
	return r;

###################################
###    Delete an <Container>    ###
###################################
def deleteContainer(origin,CSEurl,api_value,rn_value):
    payload = ''
    _headers =   {'X-M2M-Origin': origin,'X-M2M-RI': 'req1', 'X-M2M-RVI': '3','Content-Type': 'application/json'}
    r = requests.delete((CSEurl+'/'+rn_value).strip(),headers=_headers)
    handleResponse(r)
    return r;
    
###############################################################
###	Create a <ContentInstance> with mandatory attributes	###
###############################################################
def createContentInstance(origin,CONurl,con_value):

	payload = '{ \
	    "m2m:cin": { \
	    "con": "'+str(con_value)+'" \
	    } \
	}'
	_headers =   {'X-M2M-Origin': origin,'X-M2M-RI': 'req1', 'X-M2M-RVI': '3','Content-Type': 'application/json;ty=4'}
	json.dumps(json.loads(payload,strict=False), indent=4)
	r = requests.post(CONurl.strip(),data=payload,headers=_headers)
	handleResponse(r)
	return r;

#######################################
###	Get latest <ContentInstance>	###
#######################################
def getContentInstanceLatest(origin,CONurl):
    _headers =   {'X-M2M-Origin': origin,'X-M2M-RI': 'req1', 'X-M2M-RVI': '3','Accept': 'application/json'}
    r = requests.get(CONurl.strip(),headers=_headers)
    handleResponse(r)
    return r;


################################################################################
### Simple scenario select the CSE with best averageRunTime                  ###
################################################################################
def Test_averageRunTime(cse_list):
    # simulate the averageRunTime container for the CSE
    createContainer(ORIGIN,CSE_URL,"averageRunTime")
    createContentInstance(ORIGIN,CSE_URL+"/averageRunTime", 8002)
    print("averageRunTime created")
    # for each CSE in the list get the averageRunTime and select the best one
    bestaverageruntime=0
    bestcse=""
    for cse in cse_list:
        r=getContentInstanceLatest(ORIGIN,cse+"/averageRunTime/la")
        con_value = r.json().get("m2m:cin", {}).get("con")
        if (int(con_value) > bestaverageruntime) :
                bestaverageruntime=int(con_value)
                bestcse=cse
    print("best CSE :"+bestcse)
    print("with an average run time of:"+str(bestaverageruntime))
        
#####################################################################################
### Complexe scenario adapt sending rate of a sensor depending on CSE capabilitie ###
#####################################################################################
def Test_averageRate():
    # simulate the averageCreateRate container for the CSE
    createContainer(ORIGIN,CSE_URL,"averageCreateRate")
    createContentInstance(ORIGIN,CSE_URL+"/averageCreateRate", 500)
    print("averageCreateRate created")
    createContainer(ORIGIN,CSE_URL,"averageCreateRTT")
    createContentInstance(ORIGIN,CSE_URL+"/averageCreateRTT", 400)
    print("averageCreateRTT created")
    
    # select the good way to send data sensor
    createAE(ORIGIN+"0",CSE_URL, "NQoS.company.com", "QoS_AE")
    createContainer(ORIGIN,CSE_URL+"/QoS_AE","sensorValues")
    sensorRate=100
    r=getContentInstanceLatest(ORIGIN,CSE_URL+"/averageCreateRate/la")
    averageCreateRate = int(r.json().get("m2m:cin", {}).get("con"))
    r=getContentInstanceLatest(ORIGIN,CSE_URL+"/averageCreateRTT/la")
    averageCreateRTT = int(r.json().get("m2m:cin", {}).get("con"))
    # numbers of values to aggragate to satisfy averageCreateRate
    PossibleNumberValuesPerCreation=averageCreateRate/sensorRate
    # take care of the Create RTT and take the worst value
    if (PossibleNumberValuesPerCreation < averageCreateRTT):
        numberValuesPerCreation= averageCreateRTT
    else:
        numberValuesPerCreation=PossibleNumberValuesPerCreation
        
    # simulate the sensors send
    values=""
    for i in range(100):
        values=values+" "+str(i)
        if(i%5==0):
            createContentInstance(ORIGIN,CSE_URL+"/QoS_AE/sensorValues", values)
            print("send: "+values)
            values=""
        time.sleep(0.1)
    

#########################################
### run tests                         ###
#########################################
def main():
    print("test to select a CSE")
    Test_averageRunTime(CSE_LIST)
    print("------------------------")
    print("test to adapt transmission rate")
    Test_averageRate()
   
if __name__ == "__main__":
    main()
