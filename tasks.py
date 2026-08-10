from celery_app import celery_app
import time

@celery_app.task(name="tasks.sum", bind=True)
def sum_task(self, num1, num2):
    time.sleep(5)
    return num1 + num2


@celery_app.task(name="tasks.factorial", bind=True)
def factorial_task(self, n):
    time.sleep(3)
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers.")
    
    result = 1

    for i in range(2, n + 1):
        result *= i

    return result