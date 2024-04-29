from extraction import find_政策内容_rule_base, find_权宜处理_rule_base, find_执行过程规定_rule_base, find_一般政策语言_rule_base, find_设置特定目标_rule_base, find_设置特定期限_rule_base, find_评估标准_rule_base, find_向上级反映_rule_base

import os
import pandas as pd
import time
import sqlite3

def extract_rule_base(path_to_txt, path_to_db, need_meta = False, all_doc = False):
    result_df = pd.DataFrame()
    
    db = path_to_db
    conn = sqlite3.connect(db)
    
    # create search index for db
    c = conn.cursor()
    c.execute("CREATE INDEX idx_category_filename ON category (filename);")
    
    files = os.listdir(path_to_txt)
    for i, file in enumerate(files):
        if not file.endswith(".txt"):
            print(f"Skip {i+1}/{len(files)}: {file}")
            continue
        
        print(f"Processing {i+1}/{len(files)}: {file}")
        docs = open(os.path.join(path_to_txt, file), 'r',errors='ignore').read()
        
        result_df.loc[i, '文件名称'] = str(file)
        result_df.loc[i, '字数'] = len(docs)
        
        try:
            sql = f"SELECT id, filename, dt FROM category WHERE filename = '{file}' "
            df_sql = pd.read_sql_query(sql, conn)
            if len(df_sql) == 0:
                result_df.loc[i, '法宝引证码'] = None
                result_df.loc[i, '颁布时间'] = None
            else:
                法宝引证码 = df_sql["id"][0]
                颁布时间 = df_sql["dt"][0]
                result_df.loc[i, '法宝引证码'] = str(法宝引证码)
                result_df.loc[i, '颁布时间'] = str(颁布时间)
            
        except:
            result_df.loc[i, '法宝引证码'] = None
            result_df.loc[i, '颁布时间'] = None
            
        政策内容 = find_政策内容_rule_base(docs)
        result_df.loc[i, '文件具体政策内容'] = 政策内容
        
        
        matched_paragraphs_一般政策语言, matched_paragraphs_index = find_一般政策语言_rule_base(docs)
        一般政策语言_list = []
        一般政策语言_提取原因_list = []
        for 一般政策语言, 一般政策语言_提取原因 in matched_paragraphs_一般政策语言:
            一般政策语言_list += [一般政策语言]
            一般政策语言_提取原因_list += [一般政策语言_提取原因]
        
        if need_meta:
            result_df.loc[i, '一般政策语言'] = "\n".join(一般政策语言_list)
            result_df.loc[i, '一般政策语言_提取原因'] = "\n".join(一般政策语言_提取原因_list)
        result_df.loc[i, '一般政策语言字数'] = len("".join(一般政策语言_list))
        
        
        matched_paragraphs_执行过程规定, matched_paragraphs_index = find_执行过程规定_rule_base(docs, 一般政策语言_list)
        执行过程规定_list = []
        执行过程规定_提取原因_list = []
        for 执行过程规定, 执行过程规定_提取原因 in matched_paragraphs_执行过程规定:
            执行过程规定_list += [执行过程规定]
            执行过程规定_提取原因_list += [执行过程规定_提取原因]
        
        执行过程规定字数 = len("".join(执行过程规定_list))
        if need_meta:
            result_df.loc[i, '执行过程规定'] = "\n".join(执行过程规定_list)
            result_df.loc[i, '执行过程规定_提取原因'] = "\n".join(执行过程规定_提取原因_list)
        if 执行过程规定字数 <= 2 :
            result_df.loc[i, '对执行过程有规定'] = "否"
            result_df.loc[i, '执行过程规定字数'] = 0
        else:
            result_df.loc[i, '对执行过程有规定'] = "是"
            result_df.loc[i, '执行过程规定字数'] = 执行过程规定字数

        
        matched_paragraphs_权宜处理, matched_paragraphs_index = find_权宜处理_rule_base(docs, 一般政策语言_list)
        权宜处理_list = []
        权宜处理_提取原因_list = []
        for 权宜处理, 权宜处理_提取原因 in matched_paragraphs_权宜处理:
            权宜处理_list += [权宜处理]
            权宜处理_提取原因_list += [权宜处理_提取原因]
        
        if need_meta:
            result_df.loc[i, '权宜处理'] = "\n".join(权宜处理_list)
            result_df.loc[i, '权宜处理_提取原因'] = "\n".join(权宜处理_提取原因_list)
        if len("".join(权宜处理_list)) <= 2:
            result_df.loc[i, '建议权宜处理'] = "否"
        else:
            result_df.loc[i, '建议权宜处理'] = "是"
        
        
        matched_paragraphs_设置特定目标, matched_paragraphs_index = find_设置特定目标_rule_base(docs, 一般政策语言_list)
        设置特定目标_list = []
        设置特定目标_提取原因_list = []
        for 设置特定目标, 设置特定目标_提取原因 in matched_paragraphs_设置特定目标:
            设置特定目标_list += [设置特定目标]
            设置特定目标_提取原因_list += [设置特定目标_提取原因]
        if need_meta:
            result_df.loc[i, '设置特定目标'] = "\n".join(设置特定目标_list)
            result_df.loc[i, '设置特定目标_提取原因'] = "\n".join(设置特定目标_提取原因_list)
        if len("".join(设置特定目标_list)) <= 2:
            result_df.loc[i, '是否设置特定目标'] = "否"
        else:
            result_df.loc[i, '是否设置特定目标'] = "是"
        
        
        matched_paragraphs_设置特定期限, matched_paragraphs_index = find_设置特定期限_rule_base(docs)
        设置特定期限_list = []
        设置特定期限_提取原因_list = []
        for 设置特定期限, 设置特定期限_提取原因 in matched_paragraphs_设置特定期限:
            设置特定期限_list += [设置特定期限]
            设置特定期限_提取原因_list += [设置特定期限_提取原因]
        if need_meta:
            result_df.loc[i, '设置特定期限'] = "\n".join(设置特定期限_list)
            result_df.loc[i, '设置特定期限_提取原因'] = "\n".join(设置特定期限_提取原因_list)
        if len("".join(设置特定期限_list)) <= 2:
            result_df.loc[i, '是否为政策执行设置特定期限'] = "否"
        else:
            result_df.loc[i, '是否为政策执行设置特定期限'] = "是"
        
        
        matched_paragraphs_评估标准, matched_paragraphs_index = find_评估标准_rule_base(docs)
        评估标准_list = []
        评估标准_提取原因_list = []
        for 评估标准, 评估标准_提取原因 in matched_paragraphs_评估标准:
            评估标准_list += [评估标准]
            评估标准_提取原因_list += [评估标准_提取原因]
        if need_meta:
            result_df.loc[i, '评估标准'] = "\n".join(评估标准_list)
            result_df.loc[i, '评估标准_提取原因'] = "\n".join(评估标准_提取原因_list)
        评估标准字数 = len("".join(评估标准_list))
        if 评估标准字数 <= 2:
            result_df.loc[i, '政策执行设置任务检测的评估标准字数'] = 0
            result_df.loc[i, '是否为政策执行设置任务检测的评估标准'] = "否"
            
        else:
            result_df.loc[i, '政策执行设置任务检测的评估标准字数'] = 评估标准字数
            result_df.loc[i, '是否为政策执行设置任务检测的评估标准'] = "是"  
        
        
        matched_paragraphs_向上级反映, matched_paragraphs_index = find_向上级反映_rule_base(docs)
        向上级反馈_list = []
        向上级反馈_提取原因_list = []
        for 向上级反馈, 向上级反馈_提取原因 in matched_paragraphs_向上级反映:
            向上级反馈_list += [向上级反馈]
            向上级反馈_提取原因_list += [向上级反馈_提取原因]
        if need_meta:
            result_df.loc[i, '向上级反馈'] = "\n".join(向上级反馈_list)
            result_df.loc[i, '向上级反馈_提取原因'] = "\n".join(向上级反馈_提取原因_list)
        if len("".join(向上级反馈_list)) <= 2:
            result_df.loc[i, '是否向上级反馈'] = "否"
        else:
            result_df.loc[i, '是否向上级反馈'] = "是"  
            
          
    return result_df
       
if __name__ == "__main__":
    print("Start extracting rule base...")
    begin = time.time()
    path_to_txt = "sample"
    path_to_db = "policies_all.db"
    result = extract_rule_base(path_to_txt, path_to_db, need_meta = True)
    end_time = time.time()
    print("Finish extracting rule base...")
    print("Time used per policy: ", (end_time - begin)/len(result))
    # save the result as csv
    result.to_csv("run_batch_results.csv", index=False)