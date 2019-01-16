#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Thu Jan  4 23:22:26 2018

@author: annaelena
"""

from googleapiclient.discovery import build
import pprint
import urllib2
import re
import inflect
from word2number import w2n

        
service = build("customsearch", "v1",developerKey="AIzaSyAa-9zX05z1nZI4etQyQwTtH1qX1J1kZFs")

def numbers(word):
    #input string
    #word to number translate
    if word.isdigit()==True:
        p = inflect.engine()
        translated = p.number_to_words(word)
        return translated
    else:
        return str(w2n.word_to_num(word))
def nain(l1, l2):
    #l1=list of all keywords or list of all answers
    #l2=list of number keywords or list of number answers
    new_l2=[]
    for word in l2:
        findme=word
        for k in l1:
            newk=k.replace(findme, numbers(word))
            new_l2.append(newk)  
    return list(set(l1).union(new_l2+l2))


def counter(results, answer, kwords):
    ru = results.upper()
    answer_count= ru.count(answer.upper()) 
    for kw in kwords:
        answer_count = answer_count + ru.count(kw.upper())
    return answer_count


def main(qalist, kwords, kwnumlist, ansnumlist):
    #qalist=list of question and 3 answers
    #kwords=list of keywords
    #kwnumlist=listof number strings in kwords
    #ansnumlist=list of numbers in answers(alist)
    qu=qalist[0]
    alist=[qalist[1],qalist[2],qalist[3]]
    dict_1={}
    total_kwords=nain(kwords,kwnumlist)
    #Get master list of keywordss
    #get second list of translated answers
    for i in range(0,3):
        total=0
        res = service.cse().list( q=qu + ' ' + '{0}'.format(alist[i]) ,cx='016301781105508867602:gjgj8neq8aq', key='AIzaSyAa-9zX05z1nZI4etQyQwTtH1qX1J1kZFs').execute() # search question with i-th answer
        for item in res['items']:
            #load results item
            data=item['title']+item['snippet']
            toAdd=counter(data,alist[i], total_kwords)
            for nums in ansnumlist:
                if nums in alist[i]:
                    numsTrans=numbers(nums)
                    k1=alist[i]
                    newk=k1.replace(nums, numsTrans)
                    toAdd2=counter(data,newk,[])
            #count 
            total=total+toAdd+toAdd2
        dict_1[alist[i]]=total 
    return dict_1
