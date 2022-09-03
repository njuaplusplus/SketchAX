# coding=utf-8
import os
import glob
import shutil

def init():
    for f in glob.glob('*.sk'):
        if not has_holes_and_spec(f):
            print('Deleting unuseful sketch file:', f)
            os.remove(f)
        else:
            print('Creating directory for', f)
            dname = f[:f.index('.sk')]
            os.makedirs(dname)
            print('Moving directory for', f)
            shutil.move(f, os.path.join(dname,f))

def has_holes_and_spec(f):
    sk_file = ''
    with open(f) as in_file:
        sk_file = in_file.read()
    if ('??' in sk_file or '{*}' in sk_file or '{|}' in sk_file) and 'implements' in sk_file:
        return True
    return False

if __name__ == '__main__':
    init()
