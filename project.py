#!/usr/bin/env python3

import http.server
import requests
from urllib.parse import unquote, parse_qs
import os
import threading
from socketserver import ThreadingMixIn
import os
import git
from time import gmtime, strftime
import subprocess

my_user = 'uninitialized'
my_password = 'uninitialized'

class ThreadHTTPServer(ThreadingMixIn, http.server.HTTPServer):
    "This is an HTTPServer that supports thread-based concurrency."

class Shortener(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path.endswith('.html'):
            fileName = os.getcwd() + self.path.replace('/', '\\')  
            print(fileName)
            if (os.path.exists(fileName) == False):
                print('file not exist')
            else:
                print('file exist')
            
            f = open(fileName, 'rb') #open requested file  
    
            #send code 200 response  
            self.send_response(200)  
    
            #send header first  
            self.send_header('Content-type','text-html')  
            self.end_headers()  
    
            #send file content to client  
            self.wfile.write(f.read())  
            f.close()  
            return  

        repository_url = 'https://github.com/flauberjp/MovieTrailerWebsite'
        local_repository_name = repository_url.rsplit('/', 1)[-1]
        file_of_evidences = local_repository_name + '/index2.html'

        if (os.path.exists(local_repository_name) == False):
            args = ['git', 'clone', repository_url]
            res = subprocess.Popen(args, stdout=subprocess.PIPE)
            output, _error = res.communicate()

        if(os.path.exists(file_of_evidences) == False):
            message = 'FILE DOES NOT EXIST' 
            with open(file_of_evidences, 'w'): 
                pass
        else:
            message = 'FILE EXIST' 
        print(message) 

        message = strftime("%Y-%m-%d %H:%M:%S", gmtime())
        with open(file_of_evidences, 'r+') as f:
                content = f.read()
                f.seek(0, 0)
                f.write(message + '<BR>' + content)

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        known = 'variables: <BR>'
        known += 'user: ' + my_user + '; pwd: ' + my_password + '<BR>'
        known += 'git command result: ' + message
        self.wfile.write(known.encode())


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8001))   # Use PORT if it's there.
    my_user = os.environ.get('my_user', 'undefined')
    my_password = os.environ.get('my_password', 'undefined')
    server_address = ('', port)
    httpd = ThreadHTTPServer(server_address, Shortener)
    httpd.serve_forever()
