#! /usr/bin/env python3

import argparse, glob, os, platform, shutil, subprocess, sys, urllib.request, zipfile
sys.path.append(os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..', '..')))
import script.common as common 
import native.script.build as native_build

def main(args):
  parser = argparse.ArgumentParser()
  parser.add_argument('--skija-version')
  (args, _) = parser.parse_known_args()

  # Javac
  swt_artifact = {'macos': 'org.eclipse.swt.cocoa.macosx.x86_64',
                  'windows': 'org.eclipse.swt.win32.win32.x86_64',
                  'linux': 'org.eclipse.swt.gtk.linux.x86_64'}[common.system]
  classpath = [
    # common.fetch_maven('org.projectlombok', 'lombok', '1.18.16'),
    common.fetch_maven('org.eclipse.platform', swt_artifact, '3.115.100')
  ]

  if args.skija_version:
    classpath += [
      common.fetch_maven('org.jetbrains.skija', 'skija-shared', args.skija_version, repo='https://packages.jetbrains.team/maven/p/skija/maven'),
      common.fetch_maven('org.jetbrains.skija', common.skija_native_artifact_id, args.skija_version, repo='https://packages.jetbrains.team/maven/p/skija/maven'),
    ]
  else:
    native_build.main()
    classpath += [
      os.path.join('..', '..', 'native', 'build'),
      os.path.join('..', '..', 'shared', 'target', 'classes')
    ]

  os.chdir(os.path.join(os.path.dirname(__file__), os.pardir))

  sources = common.glob('src', '*.java')
  common.javac(classpath, sources, 'target/classes')

  # Java
  subprocess.run([
    'java',
    '--class-path', common.classpath_separator.join(['target/classes'] + classpath)]
    + (['-XstartOnFirstThread'] if 'macos' == common.system else [])
    + ['-Djava.awt.headless=true',
    '-ea',
    '-esa',
    '-Dskija.logLevel=DEBUG',
    'org.jetbrains.skija.examples.swt.Main'],
    check=True)

  return 0

if __name__ == '__main__':
  sys.exit(main())