from thefuzz import process
import logging
import re
from utils import pre_process

def find_权宜处理_rule_base(docs):
    """Return the sentence that match 权宜处理 keywords using regular expression and fuzzy matching

    Returns:
        list of string: the all sentences that match 权宜处理 keywords
        list of tuple: the index of the matched sentences in the original text
    """
    logging.getLogger().setLevel(logging.ERROR)
    
    # keywords for regular expression
    keywords = ["结合.*实际", "根据.*实际", "根据实际情况", "结合实际情况", "权宜", "结合本地实际", "根据本地实际","因地制宜"]
    pattern = re.compile('|'.join(keywords))
    
    # keywords for fuzzy matching
    keywords_fuzzy = keywords = ["结合实际", "根据实际", "根据实际情况", "结合实际情况", "权宜", "结合本地实际", "根据本地实际","因地制宜"]
    
    paragraphs = pre_process(docs)
    
    matched_paragraphs = set()
    for paragraph in paragraphs:
        if pattern.search(paragraph):
            matched_paragraphs.add(paragraph.strip())
        else:
            best_match = process.extractOne(paragraph, keywords_fuzzy)
            if best_match[1] > 70:  
                matched_paragraphs.add(paragraph.strip())

    matched_paragraphs_index = []
    for sentence in matched_paragraphs:
        begin_index = docs.find(sentence)
        end_index = begin_index + len(sentence)
        matched_paragraphs_index.append((begin_index, end_index))
        
    return list(matched_paragraphs), matched_paragraphs_index

def find_执行过程规定_rule_base(docs,一般政策语言):
    logging.getLogger().setLevel(logging.ERROR)
    
    keywords =["(以|用|通过).*?(的方式|方法)","由.*?(主要负责|负责)"]
    pattern = re.compile('|'.join(keywords))
    
    keywords_fuzzy = ["流程","程序","执行","分工","牵头","责任","措施","个阶段","进度"]
    
    paragraphs = pre_process(docs)
    matched_paragraphs = set()
    
    for paragraph in paragraphs:
        if paragraph in 一般政策语言:
            continue
        if pattern.search(paragraph):
            matched_paragraphs.add(paragraph.strip())
        else:
            best_match = process.extractOne(paragraph, keywords_fuzzy)
            if best_match[1] > 70:
                matched_paragraphs.add(paragraph.strip())
                
    # find the first and the last index of the matched paragraph
    first_index = 1000000
    last_index = 0
    matched_paragraphs_index = []
    for sentence in matched_paragraphs:
        begin_index = docs.find(sentence)
        end_index = begin_index + len(sentence)
        matched_paragraphs_index.append((begin_index, end_index))
        first_index = min(first_index, begin_index)
        last_index = max(last_index, end_index)
        
    return list(matched_paragraphs), matched_paragraphs_index, first_index, last_index, last_index - first_index
    
    
    
def find_一般政策语言_rule_base(docs):
    logging.getLogger().setLevel(logging.ERROR)
    
    rule_1_keywords =["(?:^|,)\s*为[^,]*?落实","(?:^|,)\s*为[^,]*?贯彻", "(?:^|,)\s*为规范","(?:^|,)\s*为了规范"]
    rule_1_pattern = re.compile('|'.join(rule_1_keywords))
    rule_1_keywords_fuzzy = ["根据","现提出","提出如下","提出以下","现将","现就"]
    
    rule_2_keywords = ["胡锦涛", "温家宝", "习近平", "李克强", "党中央", "国务院"]
    
    rule_3_keyword_fuzzy = ["总则"]
    
    rule_4_keywords_fuzzy = ["指导思想", "基本原则"]
    
    paragraphs = pre_process(docs)
    matched_paragraphs = set()
    for paragraph in paragraphs:
        if rule_1_pattern.search(paragraph):
            matched_paragraphs.add(paragraph.strip())
        elif process.extractOne(paragraph, rule_1_keywords_fuzzy)[1] > 70:
            matched_paragraphs.add(paragraph.strip())
        elif any(keyword in paragraph for keyword in rule_2_keywords):
            matched_paragraphs.add(paragraph.strip())
        elif process.extractOne(paragraph, rule_3_keyword_fuzzy)[1] > 70:
            matched_paragraphs.add(paragraph.strip())
        elif process.extractOne(paragraph, rule_4_keywords_fuzzy)[1] > 70:
            matched_paragraphs.add(paragraph.strip())
        else:
            continue
    
    if len(matched_paragraphs) == 0:
        print("No matched information found, using default rule")
        pass
        
    
    matched_paragraphs_index = []
    for sentence in matched_paragraphs:
        begin_index = docs.find(sentence)
        end_index = begin_index + len(sentence)
        matched_paragraphs_index.append((begin_index, end_index))
        
    return list(matched_paragraphs), matched_paragraphs_index