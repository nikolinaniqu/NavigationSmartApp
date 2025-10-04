from ftplib import FTP

ftp = FTP('test.rebex.net')
ftp.login('demo', 'password')  # ovo su javni demo podaci
ftp.dir()
ftp.quit()