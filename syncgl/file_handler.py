
import urllib2
import base64
import os.path
import sys
from multipart_form import MultiPartForm
try:
        import simplejson
except:
        from django.utils import simplejson

from exceptions import *
import traceback

class FileHandler():

    CONFIGS = dict()
    # configuration varialble contains
    # username, password and project url

    master_files = []
    languages = [] # store the project language

    def __init__(self, basepath, **kwargs):
        self.basepath = basepath # the absolute path
        self.CONFIGS = kwargs

    def get_create_link(self):
        baseurl = self.CONFIGS.get('url')
        api_path = "api/create-master/django/"
        if baseurl.endswith('/'):
            url = baseurl + api_path 
        else:
            url = baseurl + "/" + api_path

        return url

    def get_update_link(self):
        baseurl = self.CONFIGS.get('url')
        api_path = "api/update-master"
        if baseurl.endswith('/'):
            url = baseurl + api_path 
        else:
            url = baseurl + "/" + api_path

        return url

    def get_masterlist_link(self):
        baseurl = self.CONFIGS.get('url')
        api_path = "api/list-master/json"
        if baseurl.endswith('/'):
            url = baseurl + api_path
        else:
            url = baseurl + "/" + api_path

        return url

    def set_basicauth(self, request):
        # basic AUTH set up
        username = self.CONFIGS.get("username")
        password = self.CONFIGS.get("password")
        base64string = base64.encodestring('%s:%s' % (username, password))[:-1]
        authheader =  "Basic %s" % base64string
        request.add_header("Authorization", authheader)

    def retrieve_masterfiles(self):
        """
        Retrieve the master files of this project
        """
        link = self.get_masterlist_link()
        request = urllib2.Request(link)
        self.set_basicauth(request)

        try:
            handle = urllib2.urlopen(request)
            data = handle.read()
            json = simplejson.loads(data)
            self.master_files = json.get('master_files')

            if json.get('success') == '1':
                return True, ''
            else:
                return False, json.get('error')

        except urllib2.HTTPError, e:
            if e.code == 401:
                return False, "Username or password might not be correct."
            
            return False, e.message

    def retrieve_languages(self):
        link = self.CONFIGS.get('url')
        if link.startswith("https://"): link = link[8:]
        if link.startswith("http://"): link = link[7:]
        if link.endswith('/'): link = link[:-1]

        parts = link.split('/')
        if len(parts) < 2:
            raise InvalidProjectUrlException(u"The project url is not valid. Project name is missing")

        domain = parts[0]
        project = parts[1]

        sLink = "http://%s/api/languages/?type=json&product=%s" % (domain, project)
        req = urllib2.Request(sLink)
        handle = urllib2.urlopen(req)
        self.languages = simplejson.loads(handle.read())


    def has_master(self, filepath):
        """
        Check that this file already exists
        """
        if filepath in self.master_files:
            return True
        else:
            return False

    def upload(self, filepath):
        """
        Upload the file with filepath (relative path) and retun the result
        """
        # check if this file is for updating or creating new
        if self.has_master(filepath):
            url = self.get_update_link()
            request = urllib2.Request(url)                
        else:
            url = self.get_create_link()
            url += self.CONFIGS.get("master_code")
            request = urllib2.Request(url)

        self.set_basicauth(request)

        # build form
        file = os.path.join(self.basepath, filepath)
        fhandle = open(file)
        form = MultiPartForm()        
        form.addFile('file', filepath, fhandle)
        form.addField('name', filepath)

        request.add_header("Content-Type", form.getContentType());
        request.add_data(str(form))
        
        try:            
            handle = urllib2.urlopen(request)
            data = handle.read()
           
            if data.startswith('Success'):
                return True, ''
            else:
                return False, data
        
        except urllib2.HTTPError, e:
            return False, 'Issue with remote server. Status code %s' % e.code

        except Exception, e:
            return False, 'Unexpected error: %s' % e.message

        return True, ''

    def save_file_from_link(self, link, filepath):
        """
        Download the file from the link and save it as the filepath relative to the basepath.
        If the same file does exist, this will overwrite it
        """
        request = urllib2.Request(link)
        data = urllib2.urlopen(request).read()

        path = os.path.join(self.basepath, filepath)
        f = open(path, "wb+")
        f.write(data)
        f.close()

    def get_target_filepath(self, filepath, langcode):
        """
        Generate the filepath for the target language. The method is to replace the
        pattern mastercode/LC_MESSAGGES -> langcode/LC_MESSAGES. This is to prevent
        the master code can be found in the filepath.
        Then generate the missing folders in the file path
        """
        pattern = os.path.join(self.CONFIGS.get("master_code"), "LC_MESSAGES")
        target_pattern = os.path.join(langcode, "LC_MESSAGES")
        target_filepath = filepath.replace(pattern, target_pattern)

        # to make it consistent, all backslash will be converted to forward slash
        target_filepath = target_filepath.replace('\\', '/')
        folders = target_filepath.split('/')
        if len(folders) == 1: # if no slash in the filepath, no need to process
            return

        # create the missing folder
        basepath = self.basepath
        for folder in folders[:-1]:
            basepath = os.path.join(basepath, folder)
            if not os.path.exists(basepath):
                os.mkdir(basepath)

        return target_filepath

    def download(self, filepath, langcode):
        """
        Download the file in target language of a component.
        If that such language does not exist then create a new one
        """
        baseurl = self.CONFIGS.get('url')
        if baseurl.endswith('/'):
            link =  baseurl + 'api/translations/' + langcode
        else:
            link =  baseurl + '/api/translations/' + langcode

        request = urllib2.Request(link)
        self.set_basicauth(request)
        form = MultiPartForm()        
        form.addField('name', filepath)
        request.add_header("Content-Type", form.getContentType());
        request.add_data(str(form))

        try:
            handle = urllib2.urlopen(request)
            data = simplejson.loads(handle.read())

            if data.get('success') == 1:
                generated_link = data.get('link')
                lang_filepath = self.get_target_filepath(filepath, langcode)
                self.save_file_from_link(generated_link, lang_filepath)

                return True, 'Success'

            else:
                return False, data.get("error")

        except urllib2.URLError, e:
            sys.stdout.write("Issue with remote server. Status code: %s\n" % e.code)

        except Exception, e:
            sys.stdout.write("Unexpected error: %s" % e.message)






