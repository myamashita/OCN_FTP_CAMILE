# -*- coding: utf-8 -*-
from ftplib import FTP
import os
import sys
import json
import getpass
from datetime import datetime, timedelta


class FTP_connection(object):
    """docstring for FTP_connection."""

    def __init__(self, server_name=[], acqn_mode=[], path_target=os.getcwd()):
        self._ftp = FTP('')
        self.server_name = server_name
        self.acqn_mode = acqn_mode
        self.path_target = path_target
        self.make_session()

    @property
    def server_name(self):
        return self._server_name

    @server_name.setter
    def server_name(self, d):
        if not d:
            raise Exception("server_name cannot be empty.")
        if not isinstance(d, str):
            raise Exception("server_name needs to be a string.")
        self._server_name = d.upper()

    @property
    def acqn_mode(self):
        return self._acqn_mode

    @acqn_mode.setter
    def acqn_mode(self, d):
        if not d:
            raise Exception("server_name cannot be empty.")
        if not isinstance(d, str):
            raise Exception("server_name needs to be a string.")
        if d.upper() not in ['DADAS', 'SISMO']:
            raise Exception('acqn_mode is DADAS or SISMO')
        self._acqn_mode = d.upper()

    def _file_dir(self, mode):
        path = ('DADAS32\Bin\Output' if mode == 'DADAS'
                else 'Program Files (x86)\SISMO\HIST')
        try:
            self._ftp.cwd(path)
            self.file_dir = 'C:\\{}'.format(path)
            print('Directory is {}'.format(self.file_dir))
        except Exception:
            print('No such Directory C:\\{}'.format(path))
            self.quit()

    def file_list(self):
        """Return a list of file names."""
        try:
            nlst = self._ftp.nlst()
        except Exception:
            print('FTP Connection Timed Out/Closed.\n Trying to Reconnect.')
            self.make_session()
            nlst = self._ftp.nlst()
        return nlst

    def _ftp_session(self, server_name):
        self._ftp.connect(server_name, 8602)
        self._ftp.login('SABCSIS03', 'oceanop2')
        print('FTP session opened @ {}'.format(server_name))

    def make_session(self):
        self._ftp_session(self.server_name)
        self._file_dir(self.acqn_mode)
        self.nlst = self.file_list()

    def quit(self):
        """Close ftp connection."""
        try:
            self._ftp.quit()
        except Exception:
            self._ftp.close()
        print('FTP session closed')

    @staticmethod
    def check_if_exists(filename, filelist):
        return filename in filelist

    def download_file(self, filename, path_target=os.getcwd()):
        if self.check_if_exists(filename, self.nlst):
            self.path_target = path_target
            self._retrieve(filename)
        else:
            print('{} does not exist @ FTP server'.format(filename))

    def _retrieve(self, filename):
        file_ = os.path.join(self.path_target, filename)
        target = open(file_, 'wb')
        try:
            self._ftp.retrbinary('RETR ' + filename, target.write, 1024)
        except Exception:
            print('FTP Connection Timed Out/Closed.\n Trying to Reconnect.')
            self.make_session()
            self._ftp.retrbinary('RETR ' + filename, target.write, 1024)
        target.close()
        print('Download {} @ {}'.format(filename, self.path_target))

    @property
    def path_target(self):
        return self._path_target

    @path_target.setter
    def path_target(self, d):
        if not d:
            raise Exception("path_target cannot be None.")
        if not isinstance(d, str):
            raise Exception("path_target needs to be a string.")
        if not os.path.isdir(d):
            raise Exception('path_target refers to a not valid path.')
        if not self._isWritable(d):
            raise Exception('{} does not have privileges to write'
                            ' @ {}.'.format(getpass.getuser(), d))
        self._path_target = d

    def _isWritable(self, path):
        try:
            tfile = open(os.path.join(path, 't'), 'w')
            tfile.close()
            os.remove(os.path.join(path, 't'))
        except Exception:
            return False
        return True


def create_filename(dt, **kw):
    files = []
    check_dict(kw)
    if kw['software'] == 'SISMO':
        for i in kw['sensors']:
            if i == 'young':
                files.append('{}01_{:{fmt}}.yng_gz'.format(
                    kw['id'], dt - timedelta(hours=1),
                    fmt="%Y-%m-%d-%H-50"))
            if i == 'fsi2d':
                files.append('{}03_{:{fmt}}.fsi_gz'.format(
                    kw['id'], dt - timedelta(hours=1),
                    fmt="%Y-%m-%d-%H-50"))
    if kw['software'] == 'DADAS':
        for i in kw['sensors']:
            if i == 'young':
                files.append('{}01_{:{fmt}}.yng_gz'.format(
                    kw['id'], dt, fmt="%Y-%m-%d-%H-00"))
            if i == 'fsi2d':
                files.append('{}03_{:{fmt}}.fsi_gz'.format(
                    kw['id'], dt, fmt="%Y-%m-%d-%H-00"))
    return files


def check_dict(kw):
    if 'id' not in kw:
        raise Exception("'id' not found.")
    if 'sensors' not in kw:
        raise Exception("'sensors' not found.")
    if 'software' not in kw:
        raise Exception("'software' not found.")


def getparams(dname):
    """Load a json file in same path of script. """
    with open(os.path.join(dname, 'ftp_client.json')) as f:
        params = json_load_byteified(f)
        return params


def json_load_byteified(file_handle):
    return _byteify(json.load(file_handle, object_hook=_byteify),
                    ignore_dicts=True)


def _byteify(data, ignore_dicts=False):
    # if this is a unicode string, return its string representation
    if isinstance(data, unicode):
        return data.encode('utf-8')
    # if this is a list of values, return list of byteified values
    if isinstance(data, list):
        return [_byteify(item, ignore_dicts=True) for item in data]
    # if this is a dictionary, return dictionary of byteified keys and values
    # but only if we haven't already byteified it
    if isinstance(data, dict) and not ignore_dicts:
        return {_byteify(key, ignore_dicts=True):
                _byteify(value, ignore_dicts=True)
                for key, value in data.iteritems()}
    # if it's anything else, return it in its original form
    return data


if __name__ == '__main__':

    if hasattr(sys, '_MEIPASS'):
        dname = os.path.dirname(os.path.abspath(sys.argv[0]))
    else:
        dname = os.path.dirname(os.path.abspath(__file__))

    dt = datetime.utcnow()
    ftp_servers = getparams(dname)

    for i in ftp_servers:
        kw = ftp_servers[i]
        server = FTP_connection(i, kw['software'], dname)
        files = create_filename(dt, **kw)
        [server.download_file(j, kw['path']) for j in files]
        server.quit()
