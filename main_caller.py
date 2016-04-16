import threading
import thread
import main_test
import random
import time

cnt = 8008
while cnt <= 8020:
    time.sleep(10 + random.randint(-5, 5))
    thread.start_new_thread(main_test.main, (cnt,))
    cnt += 2
