# Task B - Policy Category

## About
This folder servers the task-b of the CISS Policy Document project, where the category label is missing from the original data set. After examining the data, we figured that the labels needed by the clients can be mapped from the labels from the original website.  

We have developed some scripts to pull the labels from the original website, and hopefully can be mapped to the category label (given the mapping relationship from the clients). We utilized Sqlite3 (an embedded database) to store working data and pulled lebels. The idea is to have one table to keep track of every data folder that contains policy documents, and another table to store the meta data as well as the collected labels. 

## Getting Started
1.  Add a config file as `collect/config.js` with the following format:

        module.exports = {
            proxyIp: 'rotating_proxy_ip',
            proxyPort: rotating_proxy_port,
        };
2.  Install dependiencies in `collect/` directory. 

        npm install

3.  Use [collect/manage.js](collect/manage.js) to add tasks for specific folders. 
4.  Run `app-x.js` to start collecting data. The program will log the current progress every ~20 minutes. 

## File Structure
```
repo/task-b/
  ├─ collect/
  |  ├─ app-x.js
  |  ├─ csv2sqlite.js
  |  ├─ manage.js
  |  ├─ package-lock.json
  |  ├─ package.json
  |  └─ test.js
  ├─ readme.md
  └─ test-0.ipynb
```
- [collect/app-x.js](collect/app-0.js) is the worker threads that pull labels from the website. 
- [collect/csv2sqlite.js](collect/csv2sqlite.js) can be ignored; it was used in the early stage to store everything in a csv file into a sqlite database. 
- [collect/manage.js](collect/manage.js) is the controller that add/remove tasks into/from the database. Each folder with format `region/year/` correspondes to a task in the database. 
- [collect/package.json](collect/package.json) stores the meta data and dependencies of a nodejs project. 

## Useful Commands
To start or continue collecting labels:
```
nohup node task-b/collect/app-0.js >> collect-0.log 2>&1 &
nohup node task-b/collect/app-1.js >> collect-1.log 2>&1 &
nohup node task-b/collect/app-2.js >> collect-2.log 2>&1 &
```
