from config.celery import app
from rest_framework.authtoken.models import Token

@app.task(shared=True)
def empty_tokens_table():
    
    tokens = Token.objects.all()
    for token in tokens:
        token.delete()