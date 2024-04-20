import os
cwd = os.path.dirname(os.path.realpath(__file__))
print(cwd)

mapL1 = {}
mapL2 = {}
trimLabel = lambda x: x.strip().split(' ')[0]
with open(os.path.join(cwd, 'mapping.csv')) as f:
    for line in f:
        line = line.strip().split(',')
        assert len(line) == 5
        labelL1, labelL2 = '', ''
        if len(line[3]) > 0:
            labelL1 = line[3]
        if len(line[4]) > 0:
            labelL2 = line[4]
        if len(line[0]) > 0:
            mapL1[trimLabel(line[0])] = labelL1
            mapL2[trimLabel(line[0])] = labelL2
        if len(line[1]) > 0:
            mapL1[trimLabel(line[1])] = labelL1
            mapL2[trimLabel(line[1])] = labelL2
        if len(line[2]) > 0:
            mapL1[trimLabel(line[2])] = labelL1
            mapL2[trimLabel(line[2])] = labelL2
print("Unique labels to be mapped:", len(mapL1), len(mapL2))

# load data
import pandas as pd
df = pd.read_csv(os.path.join(cwd, 'policies_all.csv'))
df['type'] = df['type'].astype(str)
print(f"All records: {len(df)}. Record with no type (or 404): {len(df[(df['type'].isnull())|(df['type']=='404-NotFound')])}. ")

# basic mapping
df['label_L1'] = df['type'].map(mapL1)
df['label_L2'] = df['type'].map(mapL2)
print(f"(Basic Mapping) Records with no L1 label: {len(df[df['label_L1'].isnull()])}. Records with no L2 label: {len(df[df['label_L2'].isnull()])}.")

df_noMap = df[~((df['type'] == 'nan') | (df['type']=='404-NotFound')) & df['label_L1'].isnull()].copy()
print(f"(Basic Mapping) Records with no mapping: {df_noMap.shape[0]}.")

# use the first label 
df_noMap['type'] = df_noMap['type'].apply(lambda x: x.split(',')[0])

def matchLongest(x):
    res = ''
    x = x.strip()
    for key in mapL1:
        if x.startswith(key) and x[len(key):] in mapL1 and len(key) > len(res):
            res = key
    return res if res != '' else x
df_noMap['type'] = df_noMap['type'].apply(matchLongest)
df_noMap['label_L1'] = df_noMap['type'].map(mapL1)
df_noMap['label_L2'] = df_noMap['type'].map(mapL2)

df.update(df_noMap)
df_noMap = df[~((df['type'] == 'nan') | (df['type']=='404-NotFound')) & df['label_L1'].isnull()].copy()
print(f"(Advance Mapping) Records with no L1 label: {len(df[df['label_L1'].isnull()])}. Records with no L2 label: {len(df[df['label_L2'].isnull()])}.")
print(f"(Advance Mapping) Records with no mapping: {df_noMap.shape[0]}.")

# save files
df.to_csv(os.path.join(cwd, 'policies_label.csv'), index=False)
df_noMap.to_csv(os.path.join(cwd, 'policies_noMap.csv'), index=False)
df_noMap.shape
