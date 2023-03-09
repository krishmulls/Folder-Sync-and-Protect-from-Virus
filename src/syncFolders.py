import os
from filehash import FileHash
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import logging
import time
import trio
import shutil

def logInitializer(logPath = None):
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        log_streamer = logging.StreamHandler()
        format='%(asctime)s - %(levelname)s - %(funcName)s - %(message)s'
        formatter = logging.Formatter(format)
        log_streamer.setFormatter(formatter)
        logger.addHandler(log_streamer)
        if logPath != None:
            log_handler = logging.FileHandler(logPath + '\source.log')
            log_handler.setFormatter(formatter)
            logger.addHandler(log_handler)
        return logger

class Handler(FileSystemEventHandler):
    def on_created(self, event):
        logger = logging.getLogger( __name__ )
        logger.info(event.src_path)
        # Event is created, you can process it now
    
    def on_deleted(self, event):
        logger = logging.getLogger( __name__ )
        logger.info(event.src_path)

    def on_moved(self, event):
        logger = logging.getLogger( __name__ )
        logger.info(event.src_path)

class folderSync():

    def __init__(self):
        self.sha2hasher = FileHash('sha256')

    def folderDictGeneration(self, filepath):
        files = {}
        for dirpath, dirname, filenames in os.walk(filepath):
            for file in filenames:
                filekey =  os.path.join(dirpath, file).replace(filepath, '') # @Todo: Pls look for librarz to resolve relative path
                files[filekey] = self.sha2hasher.hash_file(os.path.join(dirpath, file))
            for dir in dirname:
                filekey =  os.path.join(dirpath, dir).replace(filepath, '')
                files[filekey] = self.sha2hasher.cathash_dir(os.path.join(dirpath, dir), pattern = '*')
        return files
    
    def copyFileSourceToDestination(self, sourceFolder, replicaFolder, changeList):
        for files in changeList:
            if os.path.isfile(sourceFolder + files):
                fileDirectory = files.rsplit('\\',1)[0]
                try:
                    shutil.copy2((sourceFolder + files), (replicaFolder + files))
                except:
                    os.mkdir(replicaFolder+fileDirectory)
                    shutil.copy2((sourceFolder + files), (replicaFolder + files))
            else:
                check = os.path.exists(replicaFolder+files)
                if not check:
                    os.mkdir(replicaFolder+files)
    
    async def folderComparison(self, sourceFolder, replicaFolder, interval,  logPath):
        logger = logInitializer(logPath)
        event_handler = Handler()
        observer = Observer()
        observer.schedule(event_handler, sourceFolder, recursive=True)
        observer.start()
        traceFiles = {}
        try:
            while True:
                modifiedList = []
                notFoundList = []
                time.sleep(interval)
                sourceFiles = self.folderDictGeneration(sourceFolder)
                replicaFiles = self.folderDictGeneration(replicaFolder)
                
                for sKey in sourceFiles:
                    if sKey in replicaFiles:
                        if sourceFiles[sKey] != replicaFiles[sKey]:
                            modifiedList.append(sKey)
                    else:
                        notFoundList.append(sKey)

                if modifiedList == [] and notFoundList == [] and sourceFiles == traceFiles:
                    logger.info('Folder Synced')
                else:
                    logger.info('Folder Not Synced')
                    if modifiedList !=[]:
                        self.copyFileSourceToDestination(sourceFolder, replicaFolder, modifiedList)
                    if notFoundList != []:
                        self.copyFileSourceToDestination(sourceFolder, replicaFolder, notFoundList)
                    if sourceFiles != traceFiles:
                        for sKey in traceFiles:
                            if sKey not in sourceFiles: 
                                if os.path.exists(replicaFolder + sKey):
                                    try:
                                        path = replicaFolder + sKey
                                        # os.chmod(path, 0o777)  # comment it if you dont want to run with admin rights
                                        shutil.rmtree(path)
                                    except:
                                        logger.error("You dont have permission to delete and therefore the folders are not sync")
                    traceFiles.clear()
                    traceFiles = sourceFiles
        finally:
            observer.stop()
            observer.join()
        

if __name__ == '__main__':
    sync_obj = folderSync()
    sourceFolder = r"D:\Workspace\Veeam\example\sourceFolder"
    replicaFolder = r"D:\Workspace\Veeam\example\replicaFolder"
    syncTime = 5
    logPath = "D:\Workspace\Veeam"
    trio.run(sync_obj.folderComparison, sourceFolder, replicaFolder, syncTime, logPath)