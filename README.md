## 项目介绍
> 在线问答社区：者也

## 系统设计概述
> 系统采用flask作为web开发框架，sqlalchemy实现数据库的操作。服务端推送消息采用twisted&websocket实现。tornado作为web服务器进行系统的部署。

## 系统功能概述
### 已完成的功能
- 用户信息
	- 邮件确认
	- 基本资料修改
	- 密码重置
	- 用户动态
	- 我的回答
	- 我的提问
	- 我的关注
　
- 问答
	- 提问
	- 回答问题
	- 评论回答
　
- 关注
	- 关注话题
	- 关注问题
	- 关注用户
　
- 首页显示
	- 关注话题下的优秀问题
	- 关注的用户的动态
　


- 权限管理

	- 管理员对于话题类别的管理
	- 管理员对于话题的管理
	- 管理员对于用户的管理
　
### 未完成的功能

- 服务端消息的推送

	- 被关注的通知
	- 关注问题被回答的通知

## 系统页面展示
![登录界面](http://i.imgur.com/H6wsWBm.png)


![全局](http://i.imgur.com/7KqQoeA.png)

![提问](http://i.imgur.com/hJzN3yQ.png)

![个人主页](http://i.imgur.com/l8NvR7k.png)

![话题动态](http://i.imgur.com/IAVBJVq.png)

![话题广场](http://i.imgur.com/8PJKxea.png)
　
![问题界面](http://i.imgur.com/MACeAiR.png)

## 其他问题
注册时尽量采用网易邮箱注册。若收不到确认邮件，在垃圾邮件里找一下。