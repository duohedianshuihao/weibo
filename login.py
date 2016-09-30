import requests, getpass, re, base64, binascii, pickle, os, time
import json
from bs4 import BeautifulSoup
import rsa


headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'
}

def getinfo():
    username = raw_input('Username: ')
    passwd = getpass.getpass()
    return username, passwd

def prelogin(session):
    prelogUrl = 'https://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&rsakt=mod&client=ssologin.js(v1.4.18)'
    r = session.get(url = prelogUrl, headers = headers, verify = False).content
    res = re.findall('\{.*\}', r)[0]
    # res = eval(res)
    res = json.loads(res)
    return res['servertime'], res['pubkey'], res['nonce'], res['rsakv']

# RSAKey.setPublic(me.rsaPubkey, "10001")    
# password = RSAKey.encrypt([me.servertime, me.nonce].join("\t") + "\n" + password
def get_sp(pubkey, servertime, nonce, passwd):
    rsa_e = 65537
    rsa_n = int(pubkey, 16)
    message = str(servertime) + '\t' + str(nonce) + '\n' + passwd
    key = rsa.PublicKey(rsa_n, rsa_e)
    rsa_passwd = rsa.encrypt(message, key)
    return binascii.b2a_hex(rsa_passwd)

def make_data(su, sp, servertime, nonce, rsakv):
    with open('login_data.json', 'r') as f:    
        data = json.load(f)
    data['su'] = su
    data['sp'] = sp
    data['servertime'] = servertime
    data['nonce'] = nonce
    data['rsakv'] = rsakv
    return data

def login(session, data):
    loginURL = 'http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.4.18)'
    r = session.post(url = loginURL, data = data)
    try:
        tempURL = re.findall('location.replace\(\'(.*)\'\)', r.content.decode('gbk'))[0]
    except:
        print 'username or passwd error, please try again!'
        exit()
    with open('login_cookie', 'w') as f:
        pickle.dump(requests.utils.dict_from_cookiejar(r.cookies), f)
    session.get(url = tempURL)
    r = session.get('http://weibo.com/u/3288804021/home')
    return r

def main():
    if os.path.exists('login_cookie'):
        with open('login_cookie', 'r') as f:
            cookies = requests.utils.cookiejar_from_dict(pickle.load(f))
        s = requests.session()
        s.headers = headers
        r = s.get('http://weibo.com', cookies = cookies)
    else:
        username, passwd = getinfo()
        s = requests.session()
        s.headers = headers
        servertime, pubkey, nonce, rsakv = prelogin(s)
        su = base64.b64encode(username)     # username = sinaSSOEncoder.base64.encode(urlencode(username));
        sp = get_sp(pubkey, servertime, nonce, passwd)  
        data = make_data(su, sp, servertime, nonce)
        r = login(s, data)
    res_name = re.findall('\$CONFIG\[\'nick\'\]=\'(.*)\'', r.content)
    if res_name:
        print res_name[0]
    else:
        print 'ERROR! Please try again!'
if __name__ == '__main__':
    main()