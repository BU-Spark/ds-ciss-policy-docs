from thefuzz import process
import logging
import re
from utils import pre_process
import openai
from langchain_community.vectorstores import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import PromptTemplate

def __format_docs(docs):
    """
    Just a helper function to format the documents
    """
    return "\n\n".join(doc.page_content for doc in docs)

def get_answer_RegQA(docs, system_prompt, hint, example, question, feature_name, openai_key, chunk_size = 256, chunk_overlap = 20):
    """
    This is a general  function for information extraction using OpenAI API. It uses the RAG model to extract information from the documents.
    Args:
        docs (str): the policy text to search for the answer
        
        system_prompt (str): the system prompt for the RAG model should follow the format:
            "使用以下信息来回答最后的问题。你所有的回答都应该直接返回原文内容，如果你不知道答案，就说你不知道，不要试图编造答案。在回答的最后总是说"感谢您的提问"

            {context}

            问题: {question}"
            
        hint (str): the hint for the RAG model: 
            "提示: 提示：一般政策内容只描述政策目的，而不包含任政策本身细节。可能含有以下语句：为了，贯彻落实, 按照xx要求，依据xx规定，根据，等类似描述。除此之外，一般政策内容还可能提到国家最高领导人或机构（如"胡", "温", "习", "李", "党中央", "国务院"), 总则, 指导思想, 基本原则, 等类似概括性语句"
        
        example (str): the true example for few shot learning
            "示例：为认真贯彻落国家和省关于房地产工作的决策部署，加强和改进住房及用地供应管理，规范市场秩序，稳定市场预期，促进全市房地产市场平稳健康发展，按照适度、精准的调控原则，经市政府研究，决定对房地产市场有关政策进行调整完善。现就有关事宜通知如下："
        
        question (str): the real question to ask the model
            "文本中哪些语句在描述一般政策内容? 请返回原文所有文字"
            
        feature_name (str): The feature that you specific interested in, it can be "文件具体政策内容", "行政级别", etc. You can implement specific logic base on the feature name
        
        openai_key (str): the openai key
        
        chunk_size (int): the chunk size for the text splitter. Generally, if you are looking for small information, you can set it to a small number, like 256. If you are looking for a large information, you can set it to a large number, like 2048
        
        chunk_overlap (int): the chunk overlap for the text splitter. Generally, you can set it to less than 100
        
        
    Returns:
        str: the answer from the model
    """
    
    # set the openai key
    openai.api_key = openai_key
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap, length_function=len, is_separator_regex=False,)
    splits = text_splitter.split_text(docs)
    if feature_name == "文件具体政策内容":
        # only use the first split
        splits = [splits[0]]

    vectorstore = Chroma.from_texts(splits, embedding=OpenAIEmbeddings())
    Chroma.delete_collection(vectorstore)
    vectorstore = Chroma.from_texts(splits, embedding=OpenAIEmbeddings())
    
    retriever = vectorstore.as_retriever(search_kwargs={"k": 2})
    llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0)
    
    template = system_prompt + hint + f"\n{example}" + f"\nHelpful Answer:"
    
    custom_rag_prompt = PromptTemplate.from_template(template)
    
    rag_chain = (
        {"context": retriever | __format_docs, "question": RunnablePassthrough()}
        | custom_rag_prompt
        | llm
        | StrOutputParser()
    )
    
    return rag_chain.invoke(question)

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
        
    if last_index - first_index < 100 or len(matched_paragraphs) == 0 or last_index - first_index > 0.7 * len(docs):
        return [], [], 0, 0, 0
    else:
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