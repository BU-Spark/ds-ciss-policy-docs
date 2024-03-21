# Directory for Raw Documents

## Getting Started
1.  Manually download zip file(s) from Google Drive.  
    Unzip them, and put folders of all sets in `repo/origin/` as shown below.  

        repo/origin/
          ├─ Set-1
          ├─ Set-2
          └─ Set-3

3.  Install Python depencies:  

        pip install pypinyin

2.  Run `unzip.py`. It will generate processed data in `repo/data/` in the format of `region/year/`.  
    If progress management is not required at the moment or lacking dependencies, comment out **line 50** in [unzip.py](./unzip.py).

## File Structure
After running [unzip.py](./unzip.py), you should see something like this:
```
repo/data/
  ├─ shanghai
  |  ├─ 2020
  |  ├─ 2021
  |  ├─ 2022
  |  └─ ...
  ├─ sichuan 
  |  ├─ 2020
  |  ├─ 2021
  |  ├─ 2022
  |  └─ ...
  └─ ...
```

## Useful Commands
To unzip all files in a single directory
```
unzip -O CP936 '*.zip' -d path/to/folder/
```
