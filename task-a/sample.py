import os, sys, subprocess, random
cwd = os.path.dirname(os.path.realpath(__file__))
dataDir = os.path.join(cwd, '../data')

def sample(prob=0.001):
    fileCount = 0
    docUnique = {}
    # make directory sample/ if not exist
    regions = next(os.walk(dataDir))[1]
    for region in regions:
        years = next(os.walk(os.path.join(dataDir, region)))[1]
        for year in years:
            docs = next(os.walk(os.path.join(dataDir, region, year)))[2]
            for doc in docs:
                if random.random() < prob:
                    fileCount += 1
                    subprocess.run(["cp", os.path.join(dataDir, region, year, doc), os.path.join(cwd, 'sample', doc)])
    print("Sampled", fileCount, "files")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if os.path.exists(os.path.join(cwd, "sample")):
            if len(sys.argv) > 2 and sys.argv[2] == "overwrite":
                subprocess.run(["rm", "-r", os.path.join(cwd, "sample")])
            else:
                print("Sample directory already exists. Use 'overwrite' option to overwrite.")
                sys.exit(1)
        os.makedirs(os.path.join(cwd, "sample"))
        sample(float(sys.argv[1]))
    else:
        print("Usage: python sample.py <probability> [overwrite?]")
