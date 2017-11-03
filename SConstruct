
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
    
    self.__grpcIncludePaths = [os.path.join(__grpcInstall, 'include')]
    self.__grpcLibPaths = [os.path.join(__grpcInstall, 'lib')]
    
    _pluginExt = '.exe' if archObj.isWindows else ''
    _grpcBinPath = os.path.join(__grpcInstall, 'bin')
    self.__protocExePath = os.path.join(_grpcBinPath,
                                        'protoc' + _pluginExt)
    self.__grpcCPPPlugin = os.path.join(_grpcBinPath,
                                        'grpc_cpp_plugin' + _pluginExt)
    self.__grpcPythonPlugin = os.path.join(_grpcBinPath,
                                           'grpc_python_plugin' + _pluginExt)
    self.__grpcJavaPlugin = os.path.join(_grpcBinPath,
                                        'grpc_java_plugin' + _pluginExt)
    
    def _exist(path):
      if not os.path.exists(path):
        os.makedirs(path)
      return path
    
    # build variables
    self.__buildDir = os.path.join(self.__srcDir,
                                   'build',
                                   archObj.sysDirName)
    self.__buildGenDir = os.path.join(self.__buildDir,
                                      'gen')
    self.__buildGenCCDir = _exist(os.path.join(self.__buildGenDir,
                                               'cc'))
    self.__buildGenPYDir = _exist(os.path.join(self.__buildGenDir,
                                               'py'))
    self.__buildGenJavaDir = _exist(os.path.join(self.__buildGenDir,
                                                 'java'))
    
  
  @property
  def srcDir(self):
    return self.__srcDir
  
  @property
  def buildDir(self):
    return self.__buildDir
  
  @property
  def buildGenDir(self):
    return self.__buildGenDir
  
  @property
  def buildGenCCDir(self):
    return self.__buildGenCCDir
  
  @property
  def buildGenPYDir(self):
    return self.__buildGenPYDir
  
  @property
  def buildGenJavaDir(self):
    return self.__buildGenJavaDir
  
  @property
  def protocExePath(self):
    return self.__protocExePath
  
  @property
  def grpcIncludePaths(self):
    return self.__grpcIncludePaths
  
  @property
  def grpcLibPaths(self):
    return self.__grpcLibPaths
  
  @property
  def grpcCPPPlugin(self):
    return self.__grpcCPPPlugin
  
  @property
  def grpcPythonPlugin(self):
    return self.__grpcPythonPlugin
  
  @property
  def grpcJavaPlugin(self):
    return self.__grpcJavaPlugin
  
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
  ENV=os.environ,
  tools=['default', 'protoc'],
  PROTOC=pathObj.protocExePath,
  PROTOC_GRPC_CC = pathObj.grpcCPPPlugin,
  PROTOC_GRPC_PY = pathObj.grpcPythonPlugin,
  PROTOC_GRPC_JAVA = pathObj.grpcJavaPlugin,
  PROTOC_DEBUG=True,
  CPPPATH=pathObj.grpcIncludePaths + [pathObj.buildGenCCDir],
  LIBPATH=pathObj.grpcLibPaths
  )
env.archObj = archObj
env.pathObj = pathObj

if archObj.isWindows:
  env.Replace(CPPFLAGS='/MD',
              CPPDEFINES={'_WIN32_WINNT' : '0x600'})

def _getRootList():
  for root, _, files in os.walk(pathObj.srcDir):
    if 'SConscript' in files:
      yield root.replace(pathObj.srcDir, pathObj.buildDir)

for root in _getRootList():
  SConscript(os.path.join(root, 'SConscript'),
             exports={'env' : env})
