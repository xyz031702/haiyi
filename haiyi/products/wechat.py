import xml.etree.ElementTree as ET
import time
import logging
logger = logging.getLogger(__name__)


def autoreply(data):
    try:
        #        webData = request.body
        xmlData = ET.fromstring(data)

        msg_type = xmlData.find('MsgType').text
        toUser = xmlData.find('ToUserName').text
        fromUser = xmlData.find('FromUserName').text
        created_time = xmlData.find('CreateTime').text
        msg_id = xmlData.find('MsgId').text

        if msg_type == 'text':
            content = xmlData.find('Content').text
            logger.info('autoreply|content received=%s', content)
            reply = "机器人：我是个机器人，你好"
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
        replyMsg = TextMsg(toUser, fromUser, reply)
        return replyMsg.send()
    except Exception as e:
        return e


class Msg(object):
    def __init__(self, **kwargs):
        self.ToUserName = kwargs.get('ToUserName')
        self.FromUserName = kwargs.get('FromUserName')
        self.CreateTime = kwargs.get('CreateTime')
        self.MsgType = kwargs.get('MsgType')
        self.MsgId = kwargs.get('MsgId')


class TextMsg(Msg):
    def __init__(self, toUserName, fromUserName, content):
        super(TextMsg, self).__init__(
            ToUserName=toUserName,
            FromUserName=fromUserName,
            CreateTime=int(time.time()),
            Content=content
        )

    def send(self):
        XmlForm = """
        <xml>
        <ToUserName><![CDATA[{ToUserName}]]></ToUserName>
        <FromUserName><![CDATA[{FromUserName}]]></FromUserName>
        <CreateTime>{CreateTime}</CreateTime>
        <MsgType><![CDATA[text]]></MsgType>
        <Content><![CDATA[{Content}]]></Content>
        </xml>
        """
        return XmlForm.format(**self.__dict__)
