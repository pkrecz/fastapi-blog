import threading


class Singleton(type):

    instances = {}
    lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        if cls not in cls.instances:
            with cls.lock:
                if cls not in cls.instances:
                    cls.instances[cls] = super().__call__(*args, **kwargs)
        return cls.instances[cls]
