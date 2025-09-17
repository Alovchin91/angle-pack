#! /usr/bin/env python3

import common, os, pathlib, sys, zipfile

def parents(path):
  res = []
  parent = path.parent
  while '.' != str(parent):
    res.insert(0, parent)
    parent = parent.parent
  return res

def main():
  os.chdir(os.path.join(os.path.dirname(__file__), os.pardir, 'angle'))
  
  build_type = common.build_type()
  version = common.version()
  machine = common.machine()
  target = common.target()
  classifier = common.classifier()
  out_bin = 'out/' + build_type + '-' + target + '-' + machine

  globs = [
    out_bin + '/d3dcompiler_47.dll',
    out_bin + '/libEGL.*',
    out_bin + '/libGLESv2.*',
  ]

  dist = 'Angle-' + version + '-' + target + '-' + build_type + '-' + machine + classifier + '.zip'
  print('> Writing', dist)
  
  with zipfile.ZipFile(os.path.join(os.pardir, dist), 'w', compression=zipfile.ZIP_DEFLATED) as zip:
    dirs = set()
    for glob in globs:
      for path in pathlib.Path().glob(glob):
        if not path.is_dir():
          zip.write(str(path), path.name)

  return 0

if __name__ == '__main__':
  sys.exit(main())
