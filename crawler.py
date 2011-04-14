import os.path
import os
import sys

class FileCrawler():

    results = [] # store the list of found master files path

    """
    Scan the whole project directories to find the master localization files.
    The master files are defined by all files .po within the directory "/<mastercode>/LC_MESSAGES"
    """
    def __init__(self, basepath, mastercode):
        """
        Define the starting root directory path and the master language code
        """
        self.basepath = basepath
        self.mastercode = mastercode

    def capture_po_files(self, relative_path):
        """
        Capture all po files within this path
        """
        path = os.path.join(self.basepath, relative_path)
        # check if this path exist
        if not os.path.exists(path):
            return

        for file in os.listdir(path):
            if file.endswith('.po'):
                filepath = os.path.join(relative_path, file)
                self.results.append(filepath)

    def scan(self, relative_path):
        """
        Start the scanning process in the path
        """
        #sys.stdout.write("Scanning directory %s\n" % basepath)
        
        # find all files within basepath
        path = os.path.join(self.basepath, relative_path)
        for file in os.listdir(path):
            filepath = os.path.join(path, file)
            if os.path.isdir(filepath) and not file.startswith('.'): # only deal with folder
                if file == self.mastercode:
                    folderpath = os.path.join(relative_path, file, "LC_MESSAGES")  # for clarity
                    self.capture_po_files(folderpath) # capture all po files inside this directoyy
                else:
                    next_folder = os.path.join(relative_path, file)
                    self.scan(next_folder)

    def start(self):
        self.scan(".") # start from base path





