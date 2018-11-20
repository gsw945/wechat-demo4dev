from datetime import datetime
import uuid

from flask import request, abort, jsonify

from wechatpy import parse_message, create_reply
from wechatpy.utils import check_signature
from wechatpy.exceptions import (
    InvalidSignatureException,
    InvalidAppIdException,
)
from wechatpy import WeChatClient
from wechatpy.replies import ImageReply


def random_uuid():
    '''获取随机uuid'''
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    return uuid.uuid5(uuid.NAMESPACE_DNS, ts).hex


CFG = {
    'APPID': '<Your APPID>',
    'SECRET': '<Your SECRET>',
    'TOKEN': '<Your TOKEN>',
    'AES_KEY': '<Your AES_KEY>'
}


def process_response(sub_domain):
    global CFG
    print(sub_domain)
    return wechat_auto_reply(CFG)

def get_img_reply(CFG, msg):
    client = client = WeChatClient(CFG['APPID'], CFG['SECRET'])
    reply_info = client.message.get_autoreply_info()
    media_id = reply_info['message_default_autoreply_info']['content']

    img_rpy = ImageReply()
    img_rpy.media_id = media_id
    reply = create_reply(img_rpy, msg)
    return reply

def print_info(msg):
    '''
    公共属性: http://docs.wechatpy.org/zh_CN/master/messages.html#id2
    '''
    print('消息ID:', msg.id)
    print('来源用户:', msg.source)
    print('目标用户:', msg.target)
    print('发送时间:', msg.create_time)
    print('消息类型:', msg.type)

def wechat_auto_reply(CFG):
    # http://flask.pocoo.org/docs/1.0/api/#incoming-request-data
    print(request.url)
    signature = request.args.get('signature', '')
    timestamp = request.args.get('timestamp', '')
    nonce = request.args.get('nonce', '')
    encrypt_type = request.args.get('encrypt_type', 'raw')
    msg_signature = request.args.get('msg_signature', '')
    try:
        check_signature(CFG['TOKEN'], signature, timestamp, nonce)
    except InvalidSignatureException:
        abort(403)
    if request.method == 'GET':
        echo_str = request.args.get('echostr', '')
        return echo_str

    # POST request
    if encrypt_type == 'raw':
        # plaintext mode
        print('明文模式')
        msg = parse_message(request.data)
        print_info(msg)
        # import ipdb as pdb; pdb.set_trace()
        if msg.type == 'text':
            if msg.content.lower() in ['img', 'image']:
                reply = get_img_reply(CFG, msg)
            else:
                reply = create_reply(msg.content, msg)
        else:
            reply = create_reply('Sorry, can not handle this for now', msg)
        return reply.render()
    else:
        # encryption mode
        print('加密模式')
        from wechatpy.crypto import WeChatCrypto

        crypto = WeChatCrypto(CFG['TOKEN'], CFG['AES_KEY'], CFG['APPID'])
        try:
            msg = crypto.decrypt_message(
                request.data,
                msg_signature,
                timestamp,
                nonce
            )
        except (InvalidSignatureException, InvalidAppIdException):
            abort(403)
        else:
            # import ipdb as pdb; pdb.set_trace()
            msg = parse_message(msg)
            print_info(msg)
            if msg.type == 'text':
                # reply = create_reply(msg.content, msg)
                if msg.content.lower() in ['img', 'image']:
                    reply = get_img_reply(CFG, msg)
                else:
                    reply_msg = msg.content + '\n' + 'https://blog.gsw945.com/'
                    reply = create_reply(reply_msg, msg)
            else:
                if msg.type == 'link':
                    print(type(msg), dir(msg))
                    from wechatpy.replies import ArticlesReply
                    from wechatpy.utils import ObjectDict

                    reply = ArticlesReply(message=msg)
                    '''
                    # simply use dict as article
                    reply.add_article({
                        'title': 'test',
                        'description': 'test',
                        'image': 'image url',
                        'url': 'url'
                    })
                    '''
                    # or you can use ObjectDict
                    article = ObjectDict()
                    article.title = 'JS-SDK'
                    article.description = '尝试一下JS-SDK'
                    article.image = 'https://res.wx.qq.com/mpres/htmledition/images/bg/bg_login_banner_v53a7b38.jpg'
                    article.url = 'http://demo.wx.gsw945.com/web/hello.html'
                    reply.add_article(article)
                else:
                    reply = create_reply('Sorry, can not handle this for now', msg)
            return crypto.encrypt_message(reply.render(), nonce, timestamp)


def jsapi_response(sub_domain):
    global CFG
    client = WeChatClient(CFG['APPID'], CFG['SECRET'])
    noncestr = random_uuid()
    ticket = client.jsapi.get_jsapi_ticket()
    timestamp = datetime.now().timestamp()

    '''
    from furl import furl

    origin_uri = request.headers.get('X-Origin-URI')
    host = request.headers.get('Host').strip(':')
    scheme = request.headers.get('X-Scheme')
    f = furl(origin_uri)
    f.set(host=host, scheme=scheme)
    url = f.url
    '''
    url = request.values.get('url')

    signature = client.jsapi.get_jsapi_signature(noncestr, ticket, timestamp, url)
    from pprint import pprint; pprint(signature)
    return jsonify({
        'appId': CFG['APPID'],
        'nonceStr': noncestr,
        'timestamp': timestamp,
        'signature': signature
    })