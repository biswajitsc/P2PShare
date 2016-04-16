import threading
import thread
import main_test
import random
import time

cnt = 8040
while cnt <= 8066:
    thread.start_new_thread(main_test.main, (cnt,))
    time.sleep(10 + random.randint(-5, 5))

    s1 = open('./Share/localhost:{}/suresh.txt'.format(cnt), 'w')
    s1.write('This is suresh')
    s1.close()

    s1 = open('./Share/localhost:{}/mukesh.txt'.format(cnt), 'w')
    s1.write('This is mukesh')
    s1.close()

    cnt += 2

time.sleep(200)