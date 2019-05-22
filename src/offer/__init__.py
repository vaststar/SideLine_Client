import os,uuid
# serverhost="http://127.0.0.1:44444/rest"
serverhost="http://192.168.33.128:8188/rest"
chromeName="chromedriver_74.exe"

#生成机器码
MachineID=None
MachinePath=os.path.join(os.path.dirname(os.path.realpath(__file__)),'machineID.ini')
with open(MachinePath,'a') as f:
    pass
with open(MachinePath,'r+') as f:
    MachineID=str(f.read())
    if not MachineID:
        MachineID=str(uuid.uuid1())
        f.write(MachineID)
