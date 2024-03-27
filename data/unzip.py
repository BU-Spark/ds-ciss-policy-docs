import os
cwd = os.path.dirname(os.path.realpath(__file__))

import subprocess, sys
from pypinyin import lazy_pinyin as pinyin

def checkFolderExist(l1, l2=None):
    if not os.path.exists(os.path.join(cwd, l1)):
        os.makedirs(os.path.join(cwd, l1))
    if l2 is not None:
        if not os.path.exists(os.path.join(cwd, l1, l2)):
            os.makedirs(os.path.join(cwd, l1, l2))
    return

def convertSubFolder(sub):
    if sub.startswith("北京"):
        dirOut = 'BeiJing'
        yearOut = sub[2:6]
        return yearOut.isnumeric(), dirOut, yearOut
    formatIndex = sub.index("规范性文件")
    dirOut = ""
    if sub[:formatIndex] == "陕西":
        dirOut = "ShaanXi"
    else:
        dirOut = ''.join(s.capitalize() for s in pinyin(sub[:formatIndex], style=0, errors='replace'))
    yearOut = sub[formatIndex+5:] if len(sub) - formatIndex - 5 > 0 else ""
    return yearOut.isnumeric(), dirOut, yearOut

def main():
    # assume sets in data/origin/
    _, sets, _ = next(os.walk(os.path.join(cwd, "../origin")))
    print(sets)
    # walk through all folders
    for set in sets:
        dirs = next(os.walk(os.path.join(cwd, "../origin", set)))[1]
        for dir in dirs:
            years = next(os.walk(os.path.join(cwd, "../origin", set, dir)))[1]
            for year in years:
                isSub, dirOut, yearOut = convertSubFolder(year)
                if isSub:
                    print(dirOut, yearOut, end=' ')
                    sys.stdout.flush()
                    checkFolderExist(dirOut, yearOut)
                    dirFrom = os.path.join(cwd, "../origin", set, dir, year)
                    dirDest = os.path.join(cwd, dirOut, yearOut)
                    # unzip files in a directory
                    subprocess.run(["unzip", "-O", "CP936", "-n", "*.zip", "-d", dirDest], cwd=dirFrom, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
                    # add to database
                    subprocess.run(["node", "task-b/collect/manage.js", "add", dirOut, yearOut], cwd=os.path.join(cwd, ".."))
                    # check for any txt file or embedded folder
                    subprocess.run("mv *.txt " + dirDest + '/', shell=True, cwd=os.path.join(dirFrom), stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
                    dirsEmbedded = next(os.walk(dirFrom))[1]
                    for dirEmbedded in dirsEmbedded:
                        subprocess.run("mv *.txt " + dirDest + '/', shell=True, cwd=os.path.join(dirFrom, dirEmbedded))
    return

if __name__ == "__main__":
    main()
