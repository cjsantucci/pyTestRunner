'''
Created on Jul 11, 2020

@author: Brook Duran
'''
import os 
import sys
import traceback
import warnings
import re
import inspect
from PyClassUtil import PyClassHelper, findClassesOfCertainTypeInPackage, upperSortedKeys

 


class testCollector(PyClassHelper):
    '''
    classdocs
    '''
    _propertyDict= { "_testList":[],"_testFileList":[], "_testPath":".."}
    def __init__(self, *args, **kwargs):
        '''
        Constructor
        '''
        PyClassHelper.__init__(self 
                       ,defaultsDict= testCollector._propertyDict 
                       , *args
                       , **kwargs )
    
        
        self._setTestPath(**kwargs)
        self._findTestFiles()
        
    @property
    def testPath(self, *args, **kwargs):
        return self._testPath

    def _setTestPath(self, testPath = None, **kwargs):
        if testPath is not  None:
            assert isinstance(testPath, str)
            self._testPath = testPath
            assert os.path.exists(self.testPath)
    
    @property
    def testList(self,*args, **kwargs):
        return self._testList.copy()
    
    @property
    def testFileList(self,*args, **kwargs):
        return self._testFileList.copy()
    
    def _determineIfClassIsTestClass(self, aFile):
        
        
        return False
        
    
    def _findTestFiles(self, *args, **kwargs):
        for root, dirs, files in os.walk(self.testPath):
            for aFile in files:
                if aFile.endswith(".py"):
                    if self._determineIfClassIsTestClass(os.path.join(root, aFile)):
                        self._testFileList.append(os.path.join(root, aFile))
        
if __name__ == "__main__":
    testObj = testCollector(testPath = "..")
    testObj.useRepr= True
    print(testObj)