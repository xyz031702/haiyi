import xml.etree.ElementTree as ET
import time
import logging
from haiyi.tools.es_handler import search
from haiyi.models import HaiyiUser
from haiyi.crm.cold_call.dialog import dialog_huashu
from haiyi.constants import CHANNELS
from django.utils import timezone
from datetime import timedelta
import traceback
import requests
from django.conf import settings

logger = logging.getLogger(__name__)


def autoreply(data, channel):
    try:
        logger.info('data from wechat=%s', data)
        #        webData = request.body
        xmlData = ET.fromstring(data)

        msg_type = xmlData.find('MsgType').text
        to_user = xmlData.find('ToUserName').text
        from_user = xmlData.find('FromUserName').text
        created_time = xmlData.find('CreateTime').text
        msg_id = xmlData.find('MsgId').text

        if msg_type == 'text':
            content = xmlData.find('Content').text
            reply = handle_msg(channel, to_user, from_user, content)
        elif msg_type == 'image':
            reply = "图片已收到,谢谢"
        elif msg_type == 'voice':
            reply = "语音已收到,谢谢"
        elif msg_type == 'video':
            reply = "视频已收到,谢谢"
        elif msg_type == 'shortvideo':
            reply = "小视频已收到,谢谢"
        elif msg_type == 'location':
            reply = "位置已收到,谢谢"
        elif msg_type == 'link':
            reply = "链接已收到,谢谢"
        else:
            reply = "谢谢发送的内容"
        replyMsg = TextMsg(toUserName=to_user, fromUserName=from_user, content=reply)
        return replyMsg.send()
    except Exception as e:
        logger.info(traceback.format_exc())
        return "error|内部错误"


class Msg(object):
    def __init__(self, **kwargs):
        self.ToUserName = kwargs.get('ToUserName')
        self.FromUserName = kwargs.get('FromUserName')  # it is the openid of a user
        self.CreateTime = kwargs.get('CreateTime')
        self.MsgType = kwargs.get('MsgType')
        self.MsgId = kwargs.get('MsgId')


class TextMsg(Msg):
    def __init__(self, toUserName, fromUserName, content):
        super(TextMsg, self).__init__(
            ToUserName=toUserName,
            FromUserName=fromUserName,
            CreateTime=int(time.time()),
        )
        self.Content = content

    def send(self):
        xmlForm = """
        <xml>
        <ToUserName><![CDATA[{FromUserName}]]></ToUserName>
        <FromUserName><![CDATA[{ToUserName}]]></FromUserName>
        <CreateTime>{CreateTime}</CreateTime>
        <MsgType><![CDATA[text]]></MsgType>
        <Content><![CDATA[{Content}]]></Content>
        </xml>
        """
        xml_reply = xmlForm.format(**self.__dict__)
        logger.info('msg=%s, reply=%s', self.__dict__, xml_reply)
        return xml_reply


def handle_msg(channel, to_user, from_user, message):
    if str.startswith(message.lower(), 'dy '):
        wechat_id = message.split(" ")[1]
        r = echo_openid(to_user, from_user, wechat_id)
        logger.info(r)
        if "error" in r:
            return r["error"]
        return r["result"]
    else:
        if channel == CHANNELS.JIAGE:
            return search_item(to_user, from_user, message)
        elif channel == CHANNELS.HUASHU:
            return dialog_huashu(message)
        else:
            return "错误频道"


def search_item(to_user, from_user, message):
    WECHAT_LIMIT = 2048
    members = HaiyiUser.objects.filter(open_id=from_user). \
        filter(active=True). \
        filter(end_date__gte=timezone.now())
    if not members:
        return '不是激活用户, 请联系海蚁管理员。'
    products = search(message)
    logger.info("search_item|products=%s", len(products))
    content = ""
    i = 0
    current_content = ""
    for p in products:
        i += 1
        content = '%s\n\n%d. %s' % (content, i, p)
        length = len(content.encode("utf-8"))
        if length >= WECHAT_LIMIT:
            logger.info("search_item|content_length=%s", length)
            break
        current_content = content.strip()
    if current_content == '':
        current_content = '无结果'
    return current_content


def echo_openid(to_user, from_user, wechat_id):
    members = HaiyiUser.objects.filter(open_id=from_user). \
        filter(end_date__gte=timezone.now())
    if members:
        return {"result": "用户已注册, 确认开通或退订请联系海蚁管理员。"}
    url = "https://api.weixin.qq.com/cgi-bin/token"
    params = {
        "grant_type": "client_credential",
        "appid": settings.WECHAT_APP_ID,
        "secret": settings.WECHAT_APP_SECRET,
    }
    r = requests.get(url=url, params=params)
    if r.status_code == 200 and "access_token" in r.json():
        access_token = r.json()["access_token"]
        params = {
            "access_token": access_token,
            "lang": "zh_C",
            "openid": from_user
        }
        url = "https://api.weixin.qq.com/cgi-bin/user/info"
        r = requests.get(url=url, params=params)
        if r.status_code == 200 and "nickname" in r.json():
            nickname = r.json()["nickname"]
            haiyi_user = HaiyiUser(
                end_date=timezone.now() + timedelta(days=365),
                active=False,
                open_id=from_user,
                name=nickname,
                account_id=wechat_id,
            )
            haiyi_user.save()
            logger.warning("echo_openid|save_user|user=%s, wechat_id=%s", haiyi_user.name, haiyi_user.account_id)
        else:
            logger.warning("echo_openid|fetch_user_info|error=%s", r.text)
            return {"error": "注册失败"}
    else:
        logger.warning("echo_openid|get_access_token_info|error=%s", r.text)
        return {"error": "注册失败"}
    return {"result": "注册成功，请通知管理员开通"}
