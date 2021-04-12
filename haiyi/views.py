from django.http import HttpResponse
import datetime
from django.views.decorators.csrf import csrf_exempt
import json
import logging
import hashlib
from haiyi.products.wechat import autoreply
from haiyi.constants import CHANNELS
from django.conf import settings

logger = logging.getLogger(__name__)


@csrf_exempt
def current_datetime(request):
    now = datetime.datetime.now()
    html = "<html><body>It is now %s.</body></html>" % now
    return HttpResponse(html)


@csrf_exempt
def chat_huashu(request):
    logger.info('received request from wechat')
    if request.method == 'GET':
        logger.info('from wechat=%s', request.GET)
        signature = request.GET.get('signature')
        timestamp = request.GET.get('timestamp')
        nonce = request.GET.get('nonce')
        echostr = request.GET.get('echostr')
        token=settings.WECHAT_TOKEN
        my_list = [token, timestamp, nonce]
        my_list.sort()
        hashcode = ''.join(my_list)
        hashcode = hashlib.sha1(hashcode.encode('utf-8')).hexdigest()
        if hashcode == signature:
            logger.info("hashcode matched=%s", hashcode)
            return HttpResponse(echostr)
        else:
            logger.info("hashcode not matched, hash=%s, signature=%s", hashcode, signature)
            return HttpResponse("no match")
    else:
        othercontent = autoreply(request.body, CHANNELS.HUASHU)
        logger.info('reply=%s, length=%s', othercontent, len(othercontent.encode("utf-8")))
        return HttpResponse(othercontent)


@csrf_exempt
def chat_receiver(request):
    logger.info('received request from wechat')
    if request.method == 'GET':
        logger.info('from wechat=%s', request.GET)
        signature = request.GET.get('signature')
        timestamp = request.GET.get('timestamp')
        nonce = request.GET.get('nonce')
        echostr = request.GET.get('echostr')
        token=settings.WECHAT_TOKEN
        my_list = [token, timestamp, nonce]
        my_list.sort()
        hashcode = ''.join(my_list)
        hashcode = hashlib.sha1(hashcode.encode('utf-8')).hexdigest()
        if hashcode == signature:
            logger.info("hashcode matched=%s", hashcode)
            return HttpResponse(echostr)
        else:
            logger.info("hashcode not matched, hash=%s, signature=%s", hashcode, signature)
            return HttpResponse("no match")
    else:
        othercontent = autoreply(request.body, CHANNELS.JIAGE)
        logger.info('reply=%s, length=%s', othercontent, len(othercontent.encode("utf-8")))
        return HttpResponse(othercontent)

    # html = "<html><body>chat: %s.</body></html>" % request.POST
    # return HttpResponse(html)
