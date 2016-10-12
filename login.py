import requests, getpass, re, base64, binascii, pickle, time, os
import json
from bs4 import BeautifulSoup
import rsa
from PIL import Image

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
    vertifyURL = 'http://login.sina.com.cn/cgi/pin.php'
    r = session.get(vertifyURL)
    with open('yanzhengma.png', 'w') as f:
        f.write(r.content)
    image = Image.open('yanzhengma.png')
    image.show()
    door = raw_input("test code: ")
    data['door'] = door
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
    r = session.get('http://weibo.cn/')
    return r

# def test(session):
#     data = {
#         'location': 'v6_content_home',
#         'group_source': 'group_all',
#         'rid': '0_0_8_2669662868472703700',
#         'version': 'mini',
#         'qid': 'heart',
#         'mid': "4025855971811553",
#         'like_src': '1'
#     }
#     headers = {
#         'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36',
#         'Referer': 'http://weibo.com/u/3288804021/home' # necessary
#     }
#     likeURL = 'http://weibo.com/aj/v6/like/add?ajwvr=6'
#     r = session.post(url = likeURL, data = data, headers = headers)
#     print r.content
#     print r.status_code
def find_user(findUsername, session):
    data = {
        'keyword': findUsername,
        'suser': '2'
    }
    findUrl = 'http://weibo.cn/find/user'
    r = session.post(url = findUrl, data = data)
    soup = BeautifulSoup(r.content)
    resUrl = soup.findAll('tr')
    for index, item in enumerate(resUrl):
        print index, item.contents[1].a.text
    num = raw_input('choose the number you want: ')
    userUrl = resUrl[int(num)].contents[1].a.get('href')
    name = resUrl[int(num)].contents[1].a.text
    page = session.get(url = 'http://weibo.cn'+userUrl)
    return page, name

def get_photoUrl(page, session):
    soup = BeautifulSoup(page.content)
    tempUrl = soup.findAll('span', {'class': 'pmsl'})[0].a.get('href')
    temp = session.get(url = 'http://weibo.cn'+tempUrl)
    pagesoup = BeautifulSoup(temp.content)
    photoUrl = pagesoup.findAll('img', {'alt': '微博配图'})[0].parent.get('href')
    return photoUrl

def save_photo(photoUrl, session, name):
    photoPage = session.get('http://weibo.cn'+photoUrl)    
    photosoup = BeautifulSoup(photoPage.content)
    pageNum = photosoup.findAll('input', {'type': 'hidden'})[0].get('value')
    try:
        os.mkdir('%s' % name)
    except:
        pass
    photoLink = photosoup.findAll('img', {'class': 'c'})
    for index, item in enumerate(photoLink):
        p = re.compile('square')
        photo = session.get(p.sub('large', item.get('src'))).content
        with open('%s/photo%s' % (name, index), 'w') as f:
            f.write(photo)
        print '%s finished' % index


def main():
    try:
        with open('login_cookie', 'r') as f:
            cookies = requests.utils.cookiejar_from_dict(pickle.load(f))
        s = requests.session()
        s.headers = headers
        s.cookies = cookies
        r = s.get('http://weibo.cn/')
    except:
        username, passwd = getinfo()
        s = requests.session()
        s.headers = headers
        servertime, pubkey, nonce, rsakv = prelogin(s)
        su = base64.b64encode(username)     # username = sinaSSOEncoder.base64.encode(urlencode(username));
        sp = get_sp(pubkey, servertime, nonce, passwd)  
        data = make_data(su, sp, servertime, nonce, rsakv)
        r = login(s, data)
    soup = BeautifulSoup(r.content)
    user_name = soup.findAll('div', {'class': 'ut'})
    if user_name:
        print user_name[0].contents[0]
    else:
        print 'ERROR! Please try again! Maybe the cookie does not work'
        exit()
    findUsername = raw_input('the user you want to find: ')
    page, name = find_user(findUsername, s)
    photoUrl = get_photoUrl(page, s)
    save_photo(photoUrl, s, name)    

if __name__ == '__main__':
    main()