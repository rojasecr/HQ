import os 
import time

def start():
    s = os.listdir('/media/iPhone/DCIM/101APPLE')
    while True:
        s_1 = os.listdir('/media/iPhone/DCIM/101APPLE')
        if len(s_1) != len(s): 
            analyze(s_1[len(s_1)-1])                   
            s = s_1      
        time.sleep(0.1)
