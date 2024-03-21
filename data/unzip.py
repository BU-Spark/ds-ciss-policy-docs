import os
cwd = os.path.dirname(os.path.realpath(__file__))

from pypinyin import lazy_pinyin as pinyin

def checkFolderExist(l1, l2=None):
    if not os.path.exists(os.path.join(cwd, l1)):
        os.makedirs(os.path.join(cwd, l1))
    if l2 is not None:
        if not os.path.exists(os.path.join(cwd, l1, l2)):
            os.makedirs(os.path.join(cwd, l1, l2))
    return

def convertSubFolder(sub):
    formatIndex = sub.index("规范性文件")
    dirOut = ""
    if sub[:formatIndex] == "陕西":
        dirOut = "ShaanXi"
    else:
        dirOut = ''.join(s.capitalize() for s in pinyin(sub[:formatIndex], style=0, errors='replace'))
    yearOut = sub[formatIndex+5:] if len(sub) - formatIndex - 5 > 0 else ""
    return yearOut.isnumeric(), dirOut, yearOut

def main():

    import subprocess
    # subprocess.run(["unzip", "-O", "CP936", "-o", "*.zip", "-d", "./origin/"], cwd=cwd, stdout=subprocess.DEVNULL)
    # assume sets in data/origin/
    _, sets, _ = next(os.walk(os.path.join(cwd, "origin")))
    print(sets)

    # walk through all folders
    for set in sets:
        dirs = next(os.walk(os.path.join(cwd, "origin", set)))[1]
        for dir in dirs:
            years = next(os.walk(os.path.join(cwd, "origin", set, dir)))[1]
            for year in years:
                isSub, dirOut, yearOut = convertSubFolder(year)
                if isSub:
                    print(dirOut, yearOut)
                    checkFolderExist(dirOut, yearOut)
                    dirFrom = os.path.join(cwd, "origin", set, dir, year)
                    dirDest = os.path.join(cwd, dirOut, yearOut)
                    subprocess.run(["unzip", "-O", "CP936", "-o", "*.zip", "-d", dirDest], cwd=dirFrom, stdout=subprocess.DEVNULL)
                    subprocess.run(["node", "analysis/ajax/manage.js", "add", dirOut, yearOut], cwd=os.path.join(cwd, ".."))
                    # subprocess.run(["rm", "-f", "*.zip"], cwd=dirUnzip)

    return

if __name__ == "__main__":
    main()
