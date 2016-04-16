import threading
import thread
import main_test
import random
import time
import getip

cnt = 8040
while cnt <= 8066:
    thread.start_new_thread(main_test.main, (cnt,))
    time.sleep(10 + random.randint(-5, 5))

    s1 = open('./Share/{}:{}/suresh.txt'.format(getip.get_lan_ip(), cnt), 'w')
    s1.write('This is suresh')
    s1.close()

    s1 = open('./Share/{}:{}/mukesh.txt'.format(getip.get_lan_ip(), cnt), 'w')
    s1.write('This is mukesh')
    s1.close()

    cnt += 2

time.sleep(200)
