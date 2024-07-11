from extraction import find_权宜处理_rule_base, find_执行过程规定_rule_base, find_一般政策语言_rule_base, find_设置特定目标_rule_base, find_设置特定期限_rule_base, find_评估标准_rule_base, find_向上级反映_rule_base

import os
import pandas as pd
import time

def generate_test_data():
    data_path = "../src/data/text_data.parquet"
    df = pd.read_parquet(data_path)
    
    # sample data every 2000 rows
    df = df.iloc[::2000, :]
    
    # use encoding='utf-8' 
    df['content'] = df['content'].apply(lambda x: x.decode('utf-8'))
    df.reset_index(drop=True, inplace=True)
    return df

def extract_rule_base(df):
    for i in range(len(df)):
        docs = df.loc[i, 'content']
        
        matched_paragraphs_一般政策语言, matched_paragraphs_index = find_一般政策语言_rule_base(docs)
        一般政策语言_list = []
        一般政策语言_提取原因_list = []
        for 一般政策语言, 一般政策语言_提取原因 in matched_paragraphs_一般政策语言:
            一般政策语言_list += [一般政策语言]
            一般政策语言_提取原因_list += [一般政策语言_提取原因]
        df.loc[i, '一般政策语言'] = "\n".join(一般政策语言_list)
        df.loc[i, '一般政策语言_提取原因'] = "\n".join(一般政策语言_提取原因_list)
        
        matched_paragraphs_权宜处理, matched_paragraphs_index = find_权宜处理_rule_base(docs, 一般政策语言_list)
        权宜处理_list = []
        权宜处理_提取原因_list = []
        for 权宜处理, 权宜处理_提取原因 in matched_paragraphs_权宜处理:
            权宜处理_list += [权宜处理]
            权宜处理_提取原因_list += [权宜处理_提取原因]
        df.loc[i, '权宜处理'] = "\n".join(权宜处理_list)
        df.loc[i, '权宜处理_提取原因'] = "\n".join(权宜处理_提取原因_list)
        
        matched_paragraphs_执行过程规定, matched_paragraphs_index = find_执行过程规定_rule_base(docs, 一般政策语言_list)
        执行过程规定_list = []
        执行过程规定_提取原因_list = []
        for 执行过程规定, 执行过程规定_提取原因 in matched_paragraphs_执行过程规定:
            执行过程规定_list += [执行过程规定]
            执行过程规定_提取原因_list += [执行过程规定_提取原因]
        df.loc[i, '执行过程规定'] = "\n".join(执行过程规定_list)
        df.loc[i, '执行过程规定_提取原因'] = "\n".join(执行过程规定_提取原因_list)
        
        matched_paragraphs_设置特定目标, matched_paragraphs_index = find_设置特定目标_rule_base(docs, 一般政策语言_list)
        设置特定目标_list = []
        设置特定目标_提取原因_list = []
        for 设置特定目标, 设置特定目标_提取原因 in matched_paragraphs_设置特定目标:
            设置特定目标_list += [设置特定目标]
            设置特定目标_提取原因_list += [设置特定目标_提取原因]
        df.loc[i, '设置特定目标'] = "\n".join(设置特定目标_list)
        df.loc[i, '设置特定目标_提取原因'] = "\n".join(设置特定目标_提取原因_list)
        
        matched_paragraphs_设置特定期限, matched_paragraphs_index = find_设置特定期限_rule_base(docs)
        设置特定期限_list = []
        设置特定期限_提取原因_list = []
        for 设置特定期限, 设置特定期限_提取原因 in matched_paragraphs_设置特定期限:
            设置特定期限_list += [设置特定期限]
            设置特定期限_提取原因_list += [设置特定期限_提取原因]
        df.loc[i, '设置特定期限'] = "\n".join(设置特定期限_list)
        df.loc[i, '设置特定期限_提取原因'] = "\n".join(设置特定期限_提取原因_list)
        
        matched_paragraphs_评估标准, matched_paragraphs_index = find_评估标准_rule_base(docs)
        评估标准_list = []
        评估标准_提取原因_list = []
        for 评估标准, 评估标准_提取原因 in matched_paragraphs_评估标准:
            评估标准_list += [评估标准]
            评估标准_提取原因_list += [评估标准_提取原因]
        df.loc[i, '评估标准'] = "\n".join(评估标准_list)
        df.loc[i, '评估标准_提取原因'] = "\n".join(评估标准_提取原因_list)
        
        matched_paragraphs_向上级反映, matched_paragraphs_index = find_向上级反映_rule_base(docs)
        向上级反馈_list = []
        向上级反馈_提取原因_list = []
        for 向上级反馈, 向上级反馈_提取原因 in matched_paragraphs_向上级反映:
            向上级反馈_list += [向上级反馈]
            向上级反馈_提取原因_list += [向上级反馈_提取原因]
        df.loc[i, '向上级反馈'] = "\n".join(向上级反馈_list)
        df.loc[i, '向上级反馈_提取原因'] = "\n".join(向上级反馈_提取原因_list)
          
    return df
       
if __name__ == "__main__":
    
    df = generate_test_data()
    print("Start extracting rule base...")
    begin = time.time()
    result = extract_rule_base(df)
    end_time = time.time()
    print("Finish extracting rule base...")
    print("Time used per policy: ", (end_time - begin)/len(result))
    # save the result as csv
    result.to_csv("test_results.csv", index=False)
    
