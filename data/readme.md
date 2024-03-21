# Directory for Raw Documents

## Getting Started
1.  Prepare
    1.  Manually download zip file(s) from Google Drive.  
    2.  Unzip them, and put all sets in `repo/origin/` as shown below.  

            repo/origin/
              ├─ set1/
              ├─ set2/
              └─ set3/

3.  Install Python dependencies:  

        pip install pypinyin

2.  Run `unzip.py`. It will generate raw data in `repo/data/` in the format of `region/year/`.  

        python data/unzip.py

    \* If progress management is not required or lack NodeJS dependencies, comment out **line 50** in [unzip.py](./unzip.py).

## File Structure
After running [unzip.py](./unzip.py), you should see something like this:
```
repo/data/
  ├─ shanghai/
  |  ├─ 2020/
  |  |  ├─ document1.txt
  |  |  ├─ document2.txt
  |  |  └─ ...
  |  ├─ 2021/
  |  ├─ 2022/
  |  └─ ...
  ├─ sichuan/
  |  ├─ 2020/
  |  ├─ 2021/
  |  ├─ 2022/
  |  └─ ...
  └─ ...
```

## Useful Commands
To unzip all files in a single directory:
```
unzip -O CP936 '*.zip' -d path/to/folder/
```
