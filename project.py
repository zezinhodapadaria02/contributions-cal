#!/usr/bin/env python3

import http.server
import requests
from urllib.parse import unquote, parse_qs
import os
import threading
from socketserver import ThreadingMixIn
import os
from time import gmtime, strftime
import subprocess

try:
    import git
    if git.__version__ < '0.3.1':
        raise ImportError("Your version of git is %s. Upgrade to 0.3.1 or better." % git.__version__)
    have_git = True
except ImportError as e:
    have_git = False
    GIT_MISSING = 'Requires gitpython module, but not installed or incompatible version: %s' % e


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

subprocess.check_output('git config --global user.name \"' + my_user + '\"', 
    shell=True)

print(subprocess.check_output('git config --global user.name', 
    shell=True).decode())

subprocess.check_output('git config --global user.email \"' + my_email + '\"', 
shell=True).decode()

print(subprocess.check_output('git config --global user.email', 
shell=True).decode())

subprocess.check_output('git config --global user.password \"' + my_password + '\"', 
    shell=True).decode()

print(subprocess.check_output('git config --global user.password', 
    shell=True).decode())

print(subprocess.check_output('git config --global --list', 
    shell=True).decode())

print("user: " + my_user + "; password: " + '*****' if True else my_password)

repository_url = 'https://github.com/flauberjp/MovieTrailerWebsite'
local_repository_name = repository_url.rsplit('/', 1)[-1]
file_of_evidences = local_repository_name + '/index2.html'

if (os.path.exists(local_repository_name) == False):
    args = ['git', 'clone', repository_url]
    res = subprocess.Popen(args, stdout=subprocess.PIPE)
    output, _error = res.communicate()

print('Checking existence of \"' + file_of_evidences + '\"...')

if(os.path.exists(file_of_evidences) == False):
    print('FILE DOES NOT EXIST. Creating...') 
    with open(file_of_evidences, 'w'): 
        pass
else:
    print('FILE EXIST')

file_of_evidences = '/' +  file_of_evidences
if os.name == 'nt':
    file_of_evidences = os.getcwd() + file_of_evidences.replace('/', '\\') 
else: 
    file_of_evidences = os.getcwd() + file_of_evidences 
print('Full path: \"' + file_of_evidences + '\"...')

class ThreadHTTPServer(ThreadingMixIn, http.server.HTTPServer):
    "This is an HTTPServer that supports thread-based concurrency."

class Shortener(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if 'request' in self.path:
            if not have_git:
                print(GIT_MISSING)
            else:
                repo = git.Repo(local_repository_name) 
                print("Location "+ repo.working_tree_dir)
                print("Remote: " + repo.remote("origin").url)


                commit_message = strftime("%Y-%m-%d %H:%M:%S", gmtime())

                lastPartOfThePath = self.path.rsplit('/', 1)[-1]
                if(lastPartOfThePath != 'request'):
                    commit_message += ' ' + lastPartOfThePath

                with open(file_of_evidences, 'r+') as f:
                    content = f.read()
                    f.seek(0, 0)
                    f.write(commit_message + '<BR>' + content)
                    f.close()

                index = repo.index
                index.add([repo.working_tree_dir + '/*'])
                new_commit = index.commit(commit_message)
                origin = repo.remotes.origin
                origin.push()

        fileName = file_of_evidences
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
