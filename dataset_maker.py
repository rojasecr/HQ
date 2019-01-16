import subprocess

## Image to text module
import argparse
import io

from google.cloud import vision
from google.cloud.vision import types

import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "visionkey.json"
os.environ["GOOGLE_CLOUD_DISABLE_GRPC"]='True'


def detect_text(path):
    """Detects text in the file."""
    client = vision.ImageAnnotatorClient()

    with io.open(path, 'rb') as image_file:
        content = image_file.read()

    image = types.Image(content=content)

    response = client.text_detection(image=image)
    texts = response.text_annotations

    for text in texts:
        return(u'\n"{}"'.format(unicode(text.description)))

        vertices = (['({},{})'.format(vertex.x, vertex.y)
                    for vertex in text.bounding_poly.vertices])


def qa_format(raw):
    q_a = raw.split('?') #split the question from answers
    q = q_a[0].replace('\n', ' ') #get rid of newlines from question
    a1_a2_a3 = q_a[1].split('\n') #split by newlines
    q_a1_a2_a3 = [q] #initialize the final list and add the question
    for i in a1_a2_a3:
        if i != '':
            q_a1_a2_a3.append(i)
    return q_a1_a2_a3

##Keyword parsing module
from google.cloud import language
client = language.LanguageServiceClient()

def documentizer(q): ## turns a string into the right format
    q_doc = language.types.Document(
        content=q,
        type=language.enums.Document.Type.PLAIN_TEXT,
    )
    return q_doc
    
def tokenizer(s):
    doc = language.types.Document(
        content=s,
        type=language.enums.Document.Type.PLAIN_TEXT,
    )
    response = client.analyze_syntax(
        document= doc,
        encoding_type='UTF32',
    )
    return response.tokens    

def entiter_salience(doc): ## gives a list of entities and a list of salience scores with matching index.
    ents = []
    sals = []
    response = client.analyze_entities(
        document= doc,
        encoding_type='UTF32',
    )
    for entity in response.entities:
        ents.append(str(entity.name))
        sals.append(entity.salience)
    return dict(zip(ents,sals))
       
    
def numer(ts): ## pulls out numbers
    nums=[]
    for token in ts:
        if token.part_of_speech.tag == 7:
            nums.append(str(token.text.content) )
    return nums
    
def kworder_sals(q,ts): ##given a string and list tokens returns a list of keywords and corresponding salience scores, i.e entities including modifying adjs.
    qd = documentizer(q) 
    ents_sals = entiter_salience(qd)
    kwords_sals = ents_sals
    for token in ts:
        if token.part_of_speech.tag == 1:  ##if token is an adjective
            adj_text = str(token.text.content)
            head = token.dependency_edge.head_token_index 
            head_text = str(ts[head].text.content) 
            full = adj_text +' '+ head_text ##adjective noun phrase
            if head_text in ents_sals.keys(): 
                kwords_sals[full] = kwords_sals.pop(head_text)
            if adj_text in ents_sals.keys():
                kwords_sals[full] = kwords_sals.pop(adj_text)               
    return kwords_sals
       

## Answer scoring module, searches question with each answer and counts the occurencs of keywords and answers.

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
from colorama import init
from colorama import Fore, Back, Style
from word_forms.word_forms import get_word_forms
        

def numbers(word):
    #input string
    #word to number translate
    if word.isdigit()==True:
        p = inflect.engine()
        translated = p.number_to_words(word)
        return translated
    else:
        try:
            return str(w2n.word_to_num(word))
        except ValueError:
            return word
            
def nain(l1, l2):
    #l1=list of all keywords or list of all answers
    #l2=list of number keywords or list of number answers
    new_dict= l1
    for word in l2:
        findme=word
        for k in l1.keys():
            newk=k.replace(findme, numbers(word))
            new_dict[newk] = l1[k]
    return new_dict


def counter(results, answer, kwords,altdict):
    ru = results.upper()
    count_dict = {} ##Intialize the dict that will have round sal scores as keys and counts as values
    answer_count= ru.count(answer.upper())
    count_dict[answer] = answer_count ## count of answer
    for kw in kwords.keys():
        sal = "%.1f" % (kwords[kw],)
        count_dict[sal] = 0  ##set each sal score count to 0
    for kw in kwords.keys():
        c=0
        for form in altdict[kw]:    
            c += ru.count(form.upper())  
        sal ="%.1f" % (kwords[kw],) 
        answer_count+=c                       
        count_dict[sal] +=  c  ##add counts 
    return answer_count, count_dict


def main(qalist, kwords, kwnumlist, ansnums, results,f):
    init(autoreset = True)
    #qalist=list of question and 3 answers
    #kwords=list of keywords
    #kwnumlist=listof number strings in kwords
    #ansnumlist=list of numbers in answers(alist)
    ansnumlist = []
    for i in ansnums:
        ansnumlist = ansnumlist + i
    qu = qalist[0]
    alist=qalist[1:4]
    dict_1={}
    total_kwords=nain(kwords,kwnumlist)
    altdict={}
    for kw in total_kwords.keys():
        s=set([kw])
        alt=get_word_forms(kw)
        for key in alt:
            s=s.union(alt[key])
        ls=list(s)
        altdict[kw]=ls
    print altdict
    #Get master list of keywordss
    #get second list of translated answers
    total_counts = []
    for i in range(0,3):        
        total=0
        res = results[i]
        total_counts = {}
        total_counts[alist[i]]=0
        for j in range(0,11):
            index = '{}'.format(j/10.0)
            total_counts[index] = 0
        for item in res['items']:
            #load results item
            data=item['title']+item['snippet']
            c = counter(data,alist[i], total_kwords, altdict)
            toAdd=c[0]
            for s in c[1].keys():
                total_counts[s] = total_counts[s] + c[1][s]
            for nums in ansnumlist:
                toAdd2 = 0
                if nums in alist[i]:
                    numsTrans=numbers(nums)
                    k1=alist[i]
                    newk=k1.replace(nums, numsTrans)
                    toAdd2=counter(data,newk,{},{})[0]
                total=total + toAdd2
                total_counts[alist[i]] = total_counts[alist[i]] + toAdd2
            total=total+toAdd
        dict_1[alist[i]]=total 
        print total_counts
        f.write('{0: <5}'.format(total_counts[alist[i]]))
        for j in range(0,11):
            index = '{}'.format(j/10.0)
            f.write('{0: <5}'.format(total_counts[index]))
    if " NOT " in qu or " never " in qu:
        ##for not questions, highlight the least
        f.write('{0: <5}'.format(1))
        print "not"
        m = min(dict_1, key=dict_1.get)
        for i2 in range(0,3):
            print "\n"
            if alist[i2]==m:
                print(Back.GREEN + '|' * dict_1[alist[i2]] + alist[i2].upper() )
            else:
                print('|' * dict_1[alist[i2]] + alist[i2].upper())
        print "\n"            
       

    else:
        f.write('{0: <5}'.format(0))
        print "not not"
        m = max(dict_1, key=dict_1.get)
        for i2 in range(0,3):
            print "\n"
            if alist[i2]==m:
                print(Back.GREEN + '|' * dict_1[alist[i2]] + alist[i2].upper() )
            else:
                print('|' * dict_1[alist[i2]] + alist[i2].upper())
        print "\n"                
        

##Final program
from multiprocessing.dummy import Pool as ThreadPool 

import os 
import time
import httplib2
import apiclient

def build_request(http, *args, **kwargs):
    new_http = httplib2.Http()
    return apiclient.http.HttpRequest(new_http, *args, **kwargs)

def searcher(answer):
    service = build("customsearch", "v1",developerKey="AIzaSyAa-9zX05z1nZI4etQyQwTtH1qX1J1kZFs", requestBuilder=build_request)
    s =service.cse().list( q= unicode(answer) ,cx='016301781105508867602:gjgj8neq8aq', key='AIzaSyAa-9zX05z1nZI4etQyQwTtH1qX1J1kZFs').execute()
    if 'items' not in s:
        s =service.cse().list( q= s['spelling']['correctedQuery'] ,cx='016301781105508867602:gjgj8neq8aq', key='AIzaSyAa-9zX05z1nZI4etQyQwTtH1qX1J1kZFs').execute()
    return s 

if __name__ == '__main__':
    s = os.listdir('/media/iPhone/DCIM/102APPLE')
    with open('HQquestions.csv', 'a') as t:
        for i in range(1,4):
            t.write('a{0: <4}'.format(i))
            for j in range(0,11):
                index = '{}'.format(j/10.0)
                t.write('{0: <5}'.format(index))
        t.write('\n')
        while True:
            s_1 = os.listdir('/media/iPhone/DCIM/102APPLE')
            if len(s_1) != len(s): 
                subprocess.call(['convert', '{0}{1}'.format('../../../../media/iPhone/DCIM/102APPLE/', s_1[len(s_1)-1]), '-crop', '690x700+30+210', 'output.png']) #crop the screenshot
                rawtext = detect_text('output.png') # convert image to text
                formattedtext = qa_format(rawtext[2:-1]) # format text as a list [question, ans1, ans2, ans3]
                search_list = []   #intiate list of strings that will be used as google queries
                for a in formattedtext[1:4]:
                    search_list.append(formattedtext[0] + ' ' + a)
                pool = ThreadPool(4)                                                        
                results = pool.map(searcher, search_list)      ##Parallel version of getting results
                pool.close()
                pool.join()
                pool = ThreadPool(4)
                tokens_list = pool.map(tokenizer, formattedtext)   ##Parallel version of getting tokens   
                pool.close()
                pool.join()
                pool = ThreadPool(4)
                nums_list = pool.map(numer, tokens_list) ##Parallel version of getting numbers   
                pool.close()
                pool.join()
                kwords_sals = kworder_sals(formattedtext[0], tokens_list[0])
                main(formattedtext, kwords_sals, nums_list[0], nums_list[1:4], results, t)
                for r in results:
                    t.write('{0: <10}'.format(r['queries'].values()[0][0]['totalResults']))
                t.write('\n')
                e = [0, 0, 0]
                mr = input('Machine answer? ')
                e[mr-1] = 1
                f = open('HQtest.csv', 'a')
                for n in e:
                    f.write('{0: <5}'.format(n))    
                f.write('\n')
                f.close()
                e = [0, 0, 0]
                cr = input('Correct answer? ')
                e[cr-1] = 1
                f = open('HQlabels.csv', 'a')
                for n in e:
                    f.write('{0: <5}'.format(n))    
                f.write('\n')
                f.close()
                s = s_1      
            time.sleep(0.1)


    
## test version
## Only difference is file path in crop line and png instead of PNG
