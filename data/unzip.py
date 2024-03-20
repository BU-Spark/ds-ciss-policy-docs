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

def convertFolderName(dir):
    region = dir.replace("规范性文件", "")
    dirOut = ''.join(s.capitalize() for s in pinyin(region, style=0, errors='replace'))
    if region == "陕西":
        dirOut = "ShaanXi"
    return dirOut

def convertYear(year):
    return year[-4:]

def convertSubFolder(sub):
    formatIndex = sub.index("规范性文件")
    region = sub[:formatIndex]
    year = sub[formatIndex+5:] if len(dir) - dir.index("规范性文件") - 5 > 0 else ""
    return


def isSubFolder(dir):
    # check if the folder is a subfolder (with year)
    leftover = len(dir) - dir.index("规范性文件") - 5
    return dir[-leftover:].isnumeric()

def main():

    import subprocess
    subprocess.run(["unzip", "-O", "CP936", "-o", "*.zip", "-d", "./origin/"], cwd=cwd, stdout=subprocess.DEVNULL)
    _, sets, _ = next(os.walk(os.path.join(cwd, "origin")))
    print(sets)

    # unzip all files
    for set in sets:
        dirs = next(os.walk(os.path.join(cwd, "origin", set)))[1]
        for dir in dirs:
            dirOut = convertFolderName(dir)
            years = next(os.walk(os.path.join(cwd, "origin", set, dir)))[1]
            for year in years:
                yearOut = convertYear(year)
                checkFolderExist(dirOut, yearOut)
                subs = next(os.walk(os.path.join(cwd, "origin", set, dir, year)))[1]
                if len(subs) > 0:
                    for sub in subs:
                        if isSubFolder(sub):
                            subOut = convertYear(sub)
                            checkFolderExist(dirOut, yearOut)
                            checkFolderExist(dirOut, yearOut, subOut)
                            subprocess.run(["unzip", "-O", "CP936", "-o", os.path.join(cwd, "origin", set, dir, year, sub, "*.zip"), "-d", os.path.join(cwd, dirOut, yearOut, subOut)], cwd=cwd, stdout=subprocess.DEVNULL)
                        else:
                            checkFolderExist(dirOut, yearOut)
                            subprocess.run(["unzip", "-O", "CP936", "-o", os.path.join(cwd, "origin", set, dir, year, sub, "*.zip"), "-d", os.path.join(cwd, dirOut, yearOut)], cwd=cwd, stdout=subprocess.DEVNULL)

    return

if __name__ == "__main__":
    main()
