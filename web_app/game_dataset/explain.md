### Structure:
data.yaml
images/
    ├── train/
    └── val/
labels/
    ├── train/
    └── val/
[val is not used yet]

### file name format:
game_{current_date}_{short_sid}_{frame_num:05d}.jpg
game_{current_date}_{short_sid}_{frame_num:05d}.txt

### label format:

Example:
class_id x_center y_center width height
id =0 is human
id =1 is obstacle

0 0.619792 0.754167 0.052083 0.069444
1 0.927083 0.256944 0.052083 0.069444
1 0.983333 0.222222 0.052083 0.069444
1 0.286458 0.062500 0.052083 0.069444
1 0.441667 0.027778 0.052083 0.069444

