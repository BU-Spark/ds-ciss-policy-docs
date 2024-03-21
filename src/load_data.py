import os
import pandas as pd
import shutil
import zipfile
from pathlib import Path
import textract
import sqlite3
from utils import encode_df
import pandas as pd


def process_file(root_path):
    '''
    unfold all the folders under root and store the file in new folder
    '''
    # create a new folder to store the files under the root_path
    if not os.path.exists(os.path.join(root_path, 'all_files')):
        os.makedirs(os.path.join(root_path, 'all_files'), exist_ok=True)
    else:
        # delete the folder and recreate it
        shutil.rmtree(os.path.join(root_path, 'all_files'))
        os.makedirs(os.path.join(root_path, 'all_files'), exist_ok=True)
        
    new_folder_path = os.path.join(root_path, 'all_files')
    
    # iterate all the folders and files under the root_path
    for root, dirs, files in os.walk(root_path):
        if root == new_folder_path:
            continue
        
        # iterate all files under the root
        for file in files:
            # if the file is a zip file
            if file.endswith('.zip'):
                # move the zip file to the new folder
                # check if the file is already in the new folder
                if not os.path.exists(os.path.join(new_folder_path, file)):
                    # copy the file to the new folder
                    shutil.copy(os.path.join(root, file), new_folder_path)
            # if the file is a text file
            elif file.endswith('.txt') or file.endswith('.doc') or file.endswith('.docx') or file.endswith('.pdf'):
                # move the text file to the new folder
                # check if the file is already in the new folder
                if not os.path.exists(os.path.join(new_folder_path, file)):
                    # copy the file to the new folder
                    shutil.copy(os.path.join(root, file), new_folder_path)
            else:
                continue
                
def unzip_file(zip_folder_path, unzip_folder_path):
    '''
    unzip all file under the folder
    '''
    if not os.path.exists(unzip_folder_path):
        os.makedirs(unzip_folder_path, exist_ok=True)
    
    count = 0
    
    for root, dirs, files in os.walk(zip_folder_path):
        for file in files:
            if file.endswith('.zip'):
                # unzip the file
                try:
                    with zipfile.ZipFile(os.path.join(root, file), 'r') as zip_ref:
                        for fn in zip_ref.namelist():
                            extracted_path = Path(zip_ref.extract(fn))
                            try:                                   
                                extracted_path.rename(fn.encode('cp437').decode('gbk'))
                                # move the file to the unzip folder, base on the new file name
                                if not os.path.exists(os.path.join(unzip_folder_path, fn.encode('cp437').decode('gbk'))):
                                    shutil.move(extracted_path.name.encode('cp437').decode('gbk'), os.path.join(unzip_folder_path, fn.encode('cp437').decode('gbk')))
                                    count += 1
                                else:
                                    os.remove(extracted_path.name.encode('cp437').decode('gbk'))
                                
                            except:
                                # move the file to the unzip folder, base on the original file name
                                if not os.path.exists(os.path.join(unzip_folder_path, fn)):
                                    shutil.move(extracted_path.name, os.path.join(unzip_folder_path, fn))
                                    count += 1
                                else:
                                    os.remove(extracted_path.name)
                                
                except:
                    print("Error: ", os.path.join(root, file))     
                    # write the error file to a txt file
                    with open("data_error_log.txt", "a") as f:
                        f.write(os.path.join(root, file) + "\n")
            else:
                # move the file to the unzip folder
                if not os.path.exists(os.path.join(unzip_folder_path, file)):
                    shutil.copy(os.path.join(root, file), unzip_folder_path)
                count += 1
    
    print(f"Moving {count} files")
            
def read_data(root, output_dir = None):
    '''
    read all text file under the root, and save as praque format
    '''
    df = pd.DataFrame(columns=['file_name', 'content'])
    count = 0
    # read the data
    for root, dirs, files in os.walk(root):
        for file in files:
            if file.endswith('.txt'):
                # read the file name
                file_name = file.split('.')[0]
                content = open(os.path.join(root, file), 'r', encoding='utf-8').read()
                df.loc[len(df.index)] = [file_name, content]
            elif file.endswith('.doc') or file.endswith('.docx'):
                file_name = file.split('.')[0]
                # check existance of the file
                content = textract.process(os.path.join(root, file))
                df.loc[len(df.index)] = [file_name, content]
            count += 1
            if count % 10000 == 0:
                print("Finish reading ", count, " files")
            
    # save the data
    if output_dir is not None:
        file_name = output_dir
        # check if the file is already exist
        if os.path.exists(file_name):
            # delete the file
            os.remove(file_name)
        # save the data as parquet format use utf-8 encoding
        df.to_parquet(file_name, engine='pyarrow', index=False)
        print("Finish saving the data")
    
    return df   

def data_pipeline(raw_file_roots, output_dir):
    for raw_file_root in raw_file_roots:
        process_file(raw_file_root)
        unzip_file(raw_file_root + "/all_files", "data/all_documents")
        print("Finish processing ", raw_file_root)
    
    print("Finish processing all files")
    read_data("data/all_documents", output_dir)

def generate_label_data(df_path, db_path):
    '''
    read the parquet file (text) and db file (labels) and convert them into a single dataframe
    '''
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    res = cur.execute(" SELECT id, filename, type\
                    FROM category")
    df_label = pd.DataFrame(res.fetchall(), columns=['id', 'filename', 'type'])
    df_text = encode_df(pd.read_parquet(df_path, engine='pyarrow'),'content')
    
    id_list = []
    for index, text in enumerate(df_text['text']):
        try:
            id = 'CLI' + text.split('\n')[0].split('CLI')[1]
            id_list.append(id)
        except:
            id_list.append('None')
    df_text['id'] = id_list
    df_text_label = df_text.merge(df_label, on='id', how='inner')
    
    return df_text_label, df_text, df_label

def main():
    raw_file_root1 = "data/规范性文件1"
    raw_file_root2 = "data/规范性文件2"
    raw_file_root3 = "data/规范性文件3"
    output_dir = "data/text_data.parquet"
    
    data_pipeline([raw_file_root1, raw_file_root2, raw_file_root3], output_dir)

if __name__ == "__main__":
    main()
    