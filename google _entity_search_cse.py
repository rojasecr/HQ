#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Jan  4 23:22:26 2018

@author: annaelena
"""

from googleapiclient.discovery import build
import pprint
import json
import urllib2
import re

        
service = build("customsearch", "v1",developerKey="AIzaSyAa-9zX05z1nZI4etQyQwTtH1qX1J1kZFs")

def counter(results, answer, kwords):
    ru = results.upper()
    answer_count= ru.count(answer.upper()) 
    for kw in kwords:
        answer_count = answer_count + ru.count(kw.upper())
    return answer_count

def main(qalist, kwords):
    qu=qalist[0]
    dict_1={}
    for i in range(1,4):
        total=0
        res = service.cse().list( q=qu + ' ' + qalist[i],cx='016301781105508867602:gjgj8neq8aq', key='AIzaSyAa-9zX05z1nZI4etQyQwTtH1qX1J1kZFs').execute() # search question with i-th answer
        for item in res['items']:
            data=item['title']+item['snippet']
            toAdd=counter(data,qalist[i],kwords)
            total=total+toAdd
        dict_1[qalist[i]]=total 
    return dict_1
     
      
#  for keys in res.keys():
#      print keys
#      print res[keys]
#      print "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
#      print"\n"
#  for items in res:
#      pprint.pprint(res)
#      print "###################"
