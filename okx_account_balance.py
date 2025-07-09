#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OKX API v5 账户余额查询示例
根据 https://www.okx.com/docs-v5/zh/#overview-rest-authentication 文档实现
"""

import hmac
import hashlib
import base64
import json
import time
from datetime import datetime
import requests


class OKXAPIClient:
    def __init__(self, api_key, secret_key, passphrase, is_sandbox=False):
        """
        初始化OKX API客户端
        
        Args:
            api_key (str): API密钥
            secret_key (str): 秘钥
            passphrase (str): 密码短语
            is_sandbox (bool): 是否使用沙盒环境
        """
        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = passphrase
        
        # 根据是否沙盒环境设置基础URL
        if is_sandbox:
            self.base_url = "https://www.okx.com"  # 实际环境，沙盒环境URL需要根据文档确认
        else:
            self.base_url = "https://www.okx.com"
    
    def _get_timestamp(self):
        """获取UTC时间戳，格式为ISO 8601"""
        return datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
    
    def _generate_signature(self, timestamp, method, request_path, body=''):
        """
        生成签名
        
        Args:
            timestamp (str): 时间戳
            method (str): HTTP方法 (GET, POST等)
            request_path (str): 请求路径
            body (str): 请求体，GET请求为空字符串
        
        Returns:
            str: Base64编码的签名
        """
        # 创建prehash字符串: timestamp + method + requestPath + body
        prehash = timestamp + method.upper() + request_path + body
        
        # 使用HMAC SHA256和SecretKey签名
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            prehash.encode('utf-8'),
            hashlib.sha256
        ).digest()
        
        # Base64编码
        return base64.b64encode(signature).decode('utf-8')
    
    def _get_headers(self, timestamp, method, request_path, body=''):
        """
        获取请求头
        
        Args:
            timestamp (str): 时间戳
            method (str): HTTP方法
            request_path (str): 请求路径
            body (str): 请求体
        
        Returns:
            dict: 请求头字典
        """
        signature = self._generate_signature(timestamp, method, request_path, body)
        
        return {
            'OK-ACCESS-KEY': self.api_key,
            'OK-ACCESS-SIGN': signature,
            'OK-ACCESS-TIMESTAMP': timestamp,
            'OK-ACCESS-PASSPHRASE': self.passphrase,
            'Content-Type': 'application/json'
        }
    
    def get_account_balance(self, ccy=None):
        """
        查询账户余额
        
        Args:
            ccy (str, optional): 币种，如'BTC'。不指定则查询所有币种余额
        
        Returns:
            dict: API响应结果
        """
        # 构建请求路径
        request_path = '/api/v5/account/balance'
        if ccy:
            request_path += f'?ccy={ccy}'
        
        # 生成时间戳和请求头
        timestamp = self._get_timestamp()
        headers = self._get_headers(timestamp, 'GET', request_path)
        
        # 发送请求
        url = self.base_url + request_path
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {'error': f'请求失败: {str(e)}'}
        except json.JSONDecodeError as e:
            return {'error': f'JSON解析失败: {str(e)}'}
    
    def format_balance_response(self, response):
        """
        格式化余额响应，便于阅读
        
        Args:
            response (dict): API响应
        
        Returns:
            None: 直接打印格式化结果
        """
        if 'error' in response:
            print(f"❌ 错误: {response['error']}")
            return
        
        if response.get('code') != '0':
            print(f"❌ API错误: {response.get('msg', '未知错误')}")
            return
        
        data = response.get('data', [])
        if not data:
            print("📊 账户余额信息为空")
            return
        
        print("💰 账户余额信息")
        print("=" * 60)
        
        for account in data:
            details = account.get('details', [])
            if not details:
                print("   暂无余额信息")
                continue
            
            for detail in details:
                ccy = detail.get('ccy', 'N/A')
                cash_bal = detail.get('cashBal', '0')
                available_bal = detail.get('availBal', '0')
                frozen_bal = detail.get('frozenBal', '0')
                
                print(f"   币种: {ccy}")
                print(f"   ├─ 总余额: {cash_bal}")
                print(f"   ├─ 可用余额: {available_bal}")
                print(f"   └─ 冻结余额: {frozen_bal}")
                print("   " + "-" * 30)


def main():
    """
    主函数：演示如何使用OKX API查询账户余额
    """
    print("🚀 OKX API v5 账户余额查询示例")
    print("=" * 60)
    
    # ⚠️ 警告：请将以下占位符替换为您的实际API凭据
    # 不要在代码中硬编码真实的API凭据！
    # 建议使用环境变量或配置文件
    
    API_KEY = "YOUR_API_KEY"  # 请替换为您的API Key
    SECRET_KEY = "YOUR_SECRET_KEY"  # 请替换为您的Secret Key  
    PASSPHRASE = "YOUR_PASSPHRASE"  # 请替换为您的Passphrase
    
    # 检查是否使用了占位符
    if "YOUR_" in API_KEY or "YOUR_" in SECRET_KEY or "YOUR_" in PASSPHRASE:
        print("⚠️  请先配置您的API凭据！")
        print("\n📝 配置步骤：")
        print("1. 登录OKX官网")
        print("2. 进入API管理页面")
        print("3. 创建新的API Key")
        print("4. 将API Key、Secret Key和Passphrase替换到代码中")
        print("\n🔒 安全提醒：")
        print("- 不要在代码中硬编码API凭据")
        print("- 建议使用环境变量或配置文件")
        print("- 确保API Key权限设置合理")
        return
    
    # 创建API客户端
    client = OKXAPIClient(
        api_key=API_KEY,
        secret_key=SECRET_KEY,
        passphrase=PASSPHRASE,
        is_sandbox=False  # 设为True使用沙盒环境
    )
    
    print("📡 正在查询账户总余额...")
    # 查询所有币种余额
    response = client.get_account_balance()
    client.format_balance_response(response)
    
    print("\n" + "=" * 60)
    print("📡 正在查询BTC余额...")
    # 查询特定币种余额（示例：BTC）
    btc_response = client.get_account_balance('BTC')
    client.format_balance_response(btc_response)
    
    print("\n✅ 查询完成！")
    print("\n📖 更多API文档: https://www.okx.com/docs-v5/zh/")


if __name__ == "__main__":
    main()