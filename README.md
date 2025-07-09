# OKX API v5 账户余额查询示例

本项目演示如何使用 OKX API v5 查询账户余额。根据 [OKX API v5 官方文档](https://www.okx.com/docs-v5/zh/#overview-rest-authentication) 实现。

## 功能特性

- ✅ 完整的 OKX API v5 认证实现
- ✅ 符合 HMAC SHA256 签名算法
- ✅ 支持查询所有币种余额
- ✅ 支持查询特定币种余额  
- ✅ 安全的环境变量配置
- ✅ 友好的输出格式化
- ✅ 完善的错误处理

## 文件说明

```
├── okx_account_balance.py    # 基础版本（硬编码API密钥）
├── okx_balance_secure.py     # 安全版本（使用环境变量）
├── requirements.txt          # 依赖包列表
├── .env.example             # 环境变量示例文件
└── README.md                # 说明文档
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 获取 OKX API 凭据

1. 登录 [OKX 官网](https://www.okx.com)
2. 进入 **个人中心** > **API**
3. 创建新的 API Key，记录以下信息：
   - API Key
   - Secret Key  
   - Passphrase

⚠️ **重要提醒**：
- 确保为 API Key 设置合适的权限（只需要"读取"权限即可查询余额）
- 如有需要，可以绑定 IP 地址以增强安全性
- 切勿与他人分享您的 API 凭据

### 3. 配置方式

#### 方式一：使用环境变量（推荐）

1. 复制环境变量示例文件：
```bash
cp .env.example .env
```

2. 编辑 `.env` 文件，填入您的真实 API 凭据：
```bash
OKX_API_KEY=your_real_api_key
OKX_SECRET_KEY=your_real_secret_key
OKX_PASSPHRASE=your_real_passphrase
OKX_SANDBOX=false
```

3. 加载环境变量：
```bash
# Linux/Mac
source .env

# Windows PowerShell
Get-Content .env | ForEach-Object {
    $name, $value = $_.split('=')
    Set-Content env:\$name $value
}
```

4. 运行安全版本：
```bash
python okx_balance_secure.py
```

#### 方式二：直接在代码中配置

1. 编辑 `okx_account_balance.py` 文件
2. 将以下占位符替换为您的真实凭据：
```python
API_KEY = "your_real_api_key"
SECRET_KEY = "your_real_secret_key"  
PASSPHRASE = "your_real_passphrase"
```

3. 运行基础版本：
```bash
python okx_account_balance.py
```

## API 说明

### 认证机制

根据 OKX API v5 文档，所有私有接口都需要进行签名认证：

1. **请求头要求**：
   - `OK-ACCESS-KEY`: API 密钥
   - `OK-ACCESS-SIGN`: 签名
   - `OK-ACCESS-TIMESTAMP`: UTC 时间戳
   - `OK-ACCESS-PASSPHRASE`: 密码短语

2. **签名算法**：
   ```
   signature = base64.encode(hmac_sha256(timestamp + method + requestPath + body, secretKey))
   ```

### API 端点

- **查询账户余额**: `GET /api/v5/account/balance`
- **查询特定币种**: `GET /api/v5/account/balance?ccy=BTC`

### 响应格式

成功响应示例：
```json
{
  "code": "0",
  "msg": "",
  "data": [
    {
      "details": [
        {
          "ccy": "BTC",
          "cashBal": "0.1",
          "availBal": "0.08", 
          "frozenBal": "0.02"
        }
      ]
    }
  ]
}
```

## 使用示例

### 查询所有币种余额

```python
from okx_balance_secure import OKXAPIClient, load_credentials

# 加载凭据
api_key, secret_key, passphrase, is_sandbox = load_credentials()

# 创建客户端
client = OKXAPIClient(api_key, secret_key, passphrase, is_sandbox)

# 查询余额
response = client.get_account_balance()
client.format_balance_response(response)
```

### 查询特定币种余额

```python
# 查询 BTC 余额
btc_response = client.get_account_balance('BTC')
client.format_balance_response(btc_response)
```

## 输出示例

```
🚀 OKX API v5 账户余额查询示例 (安全版本)
============================================================
🔧 环境: 生产
📡 正在查询账户总余额...
💰 账户余额信息
============================================================
   币种: USDT
   ├─ 总余额: 1000.5
   ├─ 可用余额: 900.5
   └─ 冻结余额: 100.0
   ------------------------------
   币种: BTC  
   ├─ 总余额: 0.1
   ├─ 可用余额: 0.08
   └─ 冻结余额: 0.02
   ------------------------------
✅ 查询完成！
```

## 错误处理

常见错误类型：

1. **认证失败**：
   - 检查 API 凭据是否正确
   - 确认 API Key 权限设置
   - 验证时间戳是否准确

2. **网络错误**：
   - 检查网络连接
   - 确认请求 URL 是否正确

3. **参数错误**：
   - 验证币种代码格式
   - 检查请求参数

## 安全建议

- ❌ 不要在代码中硬编码 API 凭据
- ✅ 使用环境变量存储敏感信息
- ✅ 为 API Key 设置最小必要权限
- ✅ 定期轮换 API 凭据
- ✅ 使用 IP 白名单增强安全性
- ✅ 不要将包含真实凭据的代码提交到版本控制系统

## 相关链接

- [OKX API v5 官方文档](https://www.okx.com/docs-v5/zh/)
- [OKX 官网](https://www.okx.com)
- [API 管理页面](https://www.okx.com/account/my-api)

## 许可证

本项目仅供学习和参考使用。使用时请遵守 OKX 的服务条款和 API 使用规范。

## 免责声明

本代码仅作为技术示例，不构成投资建议。使用时请确保：
- 理解并接受 OKX 的服务条款
- 妥善保管您的 API 凭据
- 遵守相关法律法规
