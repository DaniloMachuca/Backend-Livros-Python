from celery_app import celery_app
import time

@celery_app.task(name="tasks.somar", bind=True)
def somar(self, num1, num2):
    time.sleep(5)
    return num1 + num2

@celery_app.task(name="tasks.fatorial", bind=True)
def fatorial(self, n):
    time.sleep(3)
    if n < 0:
        raise ValueError("O fatorial não está definido para números negativos.")
    
    resultado = 1

    for i in range(2, n + 1):
        resultado *= i

    return resultado