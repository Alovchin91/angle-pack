#! /usr/bin/env python3

import common, os, re, subprocess, sys

def main():
  os.chdir(os.path.join(os.path.dirname(__file__), os.pardir))

  parser = common.create_parser(True)
  args = parser.parse_args()

  # Clone depot_tools
  if not os.path.exists('depot_tools'):
    subprocess.check_call(['git', 'clone', '--config', 'core.autocrlf=input', 'https://chromium.googlesource.com/chromium/tools/depot_tools.git', 'depot_tools'])

  # Clone ANGLE
  match = re.match('[0-9a-f]+', args.version)
  if not match:
    raise Exception('Expected --version "<sha>", got "' + args.version + '"')

  commit = match.group(0)

  if os.path.exists('angle'):
    print('> Fetching')
    os.chdir('angle')
    subprocess.check_call(['git', 'reset', '--hard'])
    subprocess.check_call(['git', 'clean', '-d', '-f'])
    subprocess.check_call(['git', 'fetch', 'origin'])
  else:
    print('> Cloning')
    subprocess.check_call(['git', 'clone', '--config', 'core.autocrlf=input', 'https://chromium.googlesource.com/angle/angle.git', 'angle'])
    os.chdir('angle')
    subprocess.check_call(['git', 'fetch', 'origin'])

  # Checkout commit
  print('> Checking out', commit)
  subprocess.check_call(['git', '-c', 'advice.detachedHead=false', 'checkout', commit])

  # git deps
  print('> Running gclient sync')

  gclient_config = '''solutions = [
  {{
    "name": ".",
    "url": "https://chromium.googlesource.com/angle/angle.git@{}",
    "deps_file": "DEPS",
    "managed": False,
    "custom_vars": {{}},
  }},
]'''

  with open('.gclient', 'w') as gclient_file:
    print(gclient_config.format(commit), file=gclient_file)

  tools_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'depot_tools')
  gclient = 'gclient.bat' if 'windows' == common.host() else 'gclient'
  env = os.environ.copy()
  env['DEPOT_TOOLS_UPDATE']='0'
  env['DEPOT_TOOLS_WIN_TOOLCHAIN']='0'
  subprocess.check_call([os.path.join(tools_dir, gclient), 'sync'], env=env)

  return 0

if __name__ == '__main__':
  sys.exit(main())
