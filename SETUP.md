# XiaoYue 完整部署教程

从零到上线，每一步都有。全程约 20 分钟。

---

## 第一步：注册企业微信（免费）

1. 打开 https://work.weixin.qq.com/
2. 点击「立即注册」
3. 随便填公司名（比如"小玥科技"）
4. 扫码绑定你的微信（用你**主号**扫，不影响正常使用）
5. 注册完登录管理后台

---

## 第二步：创建应用，拿到 5 个参数

进入管理后台后：

```
应用管理 → 自建 → 创建应用
```

1. 应用名称：填「小玥」
2. 上传一个可爱的头像
3. 可见范围：选你所在的部门（只有你能看到这个应用）

创建完后，**记下这 3 个值**：

| 值 | 在哪里 | 示例 |
|----|--------|------|
| Corp ID | 首页「企业信息」 | `ww1234567890abcdef` |
| Agent ID | 应用详情页顶部 | `1000002` |
| Secret | 应用详情页，点「查看」 | `xxxxxxxxxxxxxxxxxxxx` |

然后进入应用详情页 → **接收消息** → **设置API接收**：

4. 点「随机获取」生成 **Token**，记下来
5. 点「随机获取」生成 **EncodingAESKey**，记下来
6. URL 先随便填 `https://example.com/callback`（部署后回来改）
7. **先不要点保存**（URL 还不对，保存会失败）

现在你有了 **5 个参数**：
```
WECOM_CORP_ID    = ww1234567890abcdef
WECOM_AGENT_ID   = 1000002
WECOM_SECRET     = xxxxxxxxxxxxxxxxxxxx
WECOM_TOKEN      = abcdefghijk123456
WECOM_AES_KEY    = abcdefghijklmnopqrstuvwxyz1234567890ABC
```

---

## 第三步：配置项目

编辑 `C:\Users\UserX\wecom-bot\.env`：

```bash
# DeepSeek API（你应该已经有了）
DEEPSEEK_API_KEY=sk-xxxxxxxx

# 企业微信（把上面 5 个值填进去）
WECOM_CORP_ID=ww1234567890abcdef
WECOM_AGENT_ID=1000002
WECOM_SECRET=xxxxxxxxxxxxxxxxxxxx
WECOM_TOKEN=abcdefghijk123456
WECOM_AES_KEY=abcdefghijklmnopqrstuvwxyz1234567890ABC

# 可选：只回复某个用户（不填=回复所有人）
# WECOM_ALLOWED_USER=
```

---

## 第四步：本地测试

```bash
cd C:\Users\UserX\wecom-bot
pip install -r requirements.txt
python main.py
```

看到这个就对了：
```
  XiaoYue - WeCom AI Girlfriend Bot v3
  Local:  http://localhost:8080
  Status: http://localhost:8080/
  Health: http://localhost:8080/health
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:8080
```

打开 http://localhost:8080 ，看到小玥的状态页就说明服务跑起来了。

---

## 第五步：部署到 Railway（云端 24 小时）

### 5.1 创建 GitHub 仓库

```bash
cd C:\Users\UserX\wecom-bot
git init
git add .
git commit -m "init: XiaoYue WeCom bot"
```

然后去 https://github.com/new 创建仓库（比如叫 `xiaoyue-bot`），**不要勾选 Add README**。

创建后 GitHub 会给你几条命令，类似：
```bash
git remote add origin https://github.com/你的用户名/xiaoyue-bot.git
git push -u origin main
```

### 5.2 部署到 Railway

1. 打开 https://railway.app/ → 用 GitHub 登录
2. 点 `New Project` → `Deploy from GitHub`
3. 选刚才推送的 `xiaoyue-bot` 仓库
4. Railway 会自动检测 Python 项目并部署
5. 进入项目 → `Variables` → 添加环境变量：

把 `.env` 里的所有变量一个一个加进去：
```
DEEPSEEK_API_KEY = sk-xxxxxxxx
WECOM_CORP_ID    = ww1234567890abcdef
WECOM_AGENT_ID   = 1000002
WECOM_SECRET     = xxxxxxxxxxxxxxxxxxxx
WECOM_TOKEN      = abcdefghijk123456
WECOM_AES_KEY    = abcdefghijklmnopqrstuvwxyz1234567890ABC
```

6. 等待部署完成，Railway 会给你一个域名，类似：
   `https://xiaoyue-bot.up.railway.app`

7. 测试：访问 `https://xiaoyue-bot.up.railway.app/health`
   看到 `{"status":"ok"}` 就对了。

---

## 第六步：配置企业微信回调

回到企业微信管理后台：

```
应用管理 → 小玥 → 接收消息 → 设置API接收
```

把 URL 改成：
```
https://xiaoyue-bot.up.railway.app/callback
```

**注意**: 结尾的 `/callback` 一定要加上！

Token 和 AES Key 保持之前的值不变。

点击「保存」→ 看到 **「保存成功」** 就大功告成了！

---

## 第七步：开始聊天

1. 打开普通微信
2. 找到「企业微信」联系人（你在注册时扫码绑定的那个）
3. 你会在通讯录里看到「小玥科技」（或你起的公司名）
4. 点进去 → 点「小玥」应用
5. 发消息！小玥会回复你

---

## 完整文件结构

```
wecom-bot/
├── .env              ← 填好API Key + WeCom参数
├── .env.example      ← 配置模板
├── main.py           ← 启动入口
├── Procfile          ← Railway部署描述
├── requirements.txt  ← Python依赖
├── README.md
├── sessions/         ← 会话存储（自动创建）
└── src/
    ├── config.py        ← 所有配置+女友人格
    ├── wecom_crypto.py  ← 消息加解密
    ├── wecom_api.py     ← API客户端
    ├── wecom_server.py  ← FastAPI服务
    ├── ai_client.py     ← DeepSeek + 情绪系统
    ├── session_manager.py ← 会话管理
    ├── human_simulator.py ← 人类行为模拟
    └── message_handler.py ← 消息处理
```

---

## 常用命令（发给小玥）

| 消息 | 作用 |
|------|------|
| 随便说话 | 正常聊天 |
| `#清除` | 清除对话记忆 |
| `#帮助` | 显示帮助 |
| `#状态` | 看小玥在不在线 |

---

## 有问题？

- 回调保存失败 → 检查 Railway 域名是否拼写正确，检查 `/health` 能不能访问
- 发消息不回复 → 看 Railway 日志（Railway → 项目 → Deployments → View Logs）
- 对方看不到 @公司名 → 企业微信就是这样显示的，没法去掉，但可以起个可爱的公司名
