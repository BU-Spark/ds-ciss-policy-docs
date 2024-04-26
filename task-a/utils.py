import re
import cn2an

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
    idxs = sorted(idxs, key=lambda x: x[0])
    overlap = True
    while overlap:
        overlap = False
        for i in range(len(idxs)-1, 0, -1):
            if idxs[i][0] < idxs[i-1][1]:
                idxs[i-1] = (idxs[i-1][0], idxs[i][1])
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

def get_end_word(paragraph, number_pattern, number_chinese_pattern):
    end_word = None
    try:
        number_result = re.search(number_pattern, paragraph)
        number_chinese_result = number_chinese_pattern.search(paragraph)
        
        if number_result and number_chinese_result:
            # if both number and chinese number exist, we choose the one smaller in index
            number_index = paragraph.index(number_result.group())
            number_chinese_index = paragraph.index(number_chinese_result.group())
            if number_index < number_chinese_index:
                number_chinese_result = None
            else:
                number_result = None
        
        if number_result:
            number = re.search(number_pattern, paragraph).group()
            index = paragraph.index(number)

            target_number = str(int(number) + 1)
            target_number = str(target_number)

            end_word = target_number + paragraph[index + len(number)]
        
        elif number_chinese_result:
            number = re.search(number_chinese_pattern, paragraph).group()
            index = paragraph.index(number)

            number_int = cn2an.cn2an(number)
            number_int += 1
            target_number = cn2an.an2cn(number_int)

            end_word = target_number + paragraph[index + len(number)]
    except:
        pass
    
    return end_word

# a helper function to add the content between current sentence and the next sentence
def add_next_sentence(paragraphs, paragraph, next_index, matched_paragraphs, match, default_reason):
    temp = [paragraph]
    # Check if the next sentence index is valid, if it is valid, we add the content between current sentence and the next sentence
    if next_index < len(paragraphs):
        temp += [paragraphs[next_index]]
        for index, sentence in enumerate(temp):
            if index == 0:
                matched_paragraphs.append((sentence, match.group()))
            else:
                matched_paragraphs.append((sentence, default_reason))
    # If the next sentence index is not valid, we only add the current content 
    else:
        matched_paragraphs.append((paragraph.strip(), match.group()))
        
    return matched_paragraphs