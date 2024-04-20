import os, sys, re
cwd = os.path.dirname(os.path.realpath(__file__))
dataDir = os.path.join(cwd, '../data')

import pandas as pd
from pypinyin import lazy_pinyin as pinyin

def fileExist(file):
    return os.path.exists(os.path.join(cwd, file)) and os.path.isfile(os.path.join(cwd, file))

if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1].lower()
        if cmd == 'csv':
            args = sys.argv[2:]
            if len(args) != 2:
                print("Usage: python utils.py csv < region | year | type | l1 | l2 > <value>")
                exit(1)
            cols = {'region': 'area', 'year': 'year', 'type': 'type', 'l1': 'label_L1', 'l2': 'label_L2'}
            if args[0].lower() not in cols:
                print("Invalid filter column. Choose from 'region', 'year', 'type', 'l1', 'l2'.")
                exit(1)
            col = cols[args[0].lower()]
            df = None
            if fileExist('policies_label.csv'):
                df = pd.read_csv(os.path.join(cwd, 'policies_label.csv'))
            elif fileExist('policies_all.csv') and args[0] != 'l1' and args[0] != 'l2':
                df = pd.read_csv(os.path.join(cwd, 'policies_all.csv'))
            else:
                print("File 'policies_label.csv' or 'policies_all.csv' not found. Please make sure at least one of them exists in the 'task-b/' directory ('policies_label.csv' must exist for 'l1' or 'l2' column).")
                exit(1)
            if args[0] == 'region':
                region = args[1]
                regionRegex = re.compile(r'^[A-Za-z]+$')
                if regionRegex.match(region) is None:
                    if region == "陕西":
                        region = "shaanxi"
                    else:
                        region = ''.join(pinyin(region, style=0, errors='replace'))
                else:
                    region = region.lower()
                df = df[df[col].str.lower() == region]
            else:
                df = df[df[col] == args[1]]
            if df.shape[0] == 0:
                print(f"No data found for {args[0]}: {args[1]}.")
                exit(1)
            df.to_csv(os.path.join(cwd, f'result_{args[0]}_{args[1]}.csv'), index=False)
            print(f"File saved as 'result_{args[0]}_{args[1]}.csv'; total rows: {df.shape[0]}.")
            exit(0)
        elif cmd == 'doc':
            print("Still WIP.")
        else:
            print(f"COMMAND '{cmd}' invalid. Choose from 'csv', 'doc'.")
    print("Usage: python utils.py COMMAND")
    print("COMMAND 'csv' will create a csv file with filtered records. You can select a column (from 'region', 'year', 'type', 'l1', or 'l2') to filter by and the value to filter.")
    print("COMMAND 'doc' still WIP.")
