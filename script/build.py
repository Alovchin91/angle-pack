#! /usr/bin/env python3

import common, os, subprocess, sys

def main():
  os.chdir(os.path.join(os.path.dirname(__file__), os.pardir, 'angle'))

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
    'angle_enable_gl=false',
    'angle_enable_null=false',
    'angle_enable_vulkan=false',
    # rapidJSON is used for ANGLE's frame capture (among other things), which is unnecessary for our build.
    'angle_has_rapidjson=false',
    'angle_build_all=false',
    'is_component_build=false',
    'use_siso=false',
  ]

  tools_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'depot_tools')

  out = os.path.join('out', build_type + '-' + target + '-' + machine)
  gn = 'gn.bat' if 'windows' == host else 'gn'
  
  env = os.environ.copy()
  env['DEPOT_TOOLS_UPDATE']='0'
  env['DEPOT_TOOLS_WIN_TOOLCHAIN']='0'

  print([os.path.join(tools_dir, gn), 'gen', out, '--args=' + ' '.join(args)])
  subprocess.check_call([os.path.join(tools_dir, gn), 'gen', out, '--args=' + ' '.join(args)], env=env)
  subprocess.check_call(['python3', os.path.join(tools_dir, 'autoninja.py'), '--offline', '-C', out, 'libEGL', 'libGLESv2'], env=env)

  return 0

if __name__ == '__main__':
  sys.exit(main())
