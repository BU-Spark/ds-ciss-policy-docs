import re

def pre_process(text):
    text = re.sub(r"\n\n", "\n", text)
    # remove \u3000 and \u00a0
    # text = text.replace("\u3000", "").replace("\u00a0", "")
    paragraphs = re.split(r'。|\n', text.strip())
    # remove all empty strings
    paragraphs = [p for p in paragraphs if p.strip()]
    return paragraphs

def pre_process_without_n(text):
    text = re.sub(r"\n\n", "\n", text)
    # text = text.replace("\u3000", "").replace("\u00a0", "")
    paragraphs = re.split(r'。', text.strip())
    # remove all empty strings
    paragraphs = [p for p in paragraphs if p.strip()]
    return paragraphs

def printWithColor(doc, idxs):
    idxs = sorted(idxs, key=lambda x: x[0], reverse=True)
    overlap = True
    while overlap:
        overlap = False
        for i in range(len(idxs)-1, 0, -1):
            if idxs[i-1][0] < idxs[i][1]:
                idxs[i-1] = (idxs[i][0], idxs[i-1][1])
                idxs.pop(i)
                overlap = True
    for idx in idxs:
        doc = f'{doc[:idx[0]]}\033[30;103m{doc[idx[0]:idx[1]+1]}\033[0m{doc[idx[1]+1:]}'
    print(doc)

def standerlize_一般政策性内容(一般政策性内容):
    if 一般政策性内容 == [] or 一般政策性内容 == [''] or 一般政策性内容 == None:
        return []
    
    if isinstance(一般政策性内容[0], tuple):
        一般政策性内容 = [re.sub(r'\s+', '', content[0]) for content in 一般政策性内容]
    else:
        一般政策性内容 = [re.sub(r'\s+', '', content) for content in 一般政策性内容]
        
    return 一般政策性内容