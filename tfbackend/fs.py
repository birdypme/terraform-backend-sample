import json

class FilePermissionError(RuntimeError):
    """
    This error is raised by write() when the file is not locked or permission is required.
    """
    pass


class FileLockedError(RuntimeError):
    """
    This error is raised by lock() when the file is already locked by someone else.
    """
    def __init__(self, filename, lock_content, lock_id):
        super(RuntimeError, self).__init__("Failed to lock " + str(filename) + ": already locked by " + str(lock_id))
        self.filename = filename
        self.lock_id = lock_id
        self.lock_content = lock_content


class LockConflictError(RuntimeError):
    """
    This error is raised by unlock() when the file is not locked or locked by someone else
    """
    def __init__(self, filename, lock_id):
        super(RuntimeError, self).__init__("Failed to unlock " + str(filename) + ": not locked by " + str(lock_id))
        self.filename = filename
        self.lock_id = lock_id


class Fs(object):
    """
    Simple file system to store files in memory.
    """
    def __init__(self):
        self.files = {}
        self.locks = {}

    def read(self, filename):
        return self.files.get(filename)

    def write(self, filename, content, request_id):
        lock_content, lock_id = self.get_lock_content(filename)
        if not request_id:
            raise FilePermissionError('Lock is required to write any file.')
        if request_id!=lock_id:
            raise FilePermissionError('Failed to write file ' + str(filename) + ': not locked by ' + str(request_id))
        self.files[filename] = content

    def lock(self, filename, request_content):
        lock_content, lock_id = self.get_lock_content(filename)
        if lock_content:
            raise FileLockedError(filename, lock_content, lock_id)
        # TODO: validate request_content format
        self.locks[filename] = request_content

    def unlock(self, filename, lock_id):
        lock_content, current_lock_id = self.get_lock_content(filename)
        if not lock_content:
            raise LockConflictError(filename, lock_id)
        if current_lock_id!=lock_id:
            raise LockConflictError(filename, lock_id)
        self.locks.pop(filename)

    def get_lock_content(self, filename):
        lock_content = self.locks.get(filename, '')
        if not lock_content:
            return ('', '')
        lock_data = json.loads(lock_content)
        lock_id = lock_data.get('ID')
        print('found lock on ' + str(filename) + ' for ' + str(lock_id))
        return (lock_content, lock_id)
