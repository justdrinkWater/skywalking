from time import sleep

from sender import send_message

a = 3000
while a > 0:
    send_message()
    a = a - 1
    sleep(1)
