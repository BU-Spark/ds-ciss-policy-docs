import os
import pandas as pd
import shutil
import zipfile
from pathlib import Path
import textract
import urllib.parse


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
                                else:
                                    os.remove(extracted_path.name.encode('cp437').decode('gbk'))
                            except:
                                # move the file to the unzip folder, base on the original file name
                                if not os.path.exists(os.path.join(unzip_folder_path, fn)):
                                    shutil.move(extracted_path.name, os.path.join(unzip_folder_path, fn))
                                else:
                                    os.remove(extracted_path.name)
                except:
                    print("Error: ", os.path.join(root, file))
                    print("Error: ", os.path.join(root, file))      
            else:
                # move the file to the unzip folder
                if not os.path.exists(os.path.join(unzip_folder_path, file)):
                    shutil.copy(os.path.join(root, file), unzip_folder_path)
            
def read_data(root, output_dir):
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
            print(f"finish {count} files")
            count += 1
            
    # save the data
    file_name = output_dir
    df.to_parquet(file_name, index=False)
    return df   

def data_pipeline(raw_file_roots, output_dir):
    for raw_file_root in raw_file_roots:
        process_file(raw_file_root)
        unzip_file(raw_file_root + "/all_files", "data/all_documents")
        print("Finish processing ", raw_file_root)
    
    # read_data("data/all_documents", output_dir)

def main():
    raw_file_root1 = "data/Regulatory Statute Documents Set 1"
    #raw_file_root2 = "data/Regulatory Statute Documents Set 2"
    #raw_file_root3 = "data/Regulatory Statute Documents Set 3"
    output_dir = "data/text_data.parquet"
    
    data_pipeline([raw_file_root1], output_dir)

if __name__ == "__main__":
    main()
    