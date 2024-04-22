from thefuzz import process
import cn2an
import logging
import re
from utils import pre_process, pre_process_without_n
import openai
from langchain_community.vectorstores import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import PromptTemplate
from transformers import AutoTokenizer, AutoModelForMaskedLM

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

def find_一般政策语言_rule_base(docs):
    """Return the sentence that match 一般政策语言 keywords using regular expression and fuzzy matching

    Returns:
        list of tuple: the all sentences that match 一般政策语言 keywords and the matched keywords
        list of tuple: the index of the matched sentences in the original text
    """
    logging.getLogger().setLevel(logging.ERROR)
    
    rule_1_keywords =["(?:^|,)\s*现将","(?:^|,)\s*现就","现.*?如下","(?:^|,)\s*为[^,]*?落实","(?:^|,)\s*为[^,]*?贯彻", "(?:^|,)\s*为规范","(?:^|,)\s*为了规范"]
    rule_1_pattern = re.compile('|'.join(rule_1_keywords))
    rule_1_keywords_fuzzy = ["现提出","提出如下","提出以下"]
    
    rule_2_keywords = ["胡锦涛", "温家宝", "习近平", "李克强", "党中央", "国务院"]
    
    rule_3_keyword = ["总\s*则","指导思想", "基本原则"]
    
    paragraphs = pre_process(docs)
    matched_paragraphs = []
    i = 0
    while i < len(paragraphs):
        paragraph = paragraphs[i]
        if rule_1_pattern.search(paragraph):
            if len(paragraph.strip()) <= 15:
                try:
                    previous_paragraph = paragraphs[i-1]
                    matched_paragraphs.append((previous_paragraph + "。" + paragraph.strip(), rule_1_pattern.search(paragraph).group()))
                except:
                    matched_paragraphs.append((paragraph.strip(), rule_1_pattern.search(paragraph).group()))
            else:
                matched_paragraphs.append((paragraph.strip(), rule_1_pattern.search(paragraph).group()))
        elif any(keyword in paragraph for keyword in rule_1_keywords_fuzzy):
            if len(paragraph.strip()) <= 15:
                try:
                    previous_paragraph = paragraphs[i-1]
                    matched_paragraphs.append((previous_paragraph + "。" + paragraph.strip(), [keyword for keyword in rule_1_keywords_fuzzy if keyword in paragraph][0]))
                except:
                    matched_paragraphs.append((paragraph.strip(), [keyword for keyword in rule_1_keywords_fuzzy if keyword in paragraph][0]))
            else:
                matched_paragraphs.append((paragraph.strip(), [keyword for keyword in rule_1_keywords_fuzzy if keyword in paragraph][0]))
        elif any(keyword in paragraph for keyword in rule_2_keywords):
            matched_paragraphs.append((paragraph.strip(), [keyword for keyword in rule_2_keywords if keyword in paragraph][0]))
        elif re.search('|'.join(rule_3_keyword), paragraph):
            temp = []
            temp += [paragraph]
            
            # number = ['1','2','3','4','5','6','7','8','9']
            number_pattern = re.compile(r'\d+')
            
            # number_chinese = ["一","二","三","四","五","六","七","八","九"]
            number_chinese_pattern = re.compile(r'(?:(?:[一二三四五六七八九]十)?[一二三四五六七八九]|十[一二三四五六七八九]?|二十|三十|四十|五十|六十|七十|八十|九十)')
            
            end_word = None
            try:
                if re.search(number_pattern, paragraph):
                    number = re.search(number_pattern, paragraph).group()
                    index = paragraph.index(number)

                    target_number = str(int(number) + 1)
                    target_number = str(target_number)

                    end_word = target_number + paragraph[index + len(number)]
                
                elif number_chinese_pattern.search(paragraph):
                    number = re.search(number_chinese_pattern, paragraph).group()
                    index = paragraph.index(number)

                    number_int = cn2an.cn2an(number)
                    number_int += 1
                    target_number = cn2an.an2cn(number_int)

                    end_word = target_number + paragraph[index + len(number)]
            except:
                pass
            
            if end_word:
                reach_end = True
                
                i += 1
                while i < len(paragraphs) and reach_end:
                    if end_word in paragraphs[i]:
                        reach_end = False
                        break
                    temp += [paragraphs[i]]
                    i += 1
                    
                if reach_end == False:
                    # add list 
                    for index, sentence in enumerate(temp):
                        if index == 0:
                            matched_paragraphs.append((sentence, re.search('|'.join(rule_3_keyword), sentence).group()))
                        else:
                            matched_paragraphs.append((sentence, "总则/指导思想/基本原则内容"))
                else:
                    temp = [paragraph]
                    next_index = paragraphs.index(paragraph) + 1
                    if next_index < len(paragraphs):
                        temp += [paragraphs[next_index]]
                        for index, sentence in enumerate(temp):
                            if index == 0:
                                matched_paragraphs.append((sentence, re.search('|'.join(rule_3_keyword), sentence).group()))
                            else:
                                matched_paragraphs.append((sentence, "总则/指导思想/基本原则内容"))
                    else:
                        matched_paragraphs.append((paragraph.strip(), [keyword for keyword in rule_3_keyword if keyword in paragraph][0]))
                    i = next_index
                    
            else:
                temp = [paragraph]
                next_index = paragraphs.index(paragraph) + 1
                if next_index < len(paragraphs):
                    temp += [paragraphs[next_index]]
                    for index, sentence in enumerate(temp):
                        if index == 0:
                            matched_paragraphs.append((sentence, re.search('|'.join(rule_3_keyword), sentence).group()))
                        else:
                            matched_paragraphs.append((sentence, "总则/指导思想/基本原则内容"))
                        
                else:
                    matched_paragraphs.append((paragraph.strip(), [keyword for keyword in rule_3_keyword if keyword in paragraph][0]))
                i = next_index
                
        i += 1
    
    if len(matched_paragraphs) == 0:
        # print("No matched information found, using default rule")
        # find the first sentence in docs that have \u3000\u3000
        for paragraph in paragraphs:
            if "\u3000\u3000" in paragraph:
                if len(paragraph) > 5:
                    matched_paragraphs.append((paragraph.strip(), "默认规则"))
                break
    
    matched_paragraphs_index = []
    for sentence in matched_paragraphs:
        begin_index = docs.find(sentence[0])
        end_index = begin_index + len(sentence[0])
        matched_paragraphs_index.append((begin_index, end_index))
        
    return matched_paragraphs, matched_paragraphs_index

def find_权宜处理_rule_base(docs,一般政策性内容):
    """Return the sentence that match 权宜处理 keywords using regular expression and fuzzy matching

    Returns:
        list of tuple: the all sentences that match 权宜处理 keywords and the matched keywords
        list of tuple: the index of the matched sentences in the original text and the matched keywords
    """
    # preprocess the 一般政策性内容 to remove any blank space
    一般政策性内容 = [re.sub(r'\s+', '', content) for content in 一般政策性内容]
    
    logging.getLogger().setLevel(logging.ERROR)
    
    # keywords for regular expression
    keywords = ["结合.*?实际", "根据.*?实际", "根据实际情况", "结合实际情况", "结合本地实际", "根据本地实际","因地制宜"]
    pattern = re.compile('|'.join(keywords))
    
    # keywords for fuzzy matching
    keywords_fuzzy = ["结合实际", "根据实际", "根据实际情况", "结合实际情况", "结合本地实际", "根据本地实际"]
    
    paragraphs = pre_process(docs)
    
    matched_paragraphs = []

    for paragraph in paragraphs:
        # remove any blank space before and after the paragraph
        check_paragraph = re.sub(r'\s+', '', paragraph)
        if check_paragraph in 一般政策性内容:
            continue
        elif pattern.search(paragraph):
            matched_paragraphs.append((paragraph.strip(), pattern.search(paragraph).group()))
        else:
            best_match = process.extractOne(paragraph, keywords_fuzzy)
            if best_match[1] >= 60:  
                matched_paragraphs.append((paragraph.strip(), best_match[0]))

    matched_paragraphs_index = []
    for sentence in matched_paragraphs:
        begin_index = docs.find(sentence[0])
        end_index = begin_index + len(sentence[0])
        matched_paragraphs_index.append((begin_index, end_index))
        
    return matched_paragraphs, matched_paragraphs_index

def find_执行过程规定_rule_base(docs,一般政策语言):
    """Return the sentence that match 执行过程规定 keywords using regular expression and fuzzy matching

    Returns:
        list of tuple: the begin and end sentences that match 执行过程规定 keywords and the matched keywords
        list of tuple: the index of the matched sentences in the original text
        list of string: the content that within the begin and end sentences
        int: the first index of the matched content
        int: the last index of the matched content
    """
    一般政策语言 = [re.sub(r'\s+', '', content) for content in 一般政策语言]
    
    logging.getLogger().setLevel(logging.ERROR)
    
    keywords =["(以|用|通过).*?(的方式|方法)","由.*?(主要负责|负责)","流程","程序","执行","分工","牵头","责任","措施","个阶段","进度"]
    pattern = re.compile('|'.join(keywords))
    
    # keywords_fuzzy = ["流程","程序","执行","分工","牵头","责任","措施","个阶段","进度"]
    
    paragraphs = pre_process(docs)
    matched_paragraphs = set()
    
    for paragraph in paragraphs:
        check_paragraph = re.sub(r'\s+', '', paragraph)
        if check_paragraph in 一般政策语言:
            continue
        if pattern.search(paragraph):
            matched_paragraphs.add((paragraph.strip(), pattern.search(paragraph).group()))
        # else:
        #     best_match = process.extractOne(paragraph, keywords_fuzzy)
        #     if best_match[1] >= 60:
        #         matched_paragraphs.add((paragraph.strip(), best_match[0]))
                
    # find the first and the last index of the matched paragraph
    first_index = 1000000
    last_index = 0
    matched_paragraphs_index = []
    for sentence in matched_paragraphs:
        begin_index = docs.find(sentence[0])
        end_index = begin_index + len(sentence[0])
        matched_paragraphs_index.append((begin_index, end_index))
        first_index = min(first_index, begin_index)
        last_index = max(last_index, end_index)
        
    # include all content within the first and the last index
    content = docs[first_index:last_index]
    content = pre_process(content)
    for paragraph in content:
        check_paragraph = re.sub(r'\s+', '', paragraph)
        if check_paragraph in 一般政策语言:
            content.remove(paragraph)
        
    if last_index - first_index < 100 or len(matched_paragraphs) == 0 or last_index - first_index > 0.7 * len(docs):
        return [], [], [], 0, 0, 0
    else:
        return list(matched_paragraphs), matched_paragraphs_index, content, first_index, last_index, last_index - first_index
 
def find_设置特定目标_rule_base(docs, 一般政策语言):
    一般政策语言 = [re.sub(r'\s+', '', content) for content in 一般政策语言]
    
    logging.getLogger().setLevel(logging.ERROR)
    
    keywords = [
        "(?:^|,)\s*第.*?(章|节|点|条).*?(目标|工作目标|工作重点|发展目标|明确目标|重点目标|重要目标|目标任务|任务|重点任务|主要任务|具体要求|工作要求|主要要求)"
    ]
    rule_1_pattern = re.compile('|'.join(keywords))
    
    # rule_2_keyword_fuzzy = ["总则"]
    
    # rule_3_keyword_fuzzy = ["实现","达到","解决","确保","保证","保障"]
    rule_3_pattern = ["推动.*?目标", "在.*?方面实行", "总则","实现","达到","解决","确保","保证","保障"]
    rule_3_pattern = re.compile('|'.join(rule_3_pattern))
    
    paragraphs = pre_process_without_n(docs)
    matched_paragraphs = []
    for paragraph in paragraphs:
        if any(sentence in paragraph for sentence in 一般政策语言):
            continue
        if rule_1_pattern.search(paragraph):
            matched_paragraphs.append((paragraph.strip(), rule_1_pattern.search(paragraph).group()))
        # elif any(keyword in paragraph for keyword in rule_2_keyword_fuzzy):
        #     matched_paragraphs.add((paragraph.strip(), [keyword for keyword in rule_2_keyword_fuzzy if keyword in paragraph][0]))
        elif rule_3_pattern.search(paragraph):
            matched_paragraphs.append((paragraph.strip(), rule_3_pattern.search(paragraph).group()))
        # else:
        #     best_match = process.extractOne(paragraph, rule_3_keyword_fuzzy)
        #     if best_match[1] >= 60:
        #         matched_paragraphs.add((paragraph.strip(), best_match[0]))
                
    matched_paragraphs_index = []
    for sentence in matched_paragraphs:
        begin_index = docs.find(sentence[0])
        end_index = begin_index + len(sentence[0])
        matched_paragraphs_index.append((begin_index, end_index))
        
    return matched_paragraphs, matched_paragraphs_index

def find_设置特定期限_rule_base(docs):
    logging.getLogger().setLevel(logging.ERROR)
    
    keywords = [
        "(?:^|,)\s*本办法自.*?有效期",
        "(在|于)(年|月|日)前",
        "(至|到).*?(年|月|日)为止",
        "为期","巡查时期","时间进度","个工作日内","个月内","年内"
    ]
    
    pattern = re.compile('|'.join(keywords))
    paragraphs = pre_process(docs)
    matched_paragraphs = []
    
    for paragraph in paragraphs:
        if pattern.search(paragraph):
            matched_paragraphs.append((paragraph.strip(), pattern.search(paragraph).group()))
        else:
            continue
        
    matched_paragraphs_index = []
    for sentence in matched_paragraphs:
        begin_index = docs.find(sentence[0])
        end_index = begin_index + len(sentence[0])
        matched_paragraphs_index.append((begin_index, end_index))
        
    return matched_paragraphs, matched_paragraphs_index

def find_评估标准_rule_base(docs):
    logging.getLogger().setLevel(logging.ERROR)
    
    keywords = [
        "自评","巡查","监督","检查","追究","考核"
    ]
    pattern = re.compile('|'.join(keywords))
    
    keywords_fuzzy = ["责任追究","尽职免责","领导巡查","提交报告"]
    
    keywords_章节 = ["(?:^|,)\s*第.*?(章|节|点|条).*?(绩效检查|监督检查|监督管理|监督|绩效|评估|评价|考核|自评)"]
    pattern_章节 = re.compile('|'.join(keywords_章节))
    
    paragraphs = pre_process(docs)
    
    matched_paragraphs = []
    i = 0
    while i < len(paragraphs):
        paragraph = paragraphs[i]
        if pattern_章节.search(paragraph):
            temp = []
            temp += [paragraph]
            
            # number = ['1','2','3','4','5','6','7','8','9']
            number_pattern = re.compile(r'\d+')
            
            # number_chinese = ["一","二","三","四","五","六","七","八","九"]
            number_chinese_pattern = re.compile(r'(?:(?:[一二三四五六七八九]十)?[一二三四五六七八九]|十[一二三四五六七八九]?|二十|三十|四十|五十|六十|七十|八十|九十)')
            
            end_word = None
            try:
                if re.search(number_pattern, paragraph):
                    number = re.search(number_pattern, paragraph).group()
                    index = paragraph.index(number)

                    target_number = str(int(number) + 1)
                    target_number = str(target_number)

                    end_word = target_number + paragraph[index + len(number)]
                
                elif number_chinese_pattern.search(paragraph):
                    number = re.search(number_chinese_pattern, paragraph).group()
                    index = paragraph.index(number)

                    number_int = cn2an.cn2an(number)
                    number_int += 1
                    target_number = cn2an.an2cn(number_int)

                    end_word = target_number + paragraph[index + len(number)]
            except:
                pass
            
            if end_word:
                reach_end = True
                
                i += 1
                while i < len(paragraphs) and reach_end:
                    if end_word in paragraphs[i]:
                        reach_end = False
                        break
                    temp += [paragraphs[i]]
                    i += 1
                    
                if reach_end == False:
                    # add list
                    for index, sentence in enumerate(temp):
                        if index == 0:
                            matched_paragraphs.append((sentence, pattern_章节.search(paragraph).group()))
                        else:
                            matched_paragraphs.append((sentence, "章节/条款内容"))
                            
                else:
                    temp = [paragraph]
                    next_index = paragraphs.index(paragraph) + 1
                    if next_index < len(paragraphs):
                        temp += [paragraphs[next_index]]
                        for index, sentence in enumerate(temp):
                            if index == 0:
                                matched_paragraphs.append((sentence, pattern_章节.search(paragraph).group()))
                            else:
                                matched_paragraphs.append((sentence, "章节/条款内容"))
                    else:
                        matched_paragraphs.append((paragraph.strip(), pattern_章节.search(paragraph).group()))
                    i = next_index
                    
            else:
                temp = [paragraph]
                next_index = paragraphs.index(paragraph) + 1
                if next_index < len(paragraphs):
                    temp += [paragraphs[next_index]]
                    for index, sentence in enumerate(temp):
                        if index == 0:
                            matched_paragraphs.append((sentence, pattern_章节.search(paragraph).group()))
                        else:
                            matched_paragraphs.append((sentence, "章节/条款内容"))
                else:
                    matched_paragraphs.append((paragraph.strip(), pattern_章节.search(paragraph).group()))
                i = next_index
                
            matched_paragraphs[0] = (matched_paragraphs[0][0], pattern_章节.search(paragraph).group())
            
        elif pattern.search(paragraph):
            matched_paragraphs.append((paragraph.strip(), pattern.search(paragraph).group()))
        elif process.extractOne(paragraph, keywords_fuzzy)[1] >= 60:
                matched_paragraphs.append((paragraph.strip(), process.extractOne(paragraph, keywords_fuzzy)[0]))   
            
        i += 1
            
    matched_paragraphs_index = []
    for sentence in matched_paragraphs:
        begin_index = docs.find(sentence[0])
        end_index = begin_index + len(sentence[0])
        matched_paragraphs_index.append((begin_index, end_index))
        
    return matched_paragraphs, matched_paragraphs_index

def 评估标准详细度_summurize(评估标准):
    评估标准 = [p[0] for p in 评估标准]
    评估标准_str = "\n".join(评估标准)
    
    # load bert chinese model
    tokenizer = AutoTokenizer.from_pretrained("bert-base-chinese")
    model = AutoModelForMaskedLM.from_pretrained("bert-base-chinese")
    
    prompt = f"请根据以下内容用一个短语总结评估标准的详细度，例如：由上级负责解释，5条规定，提交报告等。以下是评估标准全文: {评估标准_str}"
    input_ids = tokenizer(prompt, return_tensors="pt")["input_ids"]
    output = model.generate(input_ids, max_length=20, num_return_sequences=1, no_repeat_ngram_size=2, temperature=0.1)
    return tokenizer.decode(output[0], skip_special_tokens=True)
    
def find_向上级反映_rule_base(docs):
    logging.getLogger().setLevel(logging.ERROR)
    
    keywords_章节 = ["(请径向|请向|向).*?(反映|反馈|报告|通报)"]
    pattern = re.compile('|'.join(keywords_章节))
    
    paragraphs = pre_process(docs)
    matched_paragraphs = []
    
    for paragraph in paragraphs:
        if pattern.search(paragraph):
            matched_paragraphs.append((paragraph.strip(), pattern.search(paragraph).group()))
        else:
            continue
    
    matched_paragraphs_index = []
    for sentence in matched_paragraphs:
        begin_index = docs.find(sentence[0])
        end_index = begin_index + len(sentence[0])
        matched_paragraphs_index.append((begin_index, end_index))
        
    return matched_paragraphs, matched_paragraphs_index    
    
