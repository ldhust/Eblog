# Eblog
本项目是参考《Flask Web开发》一书扩展开发的一个简易博客，实现了一个简易博客该有的基本功能，包括：  
* 账户注册与权限分配
* 账户密码与注册邮箱修改
* 博客发文、分类与编辑
* 个人主页资料编辑
* 用户互相关注与显示
* 用户文章评论与点赞  

## 部署  
《Flask Web开发》一书原项目是部署在Heroku平台上的，这里没有照做，只部署在了本地。具体思路参考文章[https://realpython.com/kickstarting-flask-on-ubuntu-setup-and-deployment/](https://realpython.com/kickstarting-flask-on-ubuntu-setup-and-deployment/ "ubuntu部署")，采用了Nginx+Gunicorn+Supervisor+MySQL的结构来搭建的服务器，结构如下图：  
![部署结构](https://files.realpython.com/media/flask-nginx-gunicorn-architecture.012eb1c10f5e.jpg "部署示意图")  

## 基础功能展示
1. 网站主页

![index](https://github.com/ldhust/Eblog/blob/master/img/index.png "网站主页")  
2. 注册界面

![register](https://github.com/ldhust/Eblog/blob/master/img/register.png "注册界面")  
3. 登录界面

![login](https://github.com/ldhust/Eblog/blob/master/img/login.png "登录界面")  
4. 密码重置

![resetpassword](https://github.com/ldhust/Eblog/blob/master/img/resetpassword.png "密码重置")  
5. 用户主页

![userindex](https://github.com/ldhust/Eblog/blob/master/img/userindex.png "用户主页")  
6. 用户菜单

![usermenu](https://github.com/ldhust/Eblog/blob/master/img/usermenu.png "用户菜单")  
7. 文章编辑

![article](https://github.com/ldhust/Eblog/blob/master/img/article.png "文章编辑")  
8. 评论点赞

![comment](https://github.com/ldhust/Eblog/blob/master/img/comment.png "评论点赞")  
9. 用户资料

![profile](https://github.com/ldhust/Eblog/blob/master/img/profile.png "用户资料")  
10. 关注信息

![followed](https://github.com/ldhust/Eblog/blob/master/img/followed.png "关注信息")
