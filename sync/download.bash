python download-setup.py $1
lftp -f /tmp/sstl-download.x
python ~/workspace/data_browser/scripts/import_data.py ~/sync/LUCID
