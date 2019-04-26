# from selenium import webdriver
# from urllib import parse
import re
from lxml import etree, html
import requests
import time
import json


class LETIAN:
    def __init__(self):
        DEFAULT_HEADERS = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.15 Safari/537.36',
            'Upgrade-Insecure-Requests': '1',
            'Accept-Encoding': 'gzip, deflate',
            'Host': 'chn.lottedfs.com',
        }
        # 设置白名单
        benji_ip = requests.get('http://httpbin.org/ip').json()
        print(benji_ip)
        benji_ip = benji_ip["origin"]
        baimingdan = 'http://web.http.cnapi.cc/index/index/save_white?neek=60945&appkey=fbf571c3235726b707f88aac332f210d&white={}'.format(
            benji_ip)
        back = requests.get(baimingdan).text
        # 设置白名单结束
        print(back)
        self.session = requests.session()
        self.session.verify = False
        self.ip = self.get_ip()
        time.sleep(1)
        self.ip1 = self.get_ip()
        self.session.headers = DEFAULT_HEADERS

    def get_ip(self):
        # admin
        ip_prot = requests.get(
            'http://webapi.http.zhimacangku.com/getip?num=1&type=1&pro=&city=0&yys=0&port=1&time=1&ts=0&ys=0&cs=0&lb=1&sb=0&pb=4&mr=1&regions=').text
        ip_prot = str(ip_prot).replace('\r', '').replace('\t', '').replace('\n', '')
        print(ip_prot)
        ip_proxys = {
            'http': 'http:{}'.format(ip_prot),
            'https': 'https:{}'.format(ip_prot)
        }
        return ip_proxys

    def get_key(self, name):
        s = self.session
        url = 'http://chn.lottedfs.com/kr/search?comSearchWord={}&comCollection=GOODS&comTcatCD=&comMcatCD=&comScatCD=&comPriceMin=&comPriceMax=&comErpPrdGenVal_YN=&comHsaleIcon_YN=&comSaleIcon_YN=&comCpnIcon_YN=&comSvmnIcon_YN=&comGiftIcon_YN=&comMblSpprcIcon_YN=&comSort=RANK%2FDESC&comListCount=20'.format(
            name)
        r = s.get(url, proxies=self.ip)
        etr = etree.HTML(r.text)
        # print(r.text)
        mlist = etr.xpath(
            '//div[@id="searchTabPrdList"]/*/ul[@class="listUl"]/li[contains(@class,"productMd")]/a/@href')
        # print(mlist)
        pros = set()  # 创建一个集合
        for i in mlist:
            pro = re.findall("ga_adltCheckPrdDtlMove\((.*?),'O002','N'\);", i)[0].replace("'", "")
            pros.add(pro)
        proslist = list(pros)
        data = []
        for prd_opt in proslist:
            prd, opt = str(prd_opt).split(',')
            data.append(self.get_page(prd, opt))
        di = {
            "stu": 200,
            "message": "成功",
            "data": data
        }
        return di

    def get_page(self, prdNo, prdOptNo):
        s = self.session
        if prdNo and prdNo:
            url = 'http://chn.lottedfs.com/kr/product/productDetail?prdNo={}&prdOptNo={}'.format(prdNo, prdOptNo)
            url2 = 'http://chn.lottedfs.com/kr/product/productDetailBtmInfoAjax?prdNo={}&prdOptNo={}&previewYn='.format(
                prdNo, prdOptNo)
        elif prdNo and prdNo == '':
            url = 'http://chn.lottedfs.com/kr/product/productDetail?prdNo={}'.format(prdNo)
            url2 = 'http://chn.lottedfs.com/kr/product/productDetailBtmInfoAjax?prdNo={}&previewYn='.format(prdNo)
        else:
            return {}
        print(url)
        # time.sleep(0.2)
        r = s.get(url, proxies=self.ip)
        s.headers['Referer'] = url
        # time.sleep(0.2)
        r1 = s.get(url2, proxies=self.ip1)
        etr = etree.HTML(r.text)
        etr1 = etree.HTML(r1.text)

        分类 = etr.xpath('//div[@class="selectZone sizeS"]/select/option[@selected="selected"]/text()')
        分类 = '、'.join(分类)
        名字 = etr.xpath('//meta[@property="rb:itemName"]/@content')
        名字 = '、'.join(名字)
        原价 = etr.xpath('//meta[@property="rb:originalPrice"]/@content')
        原价 = '、'.join(原价)
        try:
            商品信息 = etr1.xpath('//h3[text()="商品信息"]/following-sibling::div[1]')[0]
            商品信息content = html.tostring(商品信息, encoding='utf-8').replace(b'\r', b'').replace(b'\t', b'').replace(b'\n',
                                                                                                                b'').decode(
                'utf-8')  # 把xpath 得到的对象，转换成html
        except:
            商品信息content = ''
        try:
            详细信息 = etr1.xpath('//h3[text()="详细信息"]/..')[0]
            详细信息content = html.tostring(详细信息, encoding='utf-8').replace(b'\r', b'').replace(b'\t', b'').replace(b'\n',
                                                                                                                b'').decode(
                'utf-8')  # 把xpath 得到的对象，转换成html
        except:
            详细信息content = ''

        di = {
            "catagory": 分类,
            "name": 名字,
            "price": 原价,
            "brief": 商品信息content,
            "detail": 详细信息content,
        }

        return di

def search_all():
    pass

if __name__ == '__main__':
    l = LETIAN()
    pa = l.get_key('Aqva Pour Homme 100ml 男士香水')
    print(pa)
