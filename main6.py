import subprocess

## Image to text module
import argparse
import io

from google.cloud import vision
from google.cloud.vision import types

import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "visionkey.json"


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


from google.cloud import language
client = language.LanguageServiceClient()


def documentizer(q): ## turns a string into the right format
    q_doc = language.types.Document(
        content=q,
        type=language.enums.Document.Type.PLAIN_TEXT,
    )
    return q_doc
       
def adjer(doc): ## pulls out adjective noun pairs, not used in kworder
    adjs = []   
    response = client.analyze_syntax(
        document= doc,
        encoding_type='UTF32',
    )
    tokens = response.tokens
    for token in tokens:
        if token.part_of_speech.tag == 1:
            head = token.dependency_edge.head_token_index
            head_text = tokens[head].text.content
            adjs.append(str(token.text.content) +' '+ str(head_text))
    return adjs
    
def numer(doc): ## pulls out numbers
    nums = []   
    response = client.analyze_syntax(
        document= doc,
        encoding_type='UTF32',
    )
    tokens = response.tokens
    for token in tokens:
        if token.part_of_speech.tag == 7:
            nums.append(str(token.text.content) )
    return nums
    
def kworder_numer(q): ##given a string returns a list of keywords, i.e entities including modifying adjs. Also returns another list with  the numbers from the text. 
    qd = documentizer(q) 
    kwords = []
    nums=[]
    response = client.analyze_syntax(
        document= qd,
        encoding_type='UTF32',
    )
    tokens = response.tokens
    for token in tokens:
        t = token.part_of_speech.tag
        if t != 4 and t !=5 and t !=10 and t!=7:
            text = str(token.text.content)
            kwords.append(text)
        elif token.part_of_speech.tag == 7:
            num_text = str(token.text.content)
            nums.append(num_text)
    return kwords, nums
       

## Answer scoring module, searches question with each answer and counts the occurencs of keywords and answers.


from googleapiclient.discovery import build
import pprint
import re
import inflect
from word2number import w2n
from colorama import init
from colorama import Fore, Back, Style
from multiprocessing.dummy import Pool
from multiprocessing.dummy import Pool as ThreadPool 


        
service = build("customsearch", "v1",developerKey="AIzaSyAa-9zX05z1nZI4etQyQwTtH1qX1J1kZFs")

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
    new_l2=[]
    for word in l2:
        findme=word
        for k in l1:
            newk=k.replace(findme, numbers(word))
            new_l2.append(newk)  
    return list(set(l1).union(new_l2+l2))


def counter(results, kwords):
    ru = results.upper()
    answer_count = 0
    for kw in kwords:
        answer_count = answer_count + ru.count(kw.upper())
    return answer_count

def searcher(answer):
    return service.cse().list( q= unicode(answer) ,cx='016301781105508867602:gjgj8neq8aq', key='AIzaSyAa-9zX05z1nZI4etQyQwTtH1qX1J1kZFs').execute()
    


def main(qalist, kwords, kwnumlist, ansnumlist):
    init(autoreset = True)
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
##    pool = ThreadPool(3) 
    search_list = []
    for a in alist:
        search_list.append(qu + ' ' + a)
##    print search_list
##    results = pool.map(print, search_list)
##    print results
    results = []
    for item in search_list:
        results.append(searcher(item))
    res = results[0]['items'] + results[1]['items'] + results[2]['items']
    for i in range(0,3):
        toAdd2 = 0
        total=0
        for item in res:
            #load results item
            data=item['title']+item['snippet']
            toAdd=counter(data,[alist[i]])
            for nums in ansnumlist:
                if nums in alist[i]:
                    numsTrans=numbers(nums)
                    k1=alist[i]
                    newk=k1.replace(nums, numsTrans)
                    toAdd2=counter(data,[newk])
            #count 
            total=total+toAdd+toAdd2
        toAdd = 0
        for item in results[i]['items']:
            data=item['title']+item['snippet']
            toAdd=counter(data,total_kwords)   
            total = total + toAdd 
        dict_1[alist[i]]=total 
    if " NOT " in qu:
        ##for not questions, highlight the least
        print("not")
        m = min(dict_1, key=dict_1.get)
        for i2 in range(0,3):
            print( "\n")
            if alist[i2]==m:
                print(Back.GREEN + '|' * dict_1[alist[i2]] + alist[i2].upper() )
            else:
                print('|' * dict_1[alist[i2]] + alist[i2].upper())
        print( "\n")            
       

    else:
        print( "not not")
        m = max(dict_1, key=dict_1.get)
        for i2 in range(0,3):
            print( "\n")
            if alist[i2]==m:
                print(Back.GREEN + '|' * dict_1[alist[i2]] + alist[i2].upper() )
            else:
                print('|' * dict_1[alist[i2]] + alist[i2].upper())
        print("\n")           
    return dict_1
        
        

##Final program

def analyze(im):
    subprocess.call(['convert', '{0}{1}'.format('../../../../media/iPhone/DCIM/102APPLE/', im), '-crop', '690x700+30+210', 'output.png']) #crop the screenshot
    rawtext = detect_text('output.png') # convert image to text
    formattedtext = qa_format(rawtext[2:-1]) # format text as a list [question, ans1, ans2, ans3]
    kwords_qnums = kworder_numer(formattedtext[0]) # get question keywords and numbers
    anums = [] # intiate list that will contain numbers from the answers
    for i in formattedtext:
        di = documentizer(i)
        anums = anums + numer(di)
    scores = main(formattedtext, kwords_qnums[0], kwords_qnums[1], anums)
    print('\n')
    print(scores)
    
## Automater module. Checks if /media/iPhone/DCIM/102APPLE has grown every 0.1sec and if so runs analyze

import os 
import time

def start():
    s = os.listdir('/media/iPhone/DCIM/102APPLE')
    while True:
        s_1 = os.listdir('/media/iPhone/DCIM/102APPLE')
        if len(s_1) != len(s): 
            analyze(s_1[len(s_1)-1])                   
            s = s_1      
        time.sleep(0.1)    

    
## test version
## Only difference is file path in crop line and png instead of PNG
