import threading

kv_lock = threading.Lock()


# import threading
# import time

# # Custom lock w/ 2 second timeout
# class TimedLock:
#     def __init__(self, timeout=2):
#         self.lock = threading.Lock()
#         self.timeout = timeout
#         self.lock_acquired_time = None

#     def acquire(self):
#         acquired = self.lock.acquire(timeout=self.timeout)
#         if acquired:
#             self.lock_acquired_time = time.time()
#         return acquired

#     def release(self):
#         current_time = time.time()
#         if current_time - self.lock_acquired_time > self.timeout:
#             print("Lock auto-released after timeout")
#         self.lock.release()

# kv_lock = TimedLock(timeout=2)
