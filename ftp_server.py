# -*- coding: utf-8 -*-
from socket import gethostname, gethostbyname
from pyftpdlib.servers import FTPServer
from pyftpdlib.handlers import FTPHandler
from pyftpdlib.authorizers import DummyAuthorizer


def main():
    auth = DummyAuthorizer()
    auth.add_user("SABCSIS03", "oceanop2", homedir="C://", perm="elradfmw")

    handler = FTPHandler
    handler.authorizer = auth

    host = gethostbyname(gethostname())
    server = FTPServer((host, 8602), handler)
    server.serve_forever()


if __name__ == "__main__":
    main()
