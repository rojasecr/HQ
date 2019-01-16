from google.cloud import language
client = language.LanguageServiceClient()


def documentizer(q): ## turns a string into the right format
    q_doc = language.types.Document(
        content=q,
        type=language.enums.Document.Type.PLAIN_TEXT,
    )
    return q_doc

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
    return ents, sals
           
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
        if token.part_of_speech.tag == 8:
            nums.append(str(token.text.content) )
    return nums
    
def kworder_numer(q): ##given a string returns a list of keywords, i.e entities including modifying adjs. Also returns another list with  the numbers from the text. 
    qd = documentizer(q) 
    ents_sals = entiter_salience(qd)
    kwords = ents_sals[0]
    nums= []
    response = client.analyze_syntax(
        document= qd,
        encoding_type='UTF32',
    )
    tokens = response.tokens
    for token in tokens:
        if token.part_of_speech.tag == 1:
            adj_text = str(token.text.content)
            head = token.dependency_edge.head_token_index
            head_pos = tokens[head].part_of_speech.tag 
            print token.dependency_edge
            if head_pos == 6:
                head_text = str(tokens[head].text.content)
                full = adj_text +' '+ head_text
                if head_text in ents:
                    ents.remove(head_text)
                if adj_text in ents:
                    ents.remove(adj_text)
                if full in ents:
                    ents.remove(full)
                kwords.append(full)
            else:
                if adj_text in ents:
                    ents.remove(adj_text)
                kwords.append(adj_text)
        elif token.part_of_speech.tag == 8:
            num_text = str(token.text.content)
            nums.append(num_text)
    return kwords, nums
