import os
import pandas as pd
import shutil
import zipfile
from pathlib import Path

def unzip_file(zip_folder_path, unzip_folder_path):
    '''
    unzip all file under the folder
    '''
    if not os.path.exists(unzip_folder_path):
        os.makedirs(unzip_folder_path, exist_ok=True)
    
    for root, dirs, files in os.walk(zip_folder_path):
        for file in files:
            if file.endswith('.zip'):
                # unzip the file
                with zipfile.ZipFile(os.path.join(root, file), 'r') as zip_ref:
                    for fn in zip_ref.namelist():
                        extracted_path = Path(zip_ref.extract(fn))
                        extracted_path.rename(fn.encode('cp437').decode('gbk'))
                        # move the file to the unzip folder, base on the new file name
                        if not os.path.exists(os.path.join(unzip_folder_path, fn.encode('cp437').decode('gbk'))):
                            shutil.move(extracted_path.name.encode('cp437').decode('gbk'), os.path.join(unzip_folder_path, fn.encode('cp437').decode('gbk')))
                        else:
                            os.remove(extracted_path.name.encode('cp437').decode('gbk'))      

def process_file(root_path):
    '''
    unfold all the folders under root and store the file in new folder
    '''
    # create a new folder to store the files under the root_path
    if not os.path.exists(os.path.join(root_path, 'all_files')):
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
                
def read_data(root):
    '''
    read all text file under the root, and save as praque format
    '''
    df = pd.DataFrame(columns=['file_name', 'content'])
    
    # read the data
    for root, dirs, files in os.walk(root):
        for file in files:
            if file.endswith('.txt'):
                # read the file name
                file_name = file.split('.')[0]
                content = open(os.path.join(root, file), 'r', encoding='utf-8').read()
                df.loc[len(df.index)] = [file_name, content]
    # save the data
    file_name = 'data/all_files.parquet'
    df.to_parquet(file_name, index=False)
    return df   

def main():
    raw_file_root = "data/Regulatory Statute Documents Set 3"
    process_file(raw_file_root)
    unzip_file("data/Regulatory Statute Documents Set 3/all_files", "data/all_documents")
    read_data("data/all_documents")

if __name__ == "__main__":
    main()
    