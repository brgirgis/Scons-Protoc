"""
Google's Protoc builder

Example, will produce c++ output files in the src directory.

protoc_cc = env.Protoc(["src/Example.proto"],
    PROTOC_PATH='#src',
    PROTOC_CCOUT='#src',
    )

"""

from __future__ import print_function

import os
import SCons.Util
from SCons.Script import Builder, Action

def _protoc_emitter(target, source, env):
    """Process target, sources, and flags"""
    from SCons.Script import File, Dir
    
    isDebug = env.get('PROTOC_DEBUG', False)
    def _print(*prtList):
        if not isDebug:
            return
        print(*prtList)
    
    # always ignore target
    target = []
    
    # suffix
    protoc_suffix = env.subst('$PROTOC_SUFFIX')
    
    protoc_h_suffix = env.subst('$PROTOC_HSUFFIX')
    protoc_cc_suffix = env.subst('$PROTOC_CCSUFFIX')
    protoc_grpc_h_suffix = env.subst('$PROTOC_GRPC_HSUFFIX')
    protoc_grpc_cc_suffix = env.subst('$PROTOC_GRPC_CCSUFFIX')
    
    protoc_py_suffix = env.subst('$PROTOC_PYSUFFIX')
    protoc_grpc_py_suffix = env.subst('$PROTOC_GRPC_PYSUFFIX')
    
    # fetch all protoc flags
    if env['PROTOC_FLAGS']:
        protocflags = env.subst("$PROTOC_FLAGS",
                                target=target,
                                source=source)
        flags = SCons.Util.CLVar(protocflags)
    else:
        flags = SCons.Util.CLVar('')
    
    # flag --plugin=protoc-gen-grpc-cpp
    if env['PROTOC_GRPC_CC']:
        env['PROTOC_GRPC_CC'] = File(env['PROTOC_GRPC_CC'])
        flags.append('--plugin=protoc-gen-grpc-cpp=${PROTOC_GRPC_CC.abspath}')
    
    # flag --cpp_out
    if env['PROTOC_CCOUT']:
        env['PROTOC_CCOUT'] = Dir(env['PROTOC_CCOUT'])
        flags.append('--cpp_out=${PROTOC_CCOUT.abspath}')
    
    # flag --grpc-cpp_out
    if env['PROTOC_GRPC_CCOUT']:
        env['PROTOC_GRPC_CCOUT'] = Dir(env['PROTOC_GRPC_CCOUT'])
        flags.append('--grpc-cpp_out=${PROTOC_GRPC_CCOUT.abspath}')
    
    # flag --plugin=protoc-gen-grpc-python
    if env['PROTOC_GRPC_PY']:
        env['PROTOC_GRPC_PY'] = File(env['PROTOC_GRPC_PY'])
        flags.append('--plugin=protoc-gen-grpc-python=${PROTOC_GRPC_PY.abspath}')
    
    # flag --python_out
    if env['PROTOC_PYOUT']:
        env['PROTOC_PYOUT'] = Dir(env['PROTOC_PYOUT'])
        flags.append('--python_out=${PROTOC_PYOUT.abspath}')
    
    # flag --grpc-python_out
    if env['PROTOC_GRPC_PYOUT']:
        env['PROTOC_GRPC_PYOUT'] = Dir(env['PROTOC_GRPC_PYOUT'])
        flags.append('--grpc-python_out=${PROTOC_GRPC_PYOUT.abspath}')
    
    # flag --proto_path, -I
    proto_path = []
    if env['PROTOC_PATH']:
        inc = env['PROTOC_PATH']
        if SCons.Util.is_List(inc):
            for path in inc:
                path = Dir(path)
                _print("path:", path)
                proto_path.append(path)
        elif SCons.Util.is_Scalar(inc):
            path = Dir(inc)
            _print("path:", path)
            proto_path.append(path)
    
    # produce proper targets
    for src in source:
        srcPath = os.path.abspath(str(src))
        srcDir = os.path.dirname(srcPath)
        srcName = os.path.basename(srcPath)
        
        if srcDir not in proto_path:
            proto_path.append(srcDir)
        
        # create stem by remove the $PROTOC_SUFFIX or take a guess
        if srcName.endswith(protoc_suffix):
            stem = srcName[:-len(protoc_suffix)]
        else:
            stem = srcName
        _print("stem:", stem)
        
        # C++ output, append
        if env['PROTOC_CCOUT']:
            out = Dir(env['PROTOC_CCOUT'])
            base = os.path.join(out.abspath, stem)
            target.append(File(base + protoc_h_suffix))
            target.append(File(base + protoc_cc_suffix))
        
        if env['PROTOC_GRPC_CCOUT']:
            out = Dir(env['PROTOC_GRPC_CCOUT'])
            base = os.path.join(out.abspath, stem)
            target.append(File(base + protoc_grpc_h_suffix))
            target.append(File(base + protoc_grpc_cc_suffix))
        
        # python output, append
        if env['PROTOC_PYOUT']:
            out = Dir(env['PROTOC_PYOUT'])
            base = os.path.join(out.abspath, stem)
            target.append(File(base + protoc_py_suffix))
        
        if env['PROTOC_GRPC_PYOUT']:
            out = Dir(env['PROTOC_GRPC_PYOUT'])
            base = os.path.join(out.abspath, stem)
            target.append(File(base + protoc_grpc_py_suffix))
        
    
    for path in proto_path:
        flags.append('--proto_path=' + \
                     path if isinstance(path, str) else \
                    str(path.abspath))
    
    # updated flags
    env['PROTOC_FLAGS'] = str(flags)
    
    _print("flags:", flags)
    _print("targets:",
           env.subst("${TARGETS}",
                     target=target,
                     source=source))
    _print("sources:",
           env.subst("${SOURCES}",
                     target=target,
                     source=source))
    
    return target, source

_protoc_builder = Builder(
    action = Action('$PROTOC_COM', '$PROTOC_COMSTR'),
    suffix = '$PROTOC_CCSUFFIX',
    src_suffix = '$PROTOC_SUFFIX',
    emitter = _protoc_emitter,
)

def _multiGet(kwd,
              defaultVal,
              kwargs,
              env):
  return kwargs.get(kwd) or \
         env.get(kwd) or \
         defaultVal

def _detect(env,
            kwargs):
    """Try to find the Protoc compiler"""
    protoc = _multiGet('PROTOC',
                       '',
                       env,
                       kwargs) or \
             env.Detect('protoc')
    if protoc:
        return protoc
    raise SCons.Errors.StopError(
        "Could not detect protoc Compiler")
    

def generate(env,
             **kwargs):
    """Add Builders and construction variables."""
    env['PROTOC'] = _detect(env, kwargs)
    
    env.SetDefault(
        # Additional command-line flags
        PROTOC_FLAGS = _multiGet('PROTOC_FLAGS',
                                 SCons.Util.CLVar(''),
                                 env,
                                 kwargs),
        
        # Source path(s)
        PROTOC_PATH = _multiGet('PROTOC_PATH',
                                SCons.Util.CLVar(''),
                                env,
                                kwargs),
        
        # Plugins path
        PROTOC_GRPC_CC = _multiGet('PROTOC_GRPC_CC',
                                   '',
                                   env,
                                   kwargs),
        PROTOC_GRPC_PY = _multiGet('PROTOC_GRPC_PY',
                                   '',
                                   env,
                                   kwargs),
        
        # Output path
        PROTOC_CCOUT      = _multiGet('PROTOC_CCOUT',
                                      '',
                                      env,
                                      kwargs),
        PROTOC_GRPC_CCOUT = _multiGet('PROTOC_GRPC_CCOUT',
                                      '',
                                      env,
                                      kwargs),
        
        PROTOC_PYOUT      = _multiGet('PROTOC_PYOUT',
                                      '',
                                      env,
                                      kwargs),
        PROTOC_GRPC_PYOUT = _multiGet('PROTOC_GRPC_PYOUT',
                                      '',
                                      env,
                                      kwargs),
        
        # Suffixies / prefixes
        PROTOC_SUFFIX = _multiGet('PROTOC_SUFFIX',
                                  '.proto',
                                  env,
                                  kwargs),
        
        # C++
        PROTOC_HSUFFIX  = _multiGet('PROTOC_HSUFFIX',
                                    '.pb.h',
                                    env,
                                    kwargs),
        PROTOC_CCSUFFIX = _multiGet('PROTOC_CCSUFFIX',
                                    '.pb.cc',
                                    env,
                                    kwargs),
        
        PROTOC_GRPC_HSUFFIX  = _multiGet('PROTOC_GRPC_HSUFFIX',
                                         '.grpc.pb.h',
                                         env,
                                         kwargs),
        PROTOC_GRPC_CCSUFFIX = _multiGet('PROTOC_GRPC_CCSUFFIX',
                                         '.grpc.pb.cc',
                                         env,
                                         kwargs),
        
        # Python
        PROTOC_PYSUFFIX      = _multiGet('PROTOC_PYSUFFIX',
                                         '_pb2.py',
                                         env,
                                         kwargs),
        PROTOC_GRPC_PYSUFFIX = _multiGet('PROTOC_GRPC_PYSUFFIX',
                                         '_pb2_grpc.py',
                                         env,
                                         kwargs),
        
        # Protoc command
        PROTOC_COM = "$PROTOC $PROTOC_FLAGS $SOURCES.abspath",
        PROTOC_COMSTR = '',
        
    )
    
    env['BUILDERS']['Protoc'] = _protoc_builder
    

def exists(env):
    return _detect(env, {})
