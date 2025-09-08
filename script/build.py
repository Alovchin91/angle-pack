#! /usr/bin/env python3

import common, os, subprocess, sys

def build_angle_lib(lib_name, is_winappsdk):
  build_type = common.build_type()
  machine = common.machine()
  host = common.host()
  target = common.target()

  if build_type == 'Debug':
    args = ['is_debug=true']
  else:
    args = [
      'is_official_build=true',
      # the official build enable Chrome PGO, which requires a full Chrome checkout
      'chrome_pgo_phase=0',
    ]

  args += [
    'target_cpu="' + machine + '"',
    'angle_enable_d3d9=false',
    'angle_enable_gl=false',
    'angle_enable_gl_desktop_backend=false',
    'angle_enable_null=false',
    'angle_enable_vulkan=false',
    'angle_enable_wgpu=false',
    # rapidJSON is used for ANGLE's frame capture (among other things), which is unnecessary for our build.
    'angle_has_rapidjson=false',
    'angle_build_all=false',
    'is_clang=false',
    'is_component_build=false',
    'use_custom_libcxx=false',
    'use_siso=false',
  ]

  if is_winappsdk:
    winappsdk_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'winappsdk')
    args += [
      'angle_is_winappsdk=true',
      'winappsdk_dir="' + winappsdk_path + '"',
    ]

  tools_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'depot_tools')

  suffix = '-wasdk' if is_winappsdk else ''
  out = os.path.join('out', build_type + '-' + target + '-' + machine + suffix)
  gn = 'gn.bat' if 'windows' == host else 'gn'

  env = os.environ.copy()
  env['DEPOT_TOOLS_UPDATE']='0'
  env['DEPOT_TOOLS_WIN_TOOLCHAIN']='0'

  subprocess.check_call([os.path.join(tools_dir, gn), 'gen', out, '--args=' + ' '.join(args)], env=env)
  subprocess.check_call(['python3', os.path.join(tools_dir, 'autoninja.py'), '--offline', '-C', out, lib_name], env=env)

def main():
  os.chdir(os.path.join(os.path.dirname(__file__), os.pardir, 'angle'))

  build_angle_lib('libEGL', False)
  build_angle_lib('libGLESv2', True)

  return 0

if __name__ == '__main__':
  sys.exit(main())
