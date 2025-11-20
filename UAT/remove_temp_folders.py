import os
import shutil

# dir_path = 'C:/Program Files'
dir_path = 'C:/Program Files (x86)'
for item in os.listdir(dir_path):
    if item.startswith('scoped_dir'):
        item_path = os.path.join(dir_path, item)
        shutil.rmtree(item_path, ignore_errors=True)
