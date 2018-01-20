import requests
import tempfile
from django.core.files import File

class CuckooServer(object):

    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

def submit_task(server, name, file_handle):
    url = 'http://{ip}:{port}/tasks/create/file'.format(ip=server.ip, port=server.port)
    files = {'file': (name, file_handle)}
    data = {
        'options' : 'procmemdump=yes',
        'package' : 'exe',
        #'timeout' : 60,
        #'enforce_timeout' : True,
    }
    response = requests.post(url, files=files, data=data)
    return response.json()['task_id']


def get_status(server, task_id):
    url = 'http://{ip}:{port}/tasks/view/{task_id}'.format(ip=server.ip, port=server.port, task_id=task_id)
    response = requests.get(url)

    # See http://cuckoo.readthedocs.org/en/latest/usage/api/#tasks-view for a description of what is returned here.
    # I also added a new dict entry called ret_val['msg'], which provides info about current status.
    # To check if the job is done, you'll want to check that ret_val['status'] == 'completed'.
    return response.json()['task']

def get_report(server, task_id):
    url = 'http://{ip}:{port}/tasks/report/{task_id}'.format(ip=server.ip, port=server.port, task_id=task_id)
    response = requests.get(url)
    return response.json()

def get_procdump(server, task_id):

    # NOTE: This api is not available yet in stock Cuckoo and relies on our own patch.
    url = 'http://{ip}:{port}/memory/get/{task_id}'.format(ip=server.ip, port=server.port, task_id=task_id)
    response = requests.get(url)

    # We create a Django File to be compatible with uploaded files.  The file store in this case will be memory
    # based, since the file will be written to disk by the FileField in the BinaryFile model.
    # NOTE: Since we are we using a SpooledTemporaryFile, we must be sure that the file handle is not closed until the
    #       FileField saves it to more permanent storage.
    f = File(tempfile.SpooledTemporaryFile())
    for chunk in response.iter_content(1024):
        f.write(chunk)

    return f
