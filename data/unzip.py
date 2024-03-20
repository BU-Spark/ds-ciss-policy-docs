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
    yearOut = sub[formatIndex+5:] if len(dir) - dir.index("规范性文件") - 5 > 0 else ""
    return yearOut.isnumeric(), dirOut, yearOut

def main():

    import subprocess
    subprocess.run(["unzip", "-O", "CP936", "-o", "*.zip", "-d", "./origin/"], cwd=cwd, stdout=subprocess.DEVNULL)
    _, sets, _ = next(os.walk(os.path.join(cwd, "origin")))
    print(sets)

    # unzip all files
    for set in sets:
        dirs = next(os.walk(os.path.join(cwd, "origin", set)))[1]
        for dir in dirs:
            years = next(os.walk(os.path.join(cwd, "origin", set, dir)))[1]
            for year in years:
                isSub, dirOut, yearOut = convertSubFolder(year)
                if isSub:
                    print(dirOut, yearOut)
                    checkFolderExist("data", dirOut, yearOut)
    return

if __name__ == "__main__":
    main()
