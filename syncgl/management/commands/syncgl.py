

from django.core.management.base import BaseCommand, CommandError
import sys
import os.path

path = os.path.join(os.path.abspath(os.path.dirname(__file__)), os.pardir, os.pardir)
sys.path.append(path)

from crawler import *
from file_handler import *
try:
    from settings import GL_USERNAME
except:
    sys.stdout.write("GL_USERNAME setting is not defined.\n")
    sys.exit()
     
try:
    from settings import GL_PASSWORD
except:
    sys.stdout.write("GL_PASSWORD setting is not defined\n")
    sys.exit()
    
try:
    from settings import GL_PROJECT_URL
except:
    sys.stdout.write("GL_PROJECT_URL setting is missing\n")
    sys.exit()

try:
    from settings import GL_MASTER_IANA_CODE
except:
    GL_MASTER_IANA_CODE = "en"

class Command(BaseCommand):
    args = '<None>'
    help = 'Synchronize with Get Localization service'

    def handle(self, *args, **options):

        sys.stdout.write("==================================\n")
        sys.stdout.write("Start synchronizing localization files with Get Localization service....\n\n")
        
        # find all the master language file in all folder, ones with /locale/en/LC_MESSAGE/django.po
        project_path = os.path.abspath(os.path.dirname(sys.argv[0]))
        fc  = FileCrawler(project_path, "en")
        fc.start()        

        project_url = GL_PROJECT_URL
        if not project_url.startswith('https://'):
            project_url = project_url.replace('http', 'https')

        fh = FileHandler(project_path,
                    master_code=GL_MASTER_IANA_CODE,
                    username=GL_USERNAME,
                    password=GL_PASSWORD,
                    url=project_url)

        # retrieve the project master files
        success, message =  fh.retrieve_masterfiles()
        if not success:
            sys.stdout.write("ERROR: %s\n" % message)
            sys.exit(1)

        try:
            fh.retrieve_languages()            
        except urllib2.HTTPError, e:
            sys.stdout.write("ERROR: Issue with the remote server. Status code %s" % e.code)

        except Exception, e:
            sys.stdout.write(e.message)
            sys.exit()
        
        for filepath in fc.results:
            if fh.has_master(filepath):
                sys.stdout.write("Updating localization file %s" % filepath)
            else:
                sys.stdout.write("Uploading new localization file %s" % filepath)

            # start uploading the file
            success, message = fh.upload(filepath)
            if success:
                sys.stdout.write(' [OK]\n')
            else:
                sys.stdout.write(' **FAIL: %s\n' % message)
        
        # download the file in different language
        for lang in fh.languages:
            for masterfile in fh.master_files:
                if not masterfile.endswith('.po'):
                    continue
                    
                sys.stdout.write("Downloading %s for %s" % (masterfile, lang[1]))
                
                success, message = fh.download(masterfile, lang[0])
                if success:
                    sys.stdout.write(' [OK] \n')
                else:
                    sys.stdout.write(" **FAIL: %s\n" % message)

        sys.stdout.write("\n\nCompiling the language file to .mo files. Make sure your PYTHONPATH is set up properly\n")
        os.system("django-admin.py compilemessages")