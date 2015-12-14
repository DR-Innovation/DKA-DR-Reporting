# DKA-DR-Reporting
Scripts that collects objects published on danskkulturarv.dk for internal reporting


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
?!/bin/bash
d=$(date +%y-%m)
python ~/DKA-DR-Reporting/published_between.py 1970-01-01T12:00:00Z 2030-12-30T12:00:00Z$
```

### Update from git
```
cd DKA-DR-Reporting/
git pull
```
