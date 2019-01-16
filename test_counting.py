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
##  pool = ThreadPool(3) 
    search_list = []
    for a in alist:
        search_list.append(qu + ' ' + a)
##  results = pool.map(searcher, search_list)
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
            toAdd=counter(data,alist[i], [])
            for nums in ansnumlist:
                if nums in alist[i]:
                    numsTrans=numbers(nums)
                    k1=alist[i]
                    newk=k1.replace(nums, numsTrans)
                    toAdd2=counter(data,newk,[])
            #count 
            total=total+toAdd+toAdd2
        toAdd = 0
        for item in results[i]['items']:
            data=item['title']+item['snippet']
            toAdd=counter(data,'', total_kwords)   
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
   
