# Directory for Raw Documents

## Getting Started
1. Manually download sets from Google Drive. Put all zip files in `data/`.
```
data/
  ├─ Set-1.zip
  ├─ Set-2.zip
  └─ ...
```
2. Run `unzip.py`.

## File Structure
```
data/
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

## Unzip all files in a folder:
```
unzip -O CP936 '*.zip' -d path/to/folder/
```
