# Task A - Information Extraction

## About
This folder servers the task-a of the CISS Policy Document project, where we need to extract the specific information from the policy documents. 

We have finished the first and second batch of extraction, which are: 文件具体政策内容，一般政策语言，对政策执行过程有规定，建议权宜处理，是否设置特定目标，是否为政策执行设置特定期限，是否为政策执行设置任务检测的评估标准。(法宝引证码 and 颁布时间 are extracted in the task-b).

We also provide get_answer_RegQA() through GPT3.5 to extract the information that is extremely difficult to extract using traditional methods.

## Getting Started
Install dependiencies (please cd to task-a folder). 
```
pip install -r requirements.txt
```

## File Structure
```
repo/
    ├─ data
    ├─ task-a/
        ├─ sample/
        │  ├─ doc1.txt
        │  ├─ doc2.txt
        │  ├─ ...
        ├─ notebook/
        │  ├─ col_7_一般政策语言.ipynb
        │  ├─ col_16_对政策执行过程有规范.ipynb
        │  ├─ ...
        ├─ extraction.py
        ├─ sample.py
        ├─ batch_process.py
        ├─ utils.py
        ├─ readme.md
        └─ requirements.txt
      

```
- [data] folder contains the policy documents that we generate using sample.py.

- [notebook] folder contains a set of Jupyter notebooks that demonstrate how to extract information for individual features. Each notebook is named in the format: col_{feature_number}_{feature_name}.ipynb, where feature_number is the number of the feature, and feature_name is the name of the information to be extracted. Please refer to the end of this file (Link To Metadata) for the index number of each feature. For example, col_7_一般政策语言.ipynb is the notebook that illustrates how to extract information for the feature "col_7_一般政策语言". This notebook includes:
  1. The logic function that extracts information for the feature "col_7_一般政策语言";
  2. Visualization of the extracted information;
  3. A batch process to extract "col_7_一般政策语言" for all documents in the sample folder and provide relevant quantitative analysis.

- [extraction.py] is the main file containing all logic functions for extracting information from the policy documents.

- [sample.py] is used to select a subset of documents and store them in the sample/ folder. Run python sample.py to see its usage.

- [batch_process.py] is the file that implements the batch process to extract all features for all documents in the sample folder and outputs the results to a CSV file.

- [utils.py] is the file containing the helper functions.

## Useful Commands
To start the test, run the following command:
```
python run_test.py
```

We can run batch_process.py on either the sample data or the full data. Please download db file from google drive.
```
python batch_process.py path_to_txt path_to_db --need_meta --all_doc
e.g. python batch_process.py ../data/ policies_all.db --need_meta True --all_doc True
```
[--need_meta] is a flag to indicate whether we need to extract metadata, include the extraction texts and corresponding reasons, from the policy documents. The default value is False.

[--all_doc] is a flag to indicate whether we need to process all documents in the directory. The default value is False. If the flag is set to False, the program will only process the files in sample folder. If the flag is set to True, the program will process all files within the data directory.

To get more information for batch_process.py, please run the following command:
```
python batch_process.py -h

Extract policy information from text files.

positional arguments:
  path_to_txt           Path to the text file directory
  path_to_db            Path to the database file

optional arguments:
  -h, --help            show this help message and exit
  --need_meta NEED_META
                        Need metadata (default: False)
  --all_doc ALL_DOC     Process all documents (default: False)
```




## The Link to Metadata 
The metadata of the features can be found in the following link: [metadata](https://docs.google.com/spreadsheets/d/1BA7K6bCfNOyvs4MbpB6oiBA6FUjiYcIdMXY926yEIw8/edit?usp=sharing)