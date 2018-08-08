# OCN_FTP_CAMILE

## Projeto para dar carga ao sistema OCNSIO2.

- **ftp_server.py**  
Rotina para subir servidor de FTP.  
Código fonte para geração do executável ftp_server.exe.  

- **ftp_server.exe**  
Executável gerado via pyinstaller.  
pyinstaller --onefile ftp_server.py  
PyInstaller: 3.3.1  
Python: 3.6.0  
Platform: Windows-7-6.1.7601-SP1  

- **ftp_client.py**  
Rotina para fazer conexão com servidor de FTP e download de arquivos da última hora de medição.  
Parâmetros de entrada fornecidos via .json no local do script/executável.  

- **ftp_client.exe**  
Executável gerado via pyinstaller.  
pyinstaller --onefile ftp_client.py  
PyInstaller: 3.3  
Python: 2.7.15  
Platform: Windows-7-6.1.7601-SP1  

- **ftp_client.json**  
json com informações:  
    -Do servidor de FTP (e.g. hostname ou ip).  
    -Do software de aquisição (e.g. DADAS ou SISMO).  
    -Dos sensores habilitados para coleta.  
    -Do path para download.  
