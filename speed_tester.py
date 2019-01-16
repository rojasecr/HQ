from multiprocessing.dummy import Pool as ThreadPool 

from googleapiclient.discovery import build
import pprint
import urllib2
import re
import inflect
from word2number import w2n

import os 
import time
import httplib2
import apiclient


from google.cloud import language
client = language.LanguageServiceClient()

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "visionkey.json"

def documentizer(q): ## turns a string into the right format
    q_doc = language.types.Document(
        content=q,
        type=language.enums.Document.Type.PLAIN_TEXT,
    )
    return q_doc
    
def numer(q): ## pulls out numbers
    doc = documentizer(d)
    nums = []   
    response = client.analyze_syntax(
        document= doc,
        encoding_type='UTF32',
    )
    tokens = response.tokens
    for token in tokens:
        if token.part_of_speech.tag == 7:
            nums.append(str(token.text.content))
    return nums

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
    

alist = ['which of these cities is the capital of America', 'Boston', 'Philadelphia', 'Washington D.C.']

pool = ThreadPool(4)
anums1 = pool.map(numer, alist)
