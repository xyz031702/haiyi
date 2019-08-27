import xml.etree.ElementTree as ET
import time
import logging
from haiyi.tools.es_handler import search
from haiyi.models import HaiyiUser
import datetime

logger = logging.getLogger(__name__)


def autoreply(data):
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
            reply = handle_msg(to_user, from_user, content)
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
        return e


class Msg(object):
    def __init__(self, **kwargs):
        self.ToUserName = kwargs.get('ToUserName')
        self.FromUserName = kwargs.get('FromUserName') # it is the openid of a user
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


def handle_msg(to_user, from_user, message):
    if message == 'dy0000':
        return echo_openid(to_user, from_user, message)
    else:
        return search_item(to_user, from_user, message)

#https://api.weixin.qq.com/cgi-bin/user/info?access_token=681f2b6630982621edc25b1674760a7d&openid=OPENID&lang=zh_CN

def search_item(to_user, from_user, message):
    members = HaiyiUser.objects.filter(open_id=from_user). \
        filter(active=True). \
        filter(end_date__gte=datetime.date.today())
    if not members:
        HaiyiUser.objects.filter(open_id=from_user). \
            filter(active=True). \
            filter(end_date__gte=datetime.date.today())
        return '不是激活用户, 请联系海蚁管理员。'
    products = search(message)
    content = ''
    i = 0
    for p in products:
        i += 1
        content = '%s\n\n%d. %s' % (content, i, p)
    content = content.strip()
    if content == '':
        content = '无结果'
    logger.info('content_len=%s', len(content))
    return content


def echo_openid(to_user, from_user, message):
    return from_user
