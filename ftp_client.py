# -*- coding: utf-8 -*-
# PYTHON 3 compatible code (because using MLSD from ftplib)

from ftplib import FTP
import os
import re
import sys
import json
import jsonschema
import getpass
from datetime import datetime, timedelta


class FTP_connection(object):
    """docstring for FTP_connection."""

    def __init__(self, server_name, acqn_mode):
        self._ftp = FTP('')
        self.time = datetime.utcnow()
        self.server_name = server_name.upper()
        self.acqn_mode = acqn_mode.upper()
        self._ftp_session()

    def _ftp_session(self):
        self._ftp.connect(self.server_name, 8602)
        self._ftp.login('SABCSIS03', 'oceanop2')
        print('FTP session opened @ {}'.format(self.server_name))
        path = ('DADAS32\Bin\Output' if self.acqn_mode == 'DADAS'
                else 'Program Files (x86)\SISMO\HIST')
        try:
            self._ftp.cwd(path)
            self.lista = self.file_list()
            print('Directory is C:\\{}'.format(path))
        except Exception:
            print('No such Directory C:\\{}'.format(path))
            self.quit()

    def file_list(self):
        """Returns a list of file names in a specified directory."""
        try:
            lista = self._ftp.nlst()
        except Exception:
            print('FTP Connection Timed Out/Closed.\n Trying to Reconnect.')
            self._ftp_session()
            lista = self.file_list()
        return lista

    def quit(self):
        """Close ftp connection."""
        try:
            self._ftp.quit()
        except Exception:
            self._ftp.close()
        print('FTP session closed')

    def sync_files(self, sync, ext, path_target):
        T = (self.time - timedelta(hours=sync + 1)).strftime('%Y-%m-%d-%H-45')
        fmt = '(\d{4}-\d{2}-\d{2}-\d{2}-\d{2})'
        get_ext = lambda x: x.split('.')[-1]        
        for i in self.lista:
            value = re.search(fmt, i)
            if value:
                if (value.group(0) > T) & (get_ext(i) in ext):
                    self.download_file(i, path_target)

    def filter_time(self, x, time):
        fmt = '(\d{4}-9\d{2}-\d{2}-\d{2}-\d{2})'
        Tfmt = time.strftime('%Y-%m-%d-%H-45')
        value = re.search(fmt, x)
        if value:
            if value.group(0) > Tfmt:
                return True
        return False

    def download_file(self, filename=None, path_target=os.getcwd()):
        """Download filename if exists @ server."""
        self.test_path_target(path_target)
        if filename:
            if filename in self.lista:
                self._retrieve(filename)
            else:
                print('{} does not exist @ FTP server'.format(filename))
                return
        else:
            print('Filename is not defined')
            return

    def _retrieve(self, filename):
        file_ = os.path.join(self.path_target, filename)
        target = open(file_, 'wb')
        try:
            self._ftp.retrbinary('RETR ' + filename, target.write, 1024)
        except Exception:
            print('FTP Connection Timed Out/Closed.\n Trying to Reconnect...')
            self._ftp_session()
            self._ftp.retrbinary('RETR ' + filename, target.write, 1024)
        target.close()
        print('Download {} @ {}'.format(filename, self.path_target))

    def test_path_target(self, d):
        if not os.path.isdir(d):
            print('path_target refers to a not valid path.')
            self.path_target = os.getcwd()       
        if not self._isWritable(d):
            print('{} does not have privileges to write'
                  ' @ {}'.format(getpass.getuser(), d))
            self.path_target = os.getcwd()       
        else:
            self.path_target = d

    def _isWritable(self, path):
        try:
            tfile = open(os.path.join(path, 't'), 'w')
            tfile.close()
            os.remove(os.path.join(path, 't'))
        except Exception:
            return False
        return True


def getparams(dname):
    """Load a json file in same path of script. """
    schema = {
        "$schema": "http://json-schema.org/draft-06/schema#",
        "type": "object",
        "additionalProperties": {"$ref": "#/definitions/FTPClientValue"},
        "definitions": {
            "FTPClientValue": {
                "type": "object",
                "additionalProperties": True,
                "properties": {
                    "sync": {"type": "integer"},
                    "software": {"type": "string"},
                    "ext": {"type": "array", "items": {"type": "string"}},
                    "path": {"type": "string"},},
                "required": ["ext", "path", "software", "sync"],
                "title": "FTPClientValue"}}}
    try:
        with open(os.path.join(dname, 'ftp_client.json')) as f:
            params = json.load(f)
    except Exception:
        raise Exception("Poorly-formed text, not JSON:")
    try:
        jsonschema.validate(params, schema)
    except jsonschema.exceptions.ValidationError as e:
        raise Exception("Well-formed but invalid JSON:", e)
    return params


if __name__ == '__main__':

    if hasattr(sys, '_MEIPASS'):
        dname = os.path.dirname(os.path.abspath(sys.argv[0]))
    else:
        dname = os.path.dirname(os.path.abspath(__file__))

    ftp_servers = getparams(dname)

    for i in ftp_servers:
        print('Tentativa de conexão em {}'.format(i))
        kw = ftp_servers[i]
        try:
            server = FTP_connection(i, kw['software'])
            server.sync_files(kw['sync'], kw['ext'], kw['path'])
            server.quit()
        except Exception:
            print('servidor sem conexão em {}'.format(i))
