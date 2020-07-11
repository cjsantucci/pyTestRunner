'''
Created on Jul 3, 2019

@author: z1085043
'''
from builtins import isinstance
import collections
import importlib
import inspect as INSP
import re
import reprlib as RL
import os
import traceback
import warnings

class PyClassHelper(object):
    '''
    This class helps with property initialization and nice printing of classes for debug or understanding and other helper functions
    The basic idea is that you give it a default dictionary with all of the keys beginning with "_"
    If there is a property of the class which does has the same name without the underscore
    This class will conveniently print everything if you set the properties to use print with __repr__
    In this way you can get a print out of the interfaces of the class easily
    '''
    _Global_Use_Repr= False
    _Global_Num_Dashes= 50
    
    def __init__(self, *args, \
                 defaultsDict= None, \
                 **kwargs):
        
        assert defaultsDict is not None, "must use defaultsDict when inheriting from this class"
        ensureInstance( defaultsDict, dict )
        self.defaultsDict= defaultsDict
        
        self._useRepr= False
        self._setDefaultClassData(**kwargs)
    
    def _setDefaultClassData(self, **kwargs):
        selfDir= dir(self)
        for aKey in self.defaultsDict:
            assert aKey[0] == "_", "Default dict word must begin with \"_\""
            
            if (aKey[0] == "_") \
            and (aKey.lstrip("_") in selfDir) \
            and (aKey.lstrip("_") in kwargs.keys()) \
            and hasattr(self, aKey.lstrip("_")):
                setattr( self, aKey.lstrip("_"), kwargs[aKey.lstrip("_")]  )
            else:
                setattr( self, aKey, self.defaultsDict[aKey] )

    def _setBools(self, boolList, *args, **kwargs):
        
        propertiesWithUnderScore = determinePropertiesWithUnderscore( self )
        
        for aBool in boolList:
            if aBool not in propertiesWithUnderScore:
                warnings.warn("will unable to set--not a property: " + aBool)
                traceback.print_stack()
        
        kwKeyList = sorted(list(kwargs.keys()))
        setBoolList = [ aBool for aBool in boolList if aBool in kwKeyList ]
        
        for aBool in setBoolList:
            ensureInstance(kwargs[aBool], bool, level = 2)
            setattr(self,"_" + aBool, kwargs[aBool])
            
        return
        
    
    def _defaultHexString(self):
        return str(self.__class__) + " at " + hex(id(self))
    
    def __str__(self, *args, **kwargs):
        if not (self.useRepr or PyClassHelper._Global_Use_Repr):
            return self._defaultHexString()
        else:
            return self.__repr__()
    
    def __repr__(self, *args, **kwargs):
        """ususally for debug"""
        props2repr= determinePropertiesWithUnderscore( self )
        if props2repr is None:
            return object.__str__(self, *args, **kwargs)
        
        outStrList=[]
        outStrList.append( "-"*PyClassHelper._Global_Num_Dashes )
        for aProp in props2repr:
            outStrList.append( aProp + ": " + RL.repr(getattr(self,aProp)))
        
        outStrList.append( "-"*PyClassHelper._Global_Num_Dashes )
        
        return "\n".join(outStrList)
        
    
    def _getUseRepr(self):
        return self._useRepr
    
    def _setUseRepr(self, inVal):
        """property which indicates whether to use __repr__ or __str__ method for debug"""
        if isinstance( inVal, bool):
            self._useRepr= inVal
        elif isinstance( inVal, str ):
            assert inVal.upper() == "GLOBAL", "use_repr must be value of global when set as a string"
            PyClassHelper._Global_Use_Repr= True
        else:
            assert False, "use_repr must be assigned a bool or a string \"global\""
    
    useRepr= property( _getUseRepr, _setUseRepr  )

def determinePropertiesWithUnderscore( inObj ):
    """figure out all of the PROPERTIES which begin with a single underscore"""
    dirSelf= dir(inObj)
    underScoreProps= beginsWithSingleUnderscore(dirSelf)
    props2repr= []
    for aProp in underScoreProps:
        noUnder= aProp[1:]
        if (noUnder in dirSelf) and \
            ( hasattr(inObj.__class__, noUnder) and isinstance(getattr(inObj.__class__, noUnder), property) ):
            props2repr.append(noUnder)
    
    if len( props2repr ) > 0:
        return props2repr
    else:
        return None
    
def determineKeysWithUnderscore(inDict):
    ensureInstance(inDict, dict, level=2 )
    underScoreKeys= beginsWithSingleUnderscore(sorted(list(inDict.keys())))
    return underScoreKeys

def beginsWithSingleUnderscore( inList ):
    """helper to check to make sure that the input lists is made of strings which all begin with an underscore"""
    ensureInstance( inList, list, level=2 )
    for anElement in inList:
        assert isinstance( anElement, str ), "inList must be string"
    
    outList= []
    
    for anElement in inList:
        if len( anElement ) >= 2 and anElement[0] == "_" and anElement[1] != "_":
            outList.append( anElement )
            
    return outList

def ensureInstance( inVal, inType, level=1 ):
    """ check the instance of the type is correct for the caller. 1 is the caller """
    
    stk= INSP.stack()
    filename= stk[level].filename
    function= stk[level].function
    lineno= stk[level].lineno
    
    assert isinstance( inVal, inType ), \
        "isinstance assertion failed -- "\
        + "function: \"" + function + "\", line: " + str(lineno) \
        + ", in file: " + filename     
    
    
def upperSortedKeys( inDict ):
    """ helper to return sorted dict keys as a list in all upper case"""
    
    ensureInstance(inDict, dict)
    dKeys= list( inDict.keys() )
    
    for keyIdx, aKey in enumerate( dKeys ):
        dKeys[keyIdx]= aKey.upper()
        
    return sorted(dKeys)

def findClassesOfCertainTypeInPackage( inFile, testObj, excludeTestObject= True ):
    """ find the classes which contain the testObj in their class tree """
    
    assert INSP.isclass(testObj), "input must be a class obj (not instance)"
    testObjStrTuple= getPackageModuleClassStr(testObj)
    
    moduleDict= find_modules(inFile)
    
    classInfo = collections.namedtuple('classInfo', 'file modObj classObj packageName moduleName className')
    
    outList= []
    for aModuleFile in moduleDict:
        modObj= moduleDict[aModuleFile]
        tempStr= getPythonObjectStrInQuotes( modObj )
        pkgStr= tempStr.split(".")[0]
        modStr= tempStr.split(".")[1]
        
        
        for anAttr in dir(modObj):
            loadedAttr= getattr( modObj, anAttr )
            if determineIfInClassTree( testObj, loadedAttr ):
                classStrTuple= getPackageModuleClassStr(loadedAttr)
                ciTuple= classInfo( file= aModuleFile, modObj=modObj, classObj= loadedAttr\
                                    , packageName= classStrTuple.packageName \
                                    , moduleName= classStrTuple.moduleName \
                                    , className= classStrTuple.className )
                
                # skip the test object
                if ((ciTuple.className == testObjStrTuple.className) and excludeTestObject):
                    continue 
                
                # make sure the source of the class is the same python file.
                if pkgStr == ciTuple.packageName:
                    outList.append( ciTuple )
    
    return outList

def getPythonObjectStrInQuotes( inObj ):
    """get the class string for use"""
    classStr= str(inObj)
    reMatch= re.match( ".*?'(.*?)'.*", classStr )
    return reMatch.groups()[0]

def getPackageModuleClassStr( inClassObj ):
    """return a named tuple of the python module, class, etc. info for specific classObjs"""
    tempStr= getPythonObjectStrInQuotes( inClassObj )
    tempList= tempStr.split(".")

    classStrTuple = collections.namedtuple('classStrTuple', 'fullname packageName moduleName className')

    return classStrTuple( fullname= tempStr, packageName= tempList[0], moduleName= tempList[1], className= tempList[2] )

def determineIfInClassTree( testObj, searchObj ):
    """ try to see if the testObj is in the searchObj class tree """
    if not INSP.isclass( searchObj ):
        return False
    
    allBases= INSP.getmro( searchObj )
    for aBase in allBases:
        if aBase is testObj:
            return True
        
    return False

def determinePackage(inFile):
    """figure out if it's a package"""
    fileDir= os.path.dirname(inFile)
    files= os.listdir(fileDir)
    
    pkgName= None
    if "__init__.py" in files:
        pkgName= os.path.basename(fileDir)

    return pkgName

def find_modules(inFile):
    """get a dictionary that associates files to their respective dynamically imported module"""
    pkgName= determinePackage(inFile)
    fileDir= os.path.dirname(inFile)
    files= os.listdir(fileDir)
    
    files= [ os.path.join( fileDir, aFile) for aFile in files if aFile.endswith(".py") ]
    
    moduleDict= {}
    for aFile in files:
        fileNoExtName= os.path.basename(aFile)[:-3]
        
        
        if pkgName is None:
            modObj= importlib.import_module( fileNoExtName, fileDir )
        else:
            pkgAndFile= ".".join( [pkgName, fileNoExtName] )
            modObj= importlib.import_module( pkgAndFile, os.path.dirname(fileDir) )
        
        moduleDict[aFile]= modObj
        
    return moduleDict  
     