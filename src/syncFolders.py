import os
from filehash import FileHash
import logging
import time
import trio
import shutil

def logInitializer(logPath = None):
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        log_streamer = logging.StreamHandler()
        format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s'
        formatter = logging.Formatter(format, datefmt='%Y-%m-%d %H:%M:%S',)
        log_streamer.setFormatter(formatter)
        logger.addHandler(log_streamer)
        if logPath != None:
            log_handler = logging.FileHandler(logPath + '\source.log')
            log_handler.setFormatter(formatter)
            logger.addHandler(log_handler)
        return logger

class folderSync():

    def __init__(self):
        self.sha2hasher = FileHash('sha256')

    def fileHashDictGeneration(self, filepath):
        files = {}
        for dirpath, dirname, filenames in os.walk(filepath):
            for file in filenames:
                filekey =  os.path.join(dirpath, file).replace(filepath, '') # @Todo: Pls look for librarz to resolve relative path
                files[filekey] = self.sha2hasher.hash_file(os.path.join(dirpath, file))
            for dir in dirname:
                filekey =  os.path.join(dirpath, dir).replace(filepath, '')
                files[filekey] = self.sha2hasher.cathash_dir(os.path.join(dirpath, dir), pattern = '*')
        return files
    
    def checkCopy(self, file):
        self.copiedfile = False
        hashValue = self.sourceFiles[file]
        if hashValue in self.replicaFiles.values() and hashValue != "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855":
            self.copiedfile = True
        return self.copiedfile

    def loggingCreateCopyRemove(self, action, path, state):
        if action == "Remove":
            self.logger.info("Removed a folder %s", path)
        if action == "CopyorCreate":
            if state == True:
                self.logger.info("Copied a file %s", path)
            else:
                self.logger.info("Created a file %s", path)

    
    def copyFileSourceToDestination(self, changeList):
        for files in changeList:
            check = self.checkCopy(files)
            if os.path.isfile(self.sourceFolder + files):
                fileDirectory = files.rsplit('\\',1)[0]
                try:
                    shutil.copy2((self.sourceFolder + files), (self.replicaFolder + files))
                    self.loggingCreateCopyRemove("CopyorCreate", self.replicaFolder + files, check)
                    
                except:
                    fileExist = os.path.exists(self.replicaFolder+fileDirectory)
                    if not fileExist:
                        os.mkdir(self.replicaFolder+fileDirectory)
                    shutil.copy2((self.sourceFolder + files), (self.replicaFolder + files))
                    self.loggingCreateCopyRemove("CopyorCreate", self.replicaFolder + files, check)
            else:
                fileExist = os.path.exists(self.replicaFolder+files)
                if not fileExist:
                    os.mkdir(self.replicaFolder+files)
                    self.loggingCreateCopyRemove("CopyorCreate", self.replicaFolder + files, check)

    def deleteFolderFiles(self):
        for sKey in self.replicaFiles: 
            if sKey not in self.sourceFiles and os.path.exists(self.replicaFolder + sKey): 
                try:
                    path = self.replicaFolder + sKey
                    # os.chmod(path, 0o777)  # uncomment it if you want to run with admin rights
                    if os.path.isfile(path):
                        os.remove(path)
                        self.logger.info("Removed a file %s", path)
                    else:
                        shutil.rmtree(path)
                        self.loggingCreateCopyRemove("Remove", path, False)
                except:
                    self.logger.error("You dont have permission to delete and therefore the folders are not sync")
    
    async def folderComparison(self, sourceFolder, replicaFolder, interval,  logPath):
        self.logger = logInitializer(logPath)
        self.sourceFolder = sourceFolder
        self.replicaFolder = replicaFolder
        while True:
            modifiedList = []
            notFoundList = []
            time.sleep(interval)
            self.sourceFiles = self.fileHashDictGeneration(self.sourceFolder)
            self.replicaFiles = self.fileHashDictGeneration(self.replicaFolder)
            
            for sKey in self.sourceFiles:
                if sKey in self.replicaFiles:
                    if self.sourceFiles[sKey] != self.replicaFiles[sKey]:
                        modifiedList.append(sKey)
                else:
                    notFoundList.append(sKey)

            if modifiedList == [] and notFoundList == [] and self.sourceFiles == self.replicaFiles: 
                self.logger.info('Folder Synced')
            else:
                self.logger.info('Folder Not Synced')
                if modifiedList !=[]:
                    self.copyFileSourceToDestination(modifiedList)
                if notFoundList != []:
                    self.copyFileSourceToDestination( notFoundList)
                if self.sourceFiles != self.replicaFiles: 
                    self.deleteFolderFiles()


if __name__ == '__main__':
    sync_obj = folderSync()
    sourceFolder = r"D:\workspace\Veeam\example\sourceFolder"
    replicaFolder = r"D:\workspace\Veeam\example\replicaFolder"
    syncTime = 5
    logPath = "D:\workspace\Veeam"
    trio.run(sync_obj.folderComparison, sourceFolder, replicaFolder, syncTime, logPath)