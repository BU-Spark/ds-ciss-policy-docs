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

def find_执行过程规定(docs):
    pass
    
def find_一般政策语言(docs):
    pass