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
    subprocess.check_call(['git', 'reset', '--hard'], cwd='build')
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
  env['DEPOT_TOOLS_WIN_TOOLCHAIN']='0'

  # TODO: to be removed when depot_tools are fixed
  depot_tools_git_workaround = '''@echo off
setlocal
if not defined EDITOR set EDITOR=notepad
:: Exclude the current directory when searching for executables.
:: This is required for the SSO helper to run, which is written in Go.
:: Without this set, the SSO helper may throw an error when resolving
:: the `git` command (see https://pkg.go.dev/os/exec for more details).
set "NoDefaultCurrentDirectoryInExePath=1"
git.exe %*'''

  with open(os.path.join(tools_dir, 'git.bat'), 'w') as git_bat_file:
    print(depot_tools_git_workaround, file=git_bat_file)

  subprocess.check_call([os.path.join(tools_dir, gclient), 'sync'], env=env)

  # Calculating an official build's timestamp requires the chrome/VERSION file
  with open("build/compute_build_timestamp.py", "r") as timestamp_file:
    timestamp_file_contents = timestamp_file.read()

  timestamp_file_contents = timestamp_file_contents.replace(
    "if args.build_type == 'official':",
    "if args.build_type == 'please_no':",
  )

  with open("build/compute_build_timestamp.py", "w") as timestamp_file:
    timestamp_file.write(timestamp_file_contents)

  return 0

if __name__ == '__main__':
  sys.exit(main())
