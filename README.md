# DKA-DR-Reporting
Scripts that collects objects published on danskkulturarv.dk for internal reporting

### Install the requirements
sudo apt-get install python-dev libssl-dev libffi-dev
pip install -r requirements.txt

### Get in the correct folder
```
ssh www.danskkulturarv.dk
sudo su danskkulturarv
cd ~/
```

### Check/edit cron settings
```
crontab -e
```

### Run the script manually
```
~/generate-dka-report.sh
```

### Generate script looks like this:
```
#?!/bin/bash
d=$(date +%Y-%m)
python ~/DKA-DR-Reporting/published_between.py 1970-01-01T12:00:00Z 2030-12-30T12:00:00Z ~/dr-reports/$d.csv
ssconvert ~/dr-reports/$d.csv ~/dr-reports/$d.xlsx
```

### Update from git
```
cd DKA-DR-Reporting/
git pull && cp -r theme ~/dr-reports
```
