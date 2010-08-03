#!/usr/bin/env python

import sys
import os
import fnmatch
import subprocess
import logging

js_path = "javascripts"
closure_path = os.path.join(js_path, 'closure-library','closure')
application_js_path = os.path.join(js_path, 'application.js')
js_dirs = ['box2d','eightball','helpers']

# deps
calcdeps_py_path = os.path.join(closure_path, "bin", "calcdeps.py")
deps_js_path = os.path.join(js_path, "deps.js")

# compile
compiled_js_path = os.path.join(js_path, "compiled.js")
jar_path = os.path.join('_tools', 'closure_compiler', 'compiler.jar')
extern_dir = os.path.join(js_path, 'externs')

def make_deps():
  
  command = ['python']
  command += [calcdeps_py_path]
  
  command += ["--output_file", deps_js_path]
  command += ["--d", closure_path]
  command += ["-o", "deps"]
  
  command += ["-i", application_js_path]
  
  for js_dir in js_dirs:
    command += ["-p", os.path.join(js_path, js_dir)]
  
  return command

def get_closure_base():
  return ["java", "-jar", jar_path]

def get_closure_inputs():
  command_inputs = []
  files = []
  # add js files in goog dir, without files in demos
  for file in find_files(closure_path, '*.js'):
    if(file.find('demos') == -1):
      files.append(file)
  
  # add all js files in each of js_dirs
  for js_dir in js_dirs:
    js_dir = os.path.join(js_path, js_dir)
    for file in find_files(js_dir, '*.js'):
      files.append(file)
  
  files.append(os.path.join(js_path, 'application.js'))
  
  for file in files:
    command_inputs += ["--js", file]
  
  externs = []
  for file in find_files(extern_dir, '*.js'):
    externs.append(file)
  
  for file in externs:
    command_inputs += ["--externs", file]
  
  command_inputs += ["--manage_closure_dependencies", "true"]
  return command_inputs

def get_command_with_inputs():
  return get_closure_base() + get_closure_inputs()

def compile():
  command = get_command_with_inputs()
  
  command += ["--compilation_level", "ADVANCED_OPTIMIZATIONS"] # SIMPLE_OPTIMIZATIONS
  command += ["--summary_detail_level", "3"]
  # debug makes var names readabel, but was causing weirdness..
  # command += " --debug true"
  command += ["--warning_level", "VERBOSE"]
  # make sure everything is in a good order
  command += ["--jscomp_dev_mode", "EVERY_PASS"]
  command += ["--js_output_file", compiled_js_path]
  
  # command += " --formatting PRETTY_PRINT"
  # command += " --formatting PRINT_INPUT_DELIMITER"
  
  return command

def find_files(directory, pattern):
    for root, dirs, files in os.walk(directory):
        for basename in files:
            if fnmatch.fnmatch(basename, pattern):
                filename = os.path.join(root, basename)
                yield filename

def print_help():
  command = get_closure_base()
  command.append("--help")
  return command

def main():
  logging.basicConfig(format='make_deps.py: %(message)s', level=logging.INFO)
  args = compile()
  logging.info('Running the following command: %s', ' '.join(args))
  proc = subprocess.Popen(args, stdout=subprocess.PIPE)
  (stdoutdata, stderrdata) = proc.communicate()
  if proc.returncode != 0:
    logging.error('JavaScript compilation failed.')
    sys.exit(1)
  else:
    sys.stdout.write(stdoutdata)

if __name__ == '__main__':
  main()