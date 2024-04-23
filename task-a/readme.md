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
task-a/
  ├─ extraction.py
  ├─ run_test.py
  ├─ utils.py
  ├─ readme.md
  ├─ requirements.txt
  └─ test.ipynb
```
- [extraction.py] is the main file that contains the functions to extract the information from the policy documents.
- [run_test.py] is the file that generate the sample test result and store the result in a csv file. csv file will contain the extracted information and the corresponding reasons.
- [sample.py](sample.py) is used to take a subset of documents and store them into the `sample/` folder. Run `python sample.py` to see usage.
- [test-1.ipynb] is the jupyter notebook that can run test on function seperately.
- [utils.py] is the file that contains the helper functions.

## Useful Commands
To start the test, run the following command:
```
python run_test.py
```
