
# Merge multiple repositories into a single repository.
# This is an experiment to evaluate what a LVGL mono-repository would
# look like as discussed in https://github.com/lvgl/lvgl/issues/2456.
#
# The experimental merged mono-repo will be placed beside this script.
# This script will not push changes to any repos.
# 
# This implements the approach described in:
# https://medium.com/@checko/merging-two-git-repositories-into-one-preserving-the-git-history-4e20d3fafa4e

import glob
import os
import shutil
import subprocess
import sys


def onError(func, path, exc_info):
    import stat
    if not os.access(path, os.W_OK):
        os.chmod(path, stat.S_IWUSR)
        func(path)
    else:
        raise


def repoBaseDir(url):
    b = os.path.splitext(url)[0]
    items = b.split('/')
    return items[len(items)-1]


script_dir = os.path.dirname(os.path.realpath(__file__))
# Where the combined mono-repo will be created.
mono_repo_root = os.path.join(script_dir, 'mono-repo')
# Must not conflict with a top-level file or directory of any
# of the merged repos (i.e. `to_merge`).
repos_root_dir = 'libs'
lvgl_repo = 'https://github.com/lvgl/lvgl.git'

to_merge = [
    'https://github.com/lvgl/lv_binding_micropython.git',
    'https://github.com/lvgl/lv_demos.git',
    'https://github.com/lvgl/lv_fs_if',
    'https://github.com/lvgl/lv_i18n.git',
    'https://github.com/lvgl/lv_lib_bmp.git',
    'https://github.com/lvgl/lv_lib_freetype.git',
    'https://github.com/lvgl/lv_lib_gif.git',
    'https://github.com/lvgl/lv_lib_png.git',
    'https://github.com/lvgl/lv_lib_qrcode.git',
    'https://github.com/lvgl/lv_lib_rlottie.git',
    'https://github.com/lvgl/lv_lib_split_jpg.git',
    'https://github.com/lvgl/lv_sim_emscripten.git',
    'https://github.com/lvgl/lv_utils.git',
]

try:
    shutil.rmtree(mono_repo_root, ignore_errors=False, onerror=onError)
except FileNotFoundError:
    pass
os.mkdir(mono_repo_root)
os.mkdir(os.path.join(mono_repo_root, repos_root_dir))

os.chdir(mono_repo_root)
subprocess.check_call(['git', 'init'])

for repo_url in to_merge:
    subdir = repoBaseDir(repo_url)
    cmd = ['git', 'remote', 'add', '-f', subdir, repo_url]
    subprocess.check_call(cmd)

    cmd = ['git', 'merge', '--allow-unrelated-histories', '%s/master' % subdir]
    subprocess.check_call(cmd)

    dest_dir = os.path.join(mono_repo_root, repos_root_dir, subdir)
    os.mkdir(dest_dir)
    to_move = []
    skip_move = [repos_root_dir, '.git']
    for fname in os.listdir(mono_repo_root):
        if fname not in skip_move:
            to_move.append(fname)

    for fname in to_move:
        shutil.move(os.path.join(mono_repo_root, fname), dest_dir)

    subprocess.check_call(['git', 'add', '.'])
    cmd = ['git', 'commit', '-m', 'Move %s files to %s/%s directory.' %
           (subdir, repos_root_dir, subdir)]
    subprocess.check_call(cmd)

cmd = ['git', 'remote', 'add', '-f', 'origin', lvgl_repo]
subprocess.check_call(cmd)

cmd = ['git', 'merge', '--allow-unrelated-histories', 'origin/master']
subprocess.check_call(cmd)
