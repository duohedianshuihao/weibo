from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from gevent import monkey
monkey.patch_all()
import getpass, requests, os, time, pickle, re

class Login(object):
    """docstring for login"""
    def __init__(self, username, passwd, driver):
        self.username = username
        self.passwd = passwd
        self.driver = driver

    def index_page(self):
        self.driver.get('http://www.weibo.com')
        try:
            element = WebDriverWait(self.driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="pl_login_form"]/div/div[3]/div[3]/div/input'))
            )
            print 'initial page success'
        except:
            print 'initial page failed'
        usernameElement = self.driver.find_element_by_xpath('//*[@id="loginname"]')
        usernameElement.send_keys(self.username)
        pwElement = self.driver.find_element_by_xpath('//*[@id="pl_login_form"]/div/div[3]/div[2]/div/input')
        pwElement.send_keys(self.passwd)
        submitElement = self.driver.find_element_by_xpath('//*[@id="pl_login_form"]/div/div[3]/div[6]/a')
        submitElement.click()
        # try:
        #     vertifycodeElement = self.driver.find_element_by_xpath('//*[@id="pl_login_form"]/div/div[3]/div[3]/div/input')
        #     vertifyCode = raw_input('please input vertifyCode: ')
        #     vertifycodeElement.send_keys(vertifyCode)
        #     submitElement = self.driver.find_element_by_xpath('//*[@id="pl_login_form"]/div/div[3]/div[6]/a')
        #     submitElement.click()
        # except:
        #     pass
        try:
            element = WebDriverWait(self.driver, 1).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="plc_top"]/div/div/div[2]/a'))
            )
            print 'login success'
        except:
            print 'login failed'

    def find_the_user(self):
        targetUser = raw_input('user you want to find: ')
        searchElement = self.driver.find_element_by_xpath('//*[@id="plc_top"]/div/div/div[2]/input')
        searchElement.clear()
        searchElement.send_keys(targetUser.decode('utf-8'))
        searchBtn = self.driver.find_element_by_xpath('//*[@id="plc_top"]/div/div/div[2]/a')
        searchBtn.click()
        try:
            element = WebDriverWait(self.driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, '//*[@id="pl_common_searchTop"]/div[1]/ul/li/a[2]'))
            )
            print "page loaded"
        except:
            print 'page failed'
        self.driver.find_element_by_xpath('//*[@id="pl_common_searchTop"]/div[1]/ul/li/a[2]').click()
        try:
            element = WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="pl_user_feedList"]/div[1]/div/div/div'))
            )
            print 'list loaded'
        except:
            print 'list failed'
        soupList = BeautifulSoup(self.driver.page_source)
        userList = soupList.findAll('p', {'class': 'person_name'})
        for index, tag in enumerate(userList):
            print 'No.%d ' % index + tag.a.get('title') 
        resNum = raw_input("choose the user you want: ")
        resUID = soupList.findAll('div', {'class': 'person_pic'})[int(resNum)].a.img.get('uid')
        self.driver.get('http://photo.weibo.com/%s/albums' % resUID)
        try:
            element = WebDriverWait(self.driver, 3).until(
                EC.element_to_be_clickable((By.XPATH, '/html/body/div[2]/div[2]/div[2]/div[2]/ul/li[2]/div/div[1]/div/a'))
            )
            print 'photopage loaded'
        except:
            print 'photopage failed'
        self.driver.find_element_by_xpath('/html/body/div[2]/div[2]/div[2]/div[2]/ul/li[2]/div/div[1]/div/a').click()
        try:
            element = WebDriverWait(self.driver, 3).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="album_detail"]/div[1]/div[3]/ul'))
            )
            print 'photolink loaded'
        except:
            print 'photolink failed'
        return userList[int(resNum)].a.get('title')

    def get_links(self, resUser):
        links = {}
        i, page = 0, 0
        p = re.compile('small')
        while True:        
            page += 1
            try:
                self.driver.find_element_by_class_name('next')
                soup = BeautifulSoup(self.driver.page_source)
                temp = soup.findAll('dt', {'class', 'photo'})
                for item in temp:
                    links[i] = p.sub('large', item.a.img.get('src'))
                    print i, links[i]
                    i += 1
                try:
                    self.driver.find_element_by_class_name('next').click()
                except:
                    nextBtn = self.driver.find_element_by_class_name('next').click()
                    nextBtn.click()
                try:
                    element = WebDriverWait(self.driver, 3).until(
                        EC.presence_of_element_located((By.XPATH, '//*[@id="album_detail"]/div[1]/div[3]/ul'))
                    )
                    print '%s page loaded' % page
                except:
                    print 'error!'
            except:
                soup = BeautifulSoup(self.driver.page_source)
                temp = soup.findAll('dt', {'class', 'photo'})
                for item in temp:
                    links[i] = p.sub('large', item.a.img.get('src'))
                    print i, links[i]
                    i += 1
                break
            time.sleep(0.05)
        with open('%s_links' % resUser, 'w') as f:
            pickle.dump(links, f)
        return links

def download(resUser):
    with open('%s_links' % resUser) as f:
        links = pickle.load(f)
    try:
        os.mkdir('%s' % resUser)
        os.chdir('%s' % resUser)
    except:
        os.chdir('%s' % resUser)
    from gevent.pool import Pool
    if len(links) > 100:
        pool = Pool(100)
    else:
        pool = Pool(len(links))
    global p
    p = re.compile('large/(.*)')
    def saveLocal(i):
        global p
        photo = requests.get(links[i]).content
        with open("%s" % p.findall(links[i])[0], 'w') as f:
            f.write(photo)
        print '%d finished' % i
    pool.map(saveLocal, xrange(0, len(links)))        
    
       

def main():
    username = raw_input("username: ")
    passwd = getpass.getpass()
    driver = webdriver.Chrome()
    login = Login(username, passwd, driver)
    login.index_page()
    resUser = login.find_the_user()
    links = login.get_links(resUser)
    download(resUser)
    

if __name__ == '__main__':
    main()














       
