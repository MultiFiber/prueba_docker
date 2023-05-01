import os, redis
import time
import uuid
from django.utils.deprecation import MiddlewareMixin
from django.core.exceptions import MiddlewareNotUsed


class TraceRequest(MiddlewareMixin):
    uuid = None

    def __init__(self, get_response=None):
        self.uuid = str(uuid.uuid4())
        tr_host = os.environ['TR_HOST']
        tr_port = os.environ['TR_PORT']
        tr_db = os.environ['TR_DB']
        tr_password = os.environ['TR_PASSWORD']
        try:
            self.r = redis.Redis(host=tr_host, port=tr_port,db=int(tr_db), password=tr_password)  
        except Exception as e:
            pass
        
        super().__init__(get_response)
        #raise MiddlewareNotUsed

    #def process_request(self, request):
    #    request.prometheus_before_middleware_event = time.time()

    def process_response(self, request, response):
        if hasattr(self, 'r'):
            self.r.set(self.uuid, response.content) 
        return response
