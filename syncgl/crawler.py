"""
Copyright (c) 2011, Synble Ltd 
All rights reserved. 

Redistribution and use in source and binary forms, with or without modification, 
are permitted provided that the following conditions are met: 

    1. Redistributions of source code must retain the above copyright notice, 
       this list of conditions and the following disclaimer. 
     
    2. Redistributions in binary form must reproduce the above copyright 
       notice, this list of conditions and the following disclaimer in the 
       documentation and/or other materials provided with the distribution. 

    3. Neither the name of Synble nor the names of its contributors may be used 
       to endorse or promote products derived from this software without 
       specific prior written permission. 

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND 
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED 
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE 
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR 
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES 
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; 
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON 
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT 
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS 
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE. 
"""

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





