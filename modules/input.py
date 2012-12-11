'''
Created on Sep 30, 2012

@author: salnikov
'''

import os
import logging
import zipfile

_log = logging.getLogger(__name__)

class MultipleFiles(RuntimeError):
    '''Class for exceptions generated when there is more than one file 
    matching specified criteria.
    '''  
    def __init__(self, msg):
        RuntimeError.__init__(self, msg)

class _FileLocator(object):
    '''
    Interface for different kinds of file locators.
    '''
    
    def openXML(self):
        '''
        Returns file object for the input XML file. 
        
        If no XML file is found the None is returned. If more than one XML file is 
        found than MultipleFiles exception is raised. Can throw other exceptions 
        if file cannot be open. 
        Note that this file object may not support all operations (it may be an 
        object inside zip file for example) so you may need to copy it if you want 
        full file protocol support.
        '''
        raise NotImplementedError("Method _FileLocator.openXML() is not implemented")
    
    def openImage(self, name):
        '''
        Returns file object for the named image file. 
        
        If image file is not found the None is returned. If more than one matching file is 
        found than MultipleFiles exception is raised. Can throw other exceptions 
        if file cannot be open.
        Note that this file object may not support all operations (it may be an 
        object inside zip file for example) so you may need to copy it if you want 
        full file protocol support.
        '''
        raise NotImplementedError("Method _FileLocator.openImage() is not implemented")
    

class _FSLocator(_FileLocator):
    '''
    Implementation of _FileLocatorinterface which can find files located
    on a regular filesystem.
    '''
    
    def __init__(self, inputFile, imgdir=None):
        '''
        Constructor takes one required argument which can be either file name
        or file-like object. Optional argument imgdir specifies location of image files.
        If `imgdir` is not specified or None then images are looked up in the same 
        directory as XML file or its sub-directories.
        '''
        
        self._inputFile = inputFile
        self._imgdir = imgdir
        self._images = None
        
    def openXML(self):
        '''Returns file object for the input XML file.'''
        
        _log.debug("_FSLocator.openXML")
        if hasattr(self._inputFile, 'read'):
            # it's likely a file
            return self._inputFile
        else:
            return open(self._inputFile, 'rU')
    
    def openImage(self, name):
        '''Returns file object for the named image file.''' 
     
        _log.debug("_FSLocator.openImage: find image "+name)

        if self._imgdir:
            if self._images is None:
                # make the list of files in the image directory
                _log.debug("_FSLocator.openImage: scan directory "+self._imgdir)
                self._images = os.listdir(self._imgdir)
            if name in self._images:
                path = os.path.join(self._imgdir, name)
                _log.debug("_FSLocator.openImage: found "+path)
                return open(path, 'rb')
            _log.debug("_FSLocator.openImage: nothing found")
        else:
            if self._images is None:
                # make the list of files in the XML directory and all sub-directories
                if hasattr(self._inputFile, 'read'):
                    self._images = []
                else:
                    dir = os.path.dirname(self._inputFile)
                    _log.debug("_FSLocator.openImage: recursively scan directory "+dir)
                    self._images = list(os.walk(dir))
            matches = [os.path.join(dir, name) for dir, x, files in self._images if name in files]
            if not matches:
                _log.debug("_FSLocator.openImage: nothing found")
                return
            elif len(matches) > 1:
                _log.debug("_FSLocator.openImage: many files found: " + str(matches))
                raise MultipleFiles('More than file matches name '+name)
            else:
                _log.debug("_FSLocator.openImage: found: " + matches[0])
                return open(matches[0], 'rb')
            

class _ZipLocator(_FileLocator):
    '''
    Implementation of _FileLocatorinterface which can find files located
    in zip archive.
    '''
    
    def __init__(self, inputFile):
        '''
        Constructor takes one required argument which can be either file name
        or file-like object.
        '''
        
        # read zip file contents
        self._zip = zipfile.ZipFile(inputFile, 'r')
        self._toc = self._zip.namelist()
        
    def openXML(self):
        '''Returns file object for the input XML file.'''

        xmls = [f for f in self._toc if f.endswith(('.xml', '.XML'))]
        if not xmls: return None
        if len(xmls) > 1: raise MultipleFiles('Multiple XML files found in archive')
        _log.debug("_ZipLocator.openXML: "+xmls[0])
        return self._zip.open(xmls[0], 'rU')

    
    def openImage(self, name):
        '''Returns file object for the named image file.''' 
     
        _log.debug("_FSLocator.openImage: find image "+name)

        paths = [f for f in self._toc if os.path.basename(f) == name]
        if not paths: return None
        if len(paths) > 1: raise MultipleFiles('Multiple image files found in archive matching name '+name)
        _log.debug("_ZipLocator.openImage: "+paths[0])
        return self._zip.open(paths[0], 'r')

def FileLocator(inputFile, **kw):
    '''
    For a given input file (which can be XML file or some archive) return
    corresponding file locator (file factory) object. Argument
    can be either file name of file-like object.
    
    Optional keyword arguments accepted:
    imagedir: location of the image files, only makes sense if input is XML file,
              if not given then images are searched in the same directory as XML 
            file or its sub-directories
    '''
    
    if zipfile.is_zipfile(inputFile):
        return _ZipLocator(inputFile)
    elif hasattr(inputFile, 'read'):
        inputFile.seek(0)
        return _FSLocator(inputFile, kw.get('imagedir', None))
    elif os.path.exists(inputFile):
        return _FSLocator(inputFile, kw.get('imagedir', None))
    else:
        return None
