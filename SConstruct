
import os

class Architecture(object):
  
  def __init__(self):
    
    import platform
    import SCons
    
    self.__osName = platform.system()
    self.__pythonVersion = platform.python_version()
    self.__sconsVersion = SCons.__version__
    
    if self.__osName not in self.supportedSystems:
      raise RuntimeError('Unsupported OS architecture.')
    
    self.__sysDirName = 'unknown'
    if self.isLinux:
      self.__sysDirName = 'linx64'
      if not 'LD_LIBRARY_PATH' in os.environ:
          os.environ['LD_LIBRARY_PATH'] = ''
    elif self.isWindows:
      self.__sysDirName = 'winx64'
    
  
  @property
  def supportedSystems(self):
    return ['Windows', 'Linux']
  
  @property
  def osName(self):
    return self.__osName
  
  @property
  def isWindows(self):
    return self.osName == 'Windows'
  
  @property
  def isLinux(self):
    return self.osName == 'Linux'
  
  @property
  def pythonVersion(self):
    return self.__pythonVersion
  
  @property
  def sconsVersion(self):
    return self.__sconsVersion
  
  @property
  def sysDirName(self):
    return self.__sysDirName
  
  def summary(self):
    import sys
    lstr = '='*50 + '\n'
    lstr += 'Architecture Summary\n'
    lstr += '='*50 + '\n'
    lstr += 'operating system: ' + self.osName        + '\n'
    lstr += 'python version:   ' + self.pythonVersion + '\n'
    lstr += 'scons version:    ' + self.sconsVersion  + '\n'
    lstr += 'path:             ' + str(os.environ['PATH'].split(os.pathsep)) + '\n'
    if self.isLinux:
      lstr += 'LD_LIBRARY_PATH:  ' + str(os.environ['LD_LIBRARY_PATH'].split(os.pathsep) )+ '\n'
    if os.environ.get('PYTHONPATH'):
      lstr += 'python path:      ' + str(os.environ['PYTHONPATH'].split(os.pathsep)) + '\n'
    lstr += 'session python path: ' + str(sys.path).replace(', ', ',\n' + ' ' * 26) + '\n'
    lstr += '-'*50 + '\n'
    return lstr
  

class BuildPath(object):
  
  def __init__(self,
               archObj):
    
    from SCons.Script import Dir
    
    # main
    self.__srcDir = Dir('#').abspath
    
    __grpcInstall = os.path.join(self.__srcDir,
                                 'grpc_install',
                                 archObj.sysDirName)
    
    self.__protocExePath = os.path.join(__grpcInstall,
                                        'bin',
                                        'protoc')
    self.__grpcIncludePaths = [os.path.join(__grpcInstall, 'include')]
    self.__grpcLibPaths = [os.path.join(__grpcInstall, 'lib'),
                           os.path.join(__grpcInstall, 'lib64')]
    
    def _exist(path):
      if not os.path.exists(path):
        os.makedirs(path)
      return path
    
    # build variables
    self.__buildDir = _exist(os.path.join(self.__srcDir,
                                          'build',
                                          archObj.sysDirName))
    
  
  @property
  def srcDir(self):
    return self.__srcDir
  
  @property
  def buildDir(self):
    return self.__buildDir
  
  @property
  def protocExePath(self):
    return self.__protocExePath
  
  @property
  def grpcIncludePaths(self):
    return self.__grpcIncludePaths
  
  @property
  def grpcLibPaths(self):
    return self.__grpcLibPaths
  
  def summary(self):
    lstr = '='*50 + '\n'
    lstr += 'Paths Summary\n'
    lstr += '='*50 + '\n'
    lstr += 'build:   ' + self.buildDir              + '\n'
    lstr += 'protoc:  ' + self.protocExePath         + '\n'
    lstr += 'include: ' + str(self.grpcIncludePaths) + '\n'
    lstr += 'lib:     ' + str(self.grpcLibPaths)     + '\n'
    lstr += '-'*50 + '\n'
    return lstr
  

archObj = Architecture()
pathObj = BuildPath(archObj)

print(archObj.summary())
print(pathObj.summary())

VariantDir(variant_dir=pathObj.buildDir,
           src_dir=pathObj.srcDir,
           duplicate=0)

env = Environment(
  tools=['default', 'protoc'],
  PROTOC=pathObj.protocExePath,
  PROTOC_DEBUG=True,
  CPPPATH=pathObj.grpcIncludePaths,
  LIBPATH=pathObj.grpcLibPaths
  )
env.pathObj = pathObj


def _getRootList():
  for root, _, files in os.walk(pathObj.srcDir):
    if 'SConscript' in files:
      yield root.replace(pathObj.srcDir, pathObj.buildDir)

for root in _getRootList():
  SConscript(os.path.join(root, 'SConscript'),
             exports={'env' : env})
