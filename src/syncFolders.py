"""Syncing Repository and Backup Files."""
import logging
import os
import shutil
import sys
import time

from filehash import FileHash


def logInitializer(logPath=None):
    """Intitializes the Handler and add it to logger.

    Args:
        logPath (str): Path for the log File.

    Returns:
        logger: Logger object - <Logger __main__ (INFO)>
    """

    logger = logging.getLogger(__name__)
    logger.setLevel(
        logging.INFO
    )  # Change it to DEBUG if needed detailed logs and in future we can make it dynamically set
    logStreamer = logging.StreamHandler()
    format = "%(asctime)s - %(levelname)s - %(funcName)s - %(message)s"
    formatter = logging.Formatter(
        format,
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logStreamer.setFormatter(formatter)
    logger.addHandler(logStreamer)
    if logPath != None:
        logHandler = logging.FileHandler(logPath + "\source.log")
        logHandler.setFormatter(formatter)
        logger.addHandler(logHandler)
    logger.debug("loggers has been Intialized")
    return logger


class FolderSync:
    """Class for Syncing two folders Periodically."""

    def __init__(self, loggerPath):
        self.sha2hasher = FileHash("sha256")
        self.logger = logInitializer(loggerPath)

    def checkCopy(self, file, sourceFiles, replicaFiles):
        """Check if a file is a copy from the same directory.

        Args:
            file (str): Path for the log File.
            sourceFiles (dict): Contains all the file/folder with with source folder as key and value is the hashed256 values
            replicaFiles (dict): Contains all the file/folder with with relica folder as key and value is the hashed256 values

        Returns:
            isCopiedFile (boolean): Return true if it is copied.
        """
        self.logger.debug("checkCopy has been invoked")
        isCopiedFile = False
        hashValue = sourceFiles[file]
        fileName = file.rsplit("\\", 1)[1]
        for key in replicaFiles:
            if (
                fileName in key
                or (fileName.split(" copy")[0]) in key
                or (fileName.split(" - copy")[0]) in key
            ):
                isCopiedFile = True
        if hashValue in replicaFiles.values() and isCopiedFile == True:
            isCopiedFile = True
        return isCopiedFile

    def loggingCreateCopyRemove(self, action, path, state) -> None:
        """Logs the event into console and file.

        Args:
            action (str): Has value Remove or CopyorCreate.
            path (str): Full path of the file.
            state (boolean): True if the file is copied.

        Returns:
            None
        """
        self.logger.debug("loggingCreateCopyRemove has been invoked")
        if action == "Remove":
            self.logger.info("Removed %s", path)
        if action == "CopyorCreate":
            if state == True:
                self.logger.info("Copied %s", path)
            else:
                self.logger.info("Created %s", path)

    def copyFileSourceToDestination(
        self, changeList, sourceFiles, replicaFiles
    ) -> None:
        """Copies/Creates file based on source directory to replica directory.

        Args:
            changeList (list): List of file that is modified/created.
            sourceFiles (dict): Contains all the file/folder with with source folder as key and value is the hashed256 values
            replicaFiles (dict): Contains all the file/folder with with relica folder as key and value is the hashed256 values

        Returns:
            None
        """
        self.logger.debug("copyFileSourceToDestination has been invoked")
        for files in changeList:
            check = self.checkCopy(files, sourceFiles, replicaFiles)
            if os.path.isfile(self.sourceFolder + files):
                fileDirectory = files.rsplit("\\", 1)[0]
                try:
                    shutil.copy2(
                        (self.sourceFolder + files), (self.replicaFolder + files)
                    )
                    self.loggingCreateCopyRemove(
                        "CopyorCreate", self.replicaFolder + files, check
                    )

                except:
                    fileExist = os.path.exists(self.replicaFolder + fileDirectory)
                    if not fileExist:
                        os.mkdir(self.replicaFolder + fileDirectory)
                    shutil.copy2(
                        (self.sourceFolder + files), (self.replicaFolder + files)
                    )
                    self.loggingCreateCopyRemove(
                        "CopyorCreate", self.replicaFolder + files, check
                    )
            else:
                fileExist = os.path.exists(self.replicaFolder + files)
                if not fileExist:
                    os.mkdir(self.replicaFolder + files)
                    self.loggingCreateCopyRemove(
                        "CopyorCreate", self.replicaFolder + files, check
                    )

    def deleteFolderFiles(self, sourceFiles, replicaFiles) -> None:
        """Delete file based on source directory to replica directory.

        Args:
            sourceFiles (dict): Contains all the file/folder with with source folder as key and value is the hashed256 values
            replicaFiles (dict): Contains all the file/folder with with relica folder as key and value is the hashed256 values

        Returns:
            None
        """
        self.logger.debug("deleteFolderFiles has been invoked")
        for sKey in replicaFiles:
            if sKey not in sourceFiles and os.path.exists(self.replicaFolder + sKey):
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
                    self.logger.error(
                        "You dont have permission to delete and therefore the folders are not sync"
                    )

    def fileHashDictGeneration(self, filepath):
        """Creates hash of a file or directory.

        Args:
            filepath (str): Full path of the source file or replica file.

        Returns:
            None
        """
        self.logger.debug("fileHashDictGeneration has been invoked")
        files = {}
        for dirpath, dirname, filenames in os.walk(filepath):
            for file in filenames:
                filekey = os.path.join(dirpath, file).replace(filepath, "")
                files[filekey] = self.sha2hasher.hash_file(os.path.join(dirpath, file))
            for dir in dirname:
                filekey = os.path.join(dirpath, dir).replace(filepath, "")
                files[filekey] = self.sha2hasher.cathash_dir(
                    os.path.join(dirpath, dir), pattern="*"
                )
        return files

    def folderComparison(self, sourceFolder, replicaFolder, interval) -> None:
        """Compares Repository regularly and modifies the replica file.

        Args:
            sourceFolder (str): Source Folder path to be synced.
            replicaFolder (str): Replica/Backup Folder path to be synced.
            interval (int): Minute Interval between each sync execution.
            logPath (str): Log file path.

        Returns:
            None
        """
        self.logger.debug("folderComparison has been invoked")
        self.sourceFolder = sourceFolder
        self.replicaFolder = replicaFolder
        while True:
            modifiedList = []
            notFoundList = []
            time.sleep(interval)
            sourceFiles = self.fileHashDictGeneration(self.sourceFolder)
            replicaFiles = self.fileHashDictGeneration(self.replicaFolder)

            for sKey in sourceFiles:
                if sKey in replicaFiles:
                    if sourceFiles[sKey] != replicaFiles[sKey]:
                        modifiedList.append(sKey)
                else:
                    notFoundList.append(sKey)

            if (
                modifiedList == []
                and notFoundList == []
                and sourceFiles == replicaFiles
            ):
                self.logger.info("Folder Synced")
            else:
                self.logger.info("Folder Not Synced")
                if modifiedList != []:
                    self.copyFileSourceToDestination(
                        modifiedList, sourceFiles, replicaFiles
                    )
                if notFoundList != []:
                    self.copyFileSourceToDestination(
                        notFoundList, sourceFiles, replicaFiles
                    )
                if sourceFiles != replicaFiles:
                    self.deleteFolderFiles(sourceFiles, replicaFiles)

if __name__ == "__main__":
    sourceFolder = sys.argv[1]
    replicaFolder = sys.argv[2]
    syncTime = int(sys.argv[3])
    logPath = sys.argv[4]
    syncObj = FolderSync(logPath)
    syncObj.folderComparison(sourceFolder, replicaFolder, syncTime)
