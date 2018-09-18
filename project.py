#!/usr/bin/env python3

import http.server
import requests
from urllib.parse import unquote, parse_qs
import os
import threading
from socketserver import ThreadingMixIn
from os import environ
from time import gmtime, strftime
import subprocess
from sys import argv
from os import environ
import simplejson

try:
    import git
    if git.__version__ < '0.3.1':
        raise ImportError("Your version of git is %s. Upgrade to 0.3.1 or better." % git.__version__)
    have_git = True
except ImportError as e:
    have_git = False
    GIT_MISSING = 'Requires gitpython module, but not installed or incompatible version: %s' % e

print('Working directory (initial): ')
initialWorkingDirectory = os.getcwd()
print(initialWorkingDirectory)

print('git help -a')
print('\n' + subprocess.check_output('git help -a', 
        shell=True).decode())

print('\n' + subprocess.check_output('git --version', 
        shell=True).decode())

main_page_content = '''
<html>  
  <body>
    {content}
  </body>
</html>
'''

my_user = os.environ.get('my_user', 'undefined')
my_email = os.environ.get('my_email', 'undefined')
my_password = os.environ.get('my_password', 'undefined')

print(
    'my_user: ' + my_user + '\n' + 
    'my_user: ' + my_email + '\n' + 
    'my_user: ' + my_password + '\n')


print('git config --global credential.helper cache')
print('\n' + subprocess.check_output('git config --global credential.helper cache', 
        shell=True).decode())

print('printf \'protocol=https\\nhost=github.com\\nusername=' + my_user + '\\npassword=' + my_password + '\\n\' | git credential approve')
print('\n' + subprocess.check_output('printf \'protocol=https\\nhost=github.com\\nusername=' + my_user + '\\npassword=' + my_password + '\\n\' | git credential approve', 
        shell=True).decode())

repository_url = 'https://github.com/flauberjp/MovieTrailerWebsite'
local_repository_name = repository_url.rsplit('/', 1)[-1]
file_of_evidences = 'index2.html'

if (os.path.exists(local_repository_name) == False):
    print('git clone ' + repository_url)
    print(subprocess.check_output('git clone ' + repository_url, 
        shell=True).decode())

nextCurrentDirectory = initialWorkingDirectory + '/' +  local_repository_name
if os.name == 'nt':
    nextCurrentDirectory = nextCurrentDirectory.replace('/', '\\') 
print('Changing current directory from ' + initialWorkingDirectory + ' to ' + nextCurrentDirectory)
os.chdir(nextCurrentDirectory)
print('Working directory: ')
cwd = os.getcwd()
print(cwd)

print('git remote -v')
print(subprocess.check_output('git remote -v', shell=True).decode())    

print('Checking existence of \"' + file_of_evidences + '\"...')

if(os.path.exists(file_of_evidences) == False):
    print('FILE DOES NOT EXIST. Creating...') 
    with open(file_of_evidences, 'w'): 
        pass
else:
    print('FILE EXIST')

file_of_evidences_fullPath = '/' +  file_of_evidences
if os.name == 'nt':
    file_of_evidences_fullPath = os.getcwd() + file_of_evidences_fullPath.replace('/', '\\') 
else: 
    file_of_evidences_fullPath = os.getcwd() + file_of_evidences_fullPath 
print('Full path: \"' + file_of_evidences_fullPath + '\"...')

class ThreadHTTPServer(ThreadingMixIn, http.server.HTTPServer):
    "This is an HTTPServer that supports thread-based concurrency."

class Shortener(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        self.data_string = self.rfile.read(int(self.headers['Content-Length']))
        data = simplejson.loads(self.data_string)
        print(str(data).encode())
        print("Author: {}".format(data['push']['changes'][0]['new']['target']['author']['user']['username']))
        print("Hash: {}".format(data['push']['changes'][0]['new']['target']['hash'][0:6]))
        print("Summary: {}...".format(data['push']['changes'][0]['new']['target']['message'].rstrip()[0:6]))
        return "OK"

        if 'request' in self.path:
            ###
            self.wfile.write(str(data).encode())
            ####
            repo = git.Repo(".") 
            print("Location "+ repo.working_tree_dir)
            print("Remote: " + repo.remote("origin").url)


            commit_message = strftime("%Y-%m-%d %H:%M:%S", gmtime())

            lastPartOfThePath = self.path.rsplit('/', 1)[-1]
            if(lastPartOfThePath != 'request'):
                commit_message += ' ' + lastPartOfThePath

            with open(file_of_evidences_fullPath, 'r+') as f:
                content = f.read()
                f.seek(0, 0)
                f.write(commit_message + '<BR>' + content)
                f.close()

            index = repo.index
            index.add([repo.working_tree_dir + '/*'])
            new_commit = index.commit(commit_message)
            origin = repo.remotes.origin
            origin.push()

        fileName = file_of_evidences_fullPath
            
        f = open(fileName, 'rb') #open requested file  

        #send code 200 response  
        self.send_response(200)  

        #send header first  
        self.send_header('Content-type','text-html')  
        self.end_headers()  

        #send file content to client
        textToBeSent = main_page_content.format(content=f.read().decode("utf-8"))
        #print(textToBeSent)
        self.wfile.write(textToBeSent.encode())
        f.close()  
        return  


    def do_GET(self):
        if 'request' in self.path:
            if not have_git:
                print(GIT_MISSING)
            else:
                repo = git.Repo(".") 
                print("Location "+ repo.working_tree_dir)
                print("Remote: " + repo.remote("origin").url)


                commit_message = strftime("%Y-%m-%d %H:%M:%S", gmtime())

                lastPartOfThePath = self.path.rsplit('/', 1)[-1]
                if(lastPartOfThePath != 'request'):
                    commit_message += ' ' + lastPartOfThePath

                with open(file_of_evidences_fullPath, 'r+') as f:
                    content = f.read()
                    f.seek(0, 0)
                    f.write(commit_message + '<BR>' + content)
                    f.close()

                index = repo.index
                index.add([repo.working_tree_dir + '/*'])
                new_commit = index.commit(commit_message)
                origin = repo.remotes.origin
                origin.push()

        fileName = file_of_evidences_fullPath
        if (self.path.endswith('.html')):
            if os.name == 'nt':
                fileNameTemp = os.getcwd() + self.path.replace('/', '\\') 
            else: 
                fileNameTemp = os.getcwd() + self.path  
            print(fileName)
            if (os.path.exists(fileNameTemp) == False):
                print('\"' + fileName + '\" file not exist')
            else:
                fileName = fileNameTemp
                print('\"' + fileName + '\" file exist')
            
        f = open(fileName, 'rb') #open requested file  

        #send code 200 response  
        self.send_response(200)  

        #send header first  
        self.send_header('Content-type','text-html')  
        self.end_headers()  

        #send file content to client
        textToBeSent = main_page_content.format(content=f.read().decode("utf-8"))
        #print(textToBeSent)
        self.wfile.write(textToBeSent.encode())
        f.close()  
        return  


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8001))   # Use PORT if it's there.
    server_address = ('', port)
    httpd = ThreadHTTPServer(server_address, Shortener)
    httpd.serve_forever()
