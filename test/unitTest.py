import unittest

from src.syncFolders import FolderSync


class TestSync(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        print("Starting Unit Testing")

    def setUp(self):
        self.sourceFiles = {
            "\\test.py": "ea9b48a59278d7b127024cf9bdcc5f9a63ccdd3eaf2f0f332c0b5369b69ad4d8",
            "\\dummy": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        }
        self.replicaFiles = {
            "\\test.py": "ea9b48a59278d7b127024cf9bdcc5f9a63ccdd3eaf2f0f332c0b5369b69ad4d8",
            "\\dummy": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
        }
        self.files = {
            "\\test.py": "ea9b48a59278d7b127024cf9bdcc5f9a63ccdd3eaf2f0f332c0b5369b69ad4d8",
            "\\dummy": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
            }
        self.sourceFolder = "D:\\workspace\\Veeam\\test\\sourceFolder"
        self.file = "\\test.py"

    def testCopyFunctionCheck(self):
        print("Testing the copying Functionality.")
        testObj = FolderSync()
        result = testObj.checkCopy(self.file, self.sourceFiles, self.replicaFiles)
        self.assertEqual(result, True)

    def testHashFunctionCheck(self):
        print("Testing the Hashing Functionality.")
        testObj = FolderSync()
        result = testObj.fileHashDictGeneration(self.sourceFolder)
        self.assertEqual(result, self.files)


if __name__ == "__main__":
    unittest.main()
