import xml.etree.ElementTree as ET
from flask import Flask,render_template,request,jsonify
import wzhifuSDK
from wzhifuSDK import order_num
import requests
import codecs
import json




app = Flask(__name__)
#配置mysql



print("服务器启动")
# 微信支付信息
#加签前信息
APP_ID = "wx19d346a2910ab88e"  # 你公众账号上的appid
MCH_ID = "1523807111"  # 你的商户号
API_KEY = "Cv1D2rLD4K6bnlzu3kOZasf24YfsTiOf"  # 微信商户平台(pay.weixin.qq.com) -->账户设置 -->API安全 -->密钥设置，设置完成后把密钥复制到这里
APP_SECRECT = "dc71b5f497d9a35162e7606a8dff6f78"
UFDODER_URL = "https://api.mch.weixin.qq.com/pay/unifiedorder"  # 该url是微信下单api
attach="id=1*money=200"
detail_before='{"cost_price":1000,"receipt_id":"wx123","goods_detail":[{"goods_id":"78","goods_name":"lunch","quantity":1,"price":1000},{"goods_id":"666","goods_name":"lunch","quantity":2,"price":1}]}'

spIp_before='183.57.22.10'
NOTIFY_URL_before='https://www.zhgaft.top:7000/returnMsg?username=wafer'


#加签后信息
@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/returnMsg',methods=['GET','POST'])
def returnMsg():
    print("ssssssssssssssssssssssssssssssssssssssssssssssssss!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    #responsess=request.data
    responsess=b'<xml>' \
               b'<appid><![CDATA[wx2421b1c4370ec43b]]></appid>' \
               b'<attach><![CDATA[{"userImfor":"3","money":"100"}]]></attach>' \
               b'</xml>'
    print(responsess)
    root=ET.fromstring(responsess)
    returnMsggg=root.find('attach').text
    attachContent=json.loads(returnMsggg) #解析拿到的attach包内容
    rechargeRequest=requests.get("http://localhost:7029/Interface/PC/GetPcStaff.ashx?informationNum="+attachContent['userImfor'])
    jsonObject=json.loads(rechargeRequest.content)
    #拿到人的Id,money
    getId=(jsonObject['pcInfo'])['Id']
    getMoney=attachContent['money']
    getUrl="http://localhost:7029/Interface/pc/PCDeposit.ashx?pcid="+str(getId)+"&Amount="+str(getMoney)
    # 充值反馈
    rechargeResponse=requests.get(getUrl)
    rechargeResponse=(json.loads(rechargeResponse.content.decode()))['Msg']
    if(rechargeResponse!="充值成功"):
        pass
    return '<xml><return_code><![CDATA[SUCCESS]]></return_code><return_msg><![CDATA[OK]]></return_msg></xml>'



@app.route('/login',methods=['GET','POST'])
def login():
    ramdom8_before = wzhifuSDK.random_str(8)
    out_trade_no_before = order_num()
    if request.method == 'POST': #如果请求方法时GET,返回login.html模板页面
        bodyContent = request.form['body']
        priceContent = request.form['price']
        dict1 = {'appid': APP_ID, 'mch_id': MCH_ID, 'nonce_str': ramdom8_before, 'body': bodyContent,
                  'device_info': '013467007045764','attach':attach,
                 'out_trade_no': out_trade_no_before, 'total_fee': priceContent, 'spbill_create_ip': spIp_before,
                 'notify_url': NOTIFY_URL_before, 'trade_type': 'MWEB'}

        Sign = wzhifuSDK.get_sign(dict1, API_KEY)

        dict2 = {'appid': '<![CDATA['+APP_ID+']]>', 'mch_id': '<![CDATA['+MCH_ID+']]>', 'nonce_str': '<![CDATA['+ramdom8_before+']]>', 'sign': '<![CDATA['+Sign+']]>', 'body': '<![CDATA['+bodyContent+']]>',
                 'device_info': '<![CDATA[013467007045764]]>','attach':'<![CDATA['+attach+']]>',
                 'out_trade_no': '<![CDATA['+out_trade_no_before+']]>', 'total_fee':'<![CDATA['+priceContent+']]>' , 'spbill_create_ip':  '<![CDATA['+spIp_before+']]>', 'notify_url':  '<![CDATA['+NOTIFY_URL_before+']]>',
                 'trade_type': '<![CDATA[MWEB]]>'}
        print(dict2)
        response = wzhifuSDK.wx_pay_unifiedorde(dict2, UFDODER_URL)
        print(response.decode())
        root=ET.fromstring(response.decode())
        returnUrl=root.find('mweb_url').text
        print(returnUrl)
        return jsonify(webUrl=returnUrl)


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers','Content-Type,Authorization,session_id')
    response.headers.add('Access-Control-Allow-Headers', 'GET,PUT,POST,DELETE,OPTIONS,HEAD')
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

if __name__ == '__main__':
    app.run( debug=True)
