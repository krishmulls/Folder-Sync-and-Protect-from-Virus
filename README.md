Welcome Recruiting Team:
==============================

The program syncFolders.py is written in order to synchronize two folders: source and replica. The program should maintain a full, identical copy of the source folder in the replica folder.

**Practical Scenario Assumed**: Assume this is for the Backup of the main environment (Production or Development) System Files to be error free mirror copy of the main environment

### Below are the satisfied condition: (All the mentioned Constrains written with base code required in python without third-party library)


1. Synchronization must be one-way: after the synchronization content of the replica folder should be modified to exactly match the content of the source folder;
2. Synchronization should be performed periodically.
3. File creation/copying/removal operations should be logged to a file and to the console output;
4. Folder paths, synchronization interval, and log file paths should be provided using the command line arguments;
5. It is undesirable to use third-party libraries that implement folder synchronization;
6. It is allowed (and recommended) to use external libraries implementing other well-known algorithms. For example, there is no point in implementing yet another function that calculates MD5 if you need it for the task – it is perfectly acceptable to use a third-party (or built-in) library.


### Few Detailed Explanations:

1. Event trigger is not used because it would not make sense to log comments other than synchronization time. This might cause harm when the repository is big and sync time is less. Therefore, Periodically check the file and logs the event based on logic for events mentioned - created, copied and removed.
2. Tried Async process flow. it works well as well but this can cause harm when big repositories and threads are not handled properly. Therefore Removed it for final submission. 
3. When a file is newly copied into the repository is stated as created, when an existing file in the repository is copied into the directory it states copied, newly created is stated as created, if the file is moved it states copied and deleted and deleted or removed is stated removed. 
4. The above point is done because it periodically checks the repository and assigns the state.


### Extra Activities for Consideration:

1. Setup up unit testing which can be further improved and facilitated Continuously Integration and development.
2. Created a simple CI Pipeline.
3. Used Google Documentation style for python


### To Run the File:

(Python Executable File) (File Path - syncFolders.py) (SourceFolder) (ReplicaFolder/BackupFolder) (Sync Time Interval) (Logfile Path)

**For Example**: python.exe  d:\Workspace\Veeam\src\syncFolders.py  d:\workspace\Veeam\example\sourceFolder  d:\workspace\Veeam\example\replicaFolder  5 d:\workspace\Veeam

### Executed Proof:

![Test](https://github.com/krishmulls/Veeam/blob/68e14c1dfc9315f9771b5d7157bbc84e1dbd24d6/example/sourceFolder/testProofImageSync.png)
