from userapp.models import UserApp
from utils.models import BaseModel
from django.db.models.fields import CharField,  DateTimeField
from django.db import models



class HistorySession(BaseModel):
    user = models.ForeignKey(UserApp, on_delete=models.CASCADE) 
    date = DateTimeField(auto_now_add=True)
    ip = CharField(max_length=50)

    def __str__(self):
        return self.user.name
    class Meta:
        pass


