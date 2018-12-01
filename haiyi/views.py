from django.http import HttpResponse
import datetime
from django.views.decorators.csrf import csrf_exempt
import json
import logging

logger = logging.getLogger(__name__)

@csrf_exempt
def current_datetime(request):
    now = datetime.datetime.now()
    html = "<html><body>It is now %s.</body></html>" % now
    return HttpResponse(html)

@csrf_exempt
def chat_receiver(request):
    logger.info('from wechat:', request.POST)
    html = "<html><body>chat: %s.</body></html>" % request.POST
    return HttpResponse(html)