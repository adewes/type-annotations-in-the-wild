import os
import re
import ast
import sys
import json
import shutil
import subprocess
from multiprocessing import Process, Pool

type_comment_re = re.compile(rb'#\s*type\s*:', re.I)
typing_re = re.compile(rb'(import\s+typing)|(from\s+typing\s+import)', re.I)

def check_ast_for_type_hints(tree):
    n_return_hints, n_annotation_hints = 0, 0
    for node in ast.walk(tree):
        if hasattr(node, 'annotation') and node.annotation is not None:
            n_annotation_hints += 1
        if hasattr(node, 'returns') and node.returns is not None:
            n_return_hints += 1
    return n_annotation_hints, n_return_hints

def check_code_for_type_hints(code):
    type_comments = re.findall(type_comment_re, code)
    typing_imports = re.findall(typing_re, code)
    return len(type_comments), len(typing_imports)

def check_repo(repo, base_path="/tmp/repos"):
    if not os.path.exists(base_path):
        os.makedirs(base_path)
    repo_dir = os.path.join(base_path,repo['full_name'].replace('/','_'))
    files_with_type_hints = []
    if not os.path.exists(repo_dir):
        try:
            subprocess.call(["git","clone",repo['git_url'], repo_dir],cwd=base_path)
        except:
            shutil.rmtree(repo_dir)
    for root, dir, files in os.walk(repo_dir):
        for filename in files:
            path = os.path.join(root, filename)
            relative_path = path[len(repo_dir):]
            if filename.endswith('.pyi'):
                files_with_type_hints.append({
                        'path' : path[len(repo_dir):],
                        'annotation_hints' : 0,
                        'return_hints' : 0,
                        'type_comments' : 0,
                        'typing_imports' : 0,
                        'pyi_file' : True
                    })
            elif filename.endswith('.py'):
                try:
                    with open(path,'rb') as input_file:
                        try:
                            code = input_file.read()
                            gv = {}
                            tree = ast.parse(code)
                            n_annotation_hints, n_return_hints = check_ast_for_type_hints(tree)
                            n_type_comments, n_typing_imports = check_code_for_type_hints(code)
                            if n_annotation_hints > 0\
                               or n_return_hints > 0\
                               or n_type_comments > 0\
                               or n_typing_imports > 0:
                                files_with_type_hints.append({
                                    'path' : relative_path,
                                    'annotation_hints' : n_annotation_hints,
                                    'return_hints' : n_return_hints,
                                    'type_comments' : n_type_comments,
                                    'typing_imports' : n_typing_imports,
                                    'pyi_file' : False,
                                    })
                        except SyntaxError:
                            #we ignore errors when parsing the module
                            pass
                except (IOError, ValueError):
                    #this might be a broken link...
                    pass
    return (repo, files_with_type_hints)

def load_repos(filename):
    repos = []
    i = 0
    with open(filename, 'rb') as input_file:
        for line in input_file:
            if line.strip():
                try:
                    data = json.loads(line.strip())

                    repos.append(data)
                except:
                    pass
    return repos

def main(args):
    filename = args[1]
    repos = load_repos(filename)
    print(len(repos))
    p = Pool(20)
    try:
        result = p.map(check_repo, repos)
    except KeyboardInterrupt:
        return
    for repo, files in result:
        print(json.dumps({
                'repo' : repo,
                'files' : files
            }))

if __name__ == '__main__':
    main(sys.argv)