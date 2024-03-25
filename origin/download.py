import gdown
url = 'https://drive.google.com/uc?id=1nOeM0fEXOlHmrTA1IrNeBvfDy9pIbauc'
output = 'origin_all-3-sets.zip'
# gdown.download(url, output, quiet=False)

import os, subprocess
dirOrigin = os.path.dirname(os.path.realpath(__file__))
# subprocess.run(['unzip', '-O', 'CP936', '-n', 'origin_all-3-sets.zip', '-d', dirOrigin], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
subprocess.run('find . -name __MACOSX -exec rm -rf {} ;', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
subprocess.run('find . -name ".DS_Store" -type f -delete', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
