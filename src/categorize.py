import pandas as pd
import numpy as np
import os
import math

def read_csv_data(path_to_file):
    '''
    input: path to csv file
    return panda dataframe of raw categories
    '''
    if not os.path.exists(path_to_file):
        raise FileNotFoundError(f"File not found: {path_to_file}")
    df = pd.read_csv(path_to_file)
    
    # remove all "(number)"" from the column values
    df = df.replace(to_replace= r"\s\(.*\)", value='', regex=True)
    df = df.replace(to_replace= "\n", value=' ', regex=True)
    # drop all nan columns
    df = df.dropna(axis=1, how='all')
    
    return df

def calcualate_unique_categories(df):
    '''
    Check any dupilcate categories in column that retrive from website
    input: pandas dataframe
    return panda dataframe with unique categories of each level, and the list of duplicates
    '''
    
    # get unique categories for each column except the null values
    all_categories = []
    for col in df.columns:
        if not "法规类别自带分类" in col:
            all_categories.append([])
            continue
        
        unique_category_level = df[col].unique()
        # remove nan from unique_category_level
        unique_category_level = [x for x in unique_category_level if str(x) != 'nan']
        all_categories.append(unique_category_level)
    
    # check for duplicates for all_categories
    duplicates = {}
    report = {}
    return_categories = []
    for i, cat_each_level in enumerate(all_categories):
        if cat_each_level == []:
            continue
        for cat in cat_each_level:
            if cat not in duplicates:
                duplicates[cat] = (1, i)
            else:
                report[cat] = f"Duplicate category found in column: {i} and column: {duplicates[cat][1]}"
                duplicates[cat] = (duplicates[cat][0]+1, i)
        return_categories.append(cat_each_level)
                
    return return_categories, report

def calulate_level_from_label(df_ori, label):
    '''
    input: panda dataframe of all categories
    input: label to search
    
    return: L1, L2, L3, L4
    L1 and L2 are from the raw categories
    L3 and L4 are retrived from the website
    L3 and L4 may be None if not found
    '''
    columns_check = df_ori.columns.str.contains("法规类别自带分类")
    df = df_ori.loc[:, columns_check]
    
    # check from right to left
    for i in range(df.shape[1]-1, -1, -1):
        if label in df.iloc[:, i].values:
            # get row index
            row_index = df.iloc[:, i].values.tolist().index(label)
            col_index = i
            L1 = df_ori["Raw categorized L1"].iloc[row_index]
            L2 = df_ori["Raw categorized L2"].iloc[row_index]
            
            # check column name
            col_name = df.columns[col_index]
            if col_name == "法规类别自带分类L4":
                L4 = df["法规类别自带分类L4"].iloc[row_index]
                while(type(df["法规类别自带分类L3"].iloc[row_index]) == float):
                    row_index -= 1
                L3 = df["法规类别自带分类L3"].iloc[row_index]
                return L1, L2, L3, L4
            
            if col_name == "法规类别自带分类L3":
                L3 = df["法规类别自带分类L3"].iloc[row_index]
                return L1, L2, L3, None
            
            else:
                return L1, L2, None, None
    raise ValueError(f"Label: {label} not found in all categories")
    
                