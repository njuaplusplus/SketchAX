# coding=utf-8
import os
import glob
import shutil

def clean():
    for f in glob.glob('miniTest*'):
        sk_out_file = '%s/%s_output.sk' % (f,f)
        sk_pbe_file = '%s/%s_pbe.sk' % (f,f)
        test_config_file = '%s/test_config.py' % f
        python_test_dir = '%s/python_test' % f
        delete(sk_out_file)
        delete(sk_pbe_file)
        delete(test_config_file)
        delete(python_test_dir)

def delete(f):
    if os.path.isfile(f):
        print('Deleting file', f)
        os.remove(f)
    elif os.path.isdir(f):
        print('Deleting dir', f)
        shutil.rmtree(f)


if __name__ == '__main__':
    clean()
