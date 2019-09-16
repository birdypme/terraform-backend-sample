"""
Copyright © 2019 by Julien Champseix.
All rights reserved.
This file is part of the terraform-backend-sample tool,
and is released under the "MIT License Agreement". Please see the LICENSE
file that should have been included as part of this package.
"""

import json
import unittest

from tfbackend import fs

TEST_FILE = 'x/y/z.tf'
FILE_CONTENT = json.dumps({
    'test': 'true',
})
LOCK_ID = '225affe6-18e3-f6b1-b4d2-e23b04f12604'
LOCK_CONTENT = '''{"ID":"225affe6-18e3-f6b1-b4d2-e23b04f12604","Operation":"OperationTypeApply","Info":"","Who":"admin","Version":"0.11.13","Created":"2019-09-16T14:32:16.7858102Z","Path":""}'''
LOCK_ID2 = '335affe6-18e3-f6b1-b4d2-e23b04f12655'
LOCK_CONTENT2 = '''{"ID":"335affe6-18e3-f6b1-b4d2-e23b04f12655","Operation":"OperationTypeApply","Info":"","Who":"anonymous","Version":"0.11.13","Created":"2019-09-16T14:33:16.7858102Z","Path":""}'''

class TestFs(unittest.TestCase):
    def test_base(self):
        files = fs.Fs()

        # by default, file content is empty
        self.assertEqual(files.read(TEST_FILE), '')
        # can't write without a lock
        with self.assertRaises(fs.FilePermissionError):
            files.write(TEST_FILE, FILE_CONTENT, LOCK_ID)
        # file content hasn't changed
        self.assertEqual(files.read(TEST_FILE), '')
        # locking works
        files.lock(TEST_FILE, LOCK_CONTENT)

        # can write with the correct lock, and content can be read
        files.write(TEST_FILE, FILE_CONTENT, LOCK_ID)
        self.assertEqual(files.read(TEST_FILE), FILE_CONTENT)

        files.unlock(TEST_FILE, LOCK_ID)

        # content is still correct
        self.assertEqual(files.read(TEST_FILE), FILE_CONTENT)

    def test_multilocks(self):
        files = fs.Fs()

        files.lock(TEST_FILE, LOCK_CONTENT)

        # can't lock twice, can't lock with another use
        with self.assertRaises(fs.FileLockedError):
            files.lock(TEST_FILE, LOCK_CONTENT)
        with self.assertRaises(fs.FileLockedError):
            files.lock(TEST_FILE, LOCK_CONTENT2)

        # can't write with another user
        with self.assertRaises(fs.FilePermissionError):
            files.write(TEST_FILE, FILE_CONTENT, LOCK_ID2)
        
        # can write with the correct lock, and content can be read
        files.write(TEST_FILE, FILE_CONTENT, LOCK_ID)

        # can only unlock with the same id
        with self.assertRaises(fs.LockConflictError):
            files.unlock(TEST_FILE, LOCK_ID2)
        files.unlock(TEST_FILE, LOCK_ID)

        # content is still correct
        self.assertEqual(files.read(TEST_FILE), FILE_CONTENT)
