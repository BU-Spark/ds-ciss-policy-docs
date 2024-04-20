# Task B - Policy Category


## About
This folder servers the task-b of the CISS Policy Document project, where the category label is missing from the original data set. After examining the data, we figured that the labels needed by the clients can be mapped from the labels from the original website. 

We have developed some scripts to pull the labels from the original website, and hopefully can be mapped to the category label (given the mapping relationship from the clients). We utilized Sqlite3 (an embedded database) to store working data and pulled lebels. The idea is to have one table to keep track of every data folder that contains policy documents, and another table to store the meta data as well as the collected labels. 


## File Structure
```
task-b/
  ├─ collect/
  |  ├─ app-x.js
  |  ├─ csv2sqlite.js
  |  ├─ data_check.js
  |  ├─ data_check.out
  |  ├─ manage.js
  |  ├─ package-lock.json
  |  ├─ package.json
  |  └─ test.js
  ├─ map_labels.py
  ├─ mapping.csv
  ├─ readme.md
  └─ test-0.ipynb
```
- [collect/app-x.js](collect/app-0.js) is the worker threads that pull labels from the website. 
- [collect/csv2sqlite.js](collect/csv2sqlite.js) can be ignored; it was used in the early stage to store everything in a csv file into a sqlite database. 
- [collect/data_check.js](collect/data_check.js) is a script to check the data quality after pulling. Try `node data_check.js` to see the usage. 
- [collect/data_check.out](collect/data_check.out) is the result of the latest quality checking. It shows the number of missing values overall and the number of those in each region. 
- [collect/manage.js](collect/manage.js) is the controller that add/remove tasks into/from the database. Each folder with format `region/year/` correspondes to a task in the database. Run `node manage.js` to see the usage. 
- [collect/package-lock.json](collect/package-lock.json) and [collect/package.json](collect/package.json) stores the meta data and dependencies of a nodejs project. 
- [map_labels.py](map_labels.py) is the script to map original labels to clients' labels. See [Map from Original Labels...](#map-from-original-labels-to-clients-labels) section for more details. 
- [mapping.csv](mapping.csv) stores the latest mapping relationship used to map the original labels into L1 and L2 labels. 
- [test-0.ipynb](test-0.ipynb) shows some experiments with mapping labels. 
- [utils.py](utils.py) contains some tools to work with the large dataset. See [Work with CSV Files](#work-with-csv-files) section for more details. 



## Collect Label from the Original Website
1.  Add a config file as `collect/config.js` with the following format:

        module.exports = {
            proxyIp: 'rotating_proxy_ip',
            proxyPort: rotating_proxy_port,
        };
2.  Install dependiencies in `collect/` directory (requires nodejs environment). 

        npm install

3.  Use [collect/manage.js](collect/manage.js) to add tasks for specific folders. 
4.  Run `app-x.js` to start collecting data. The program will log the current progress every ~20 minutes. 


## Map from Original Labels to Clients' Labels
1.  Install dependiencies (requires python environment):

        pip install pandas
2.  Make sure you have `policies_all.csv` in `task-b/` directory. 
3.  Run `map_labels.py`. It will generate `policies_label.csv` and `policies_noMap.csv`, where the former contains all mapped labels and the latter contains the records that cannot be mapped. 


## Work with CSV Files
1.  Install dependiencies (requires python environment):

        pip install pandas pypinyin
2.  Run `utils.py` to see usage. Some examples:

        python utils.py csv region 陕西
        python utils.py csv region XiAn
        python utils.py csv region beijing
        python utils.py csv type 高等教育
        python utils.py csv l2 农业


## Useful Commands
To start or continue collecting labels on the background:
```
nohup node task-b/collect/app-0.js >> collect-0.log 2>&1 &
nohup node task-b/collect/app-1.js >> collect-1.log 2>&1 &
```
