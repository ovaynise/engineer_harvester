from celery import shared_task
import time





@shared_task
def hello():
    for x in range(5):
        print(f'hello{x}')
        time.sleep(2)
    return 'hello world'

