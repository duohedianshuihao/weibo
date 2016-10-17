## 微博小爬虫

### 实现功能
- 登录微博账号
- 查找用户
- 抓取用户微博配图并保存到本地

### 登陆过程参考
[传送门1](http://www.jianshu.com/p/36a39ea71bfd)
	
[传送门2](http://www.jianshu.com/p/816594c83c74)

微博登陆过程比较麻烦，用户名密码加密验证码。具体的还是看上面传送门吧，我都是照着上面做的。

### 丑话说在前头
笔者很菜…

微博页面是动态加载的，所以爬去起来比较麻烦，selenium可以解决动态加载，但是我才学会requests没几天，没有深入尝试它。偷懒找到了weibo.cn，这个不需要动态加载而且好像连登陆都不用那么麻烦==# 因为之前的登陆是先写好的，就不改了。后面的就从这里下手了，嘿嘿嘿……

### 增加selenium实现
增加selenium+webdriver实现的一个最主要的原因就是weibo.cn里面的图片不全……

#### 解决问题
解决动态加载，用的是selenium+chrome实现。
（感觉没有界面的PhantomJS应该更好一点，但是用的时候老是报"Element is not currently interactable and may not be manipulated"错误，用chrome就一切正常）

#### 存在的问题
- 不是很稳定，有时候没结束会触发结束条件，大概是[酱](http://stackoverflow.com/questions/36013135/python-with-selenium-element-is-not-attached-to-the-page-document)
- 加载时间比较长

#### 实现功能
跟上面的基本上一毛一样
