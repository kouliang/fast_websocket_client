#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OKX API v5 账户余额查询示例 - 安全版本（使用环境变量）
根据 https://www.okx.com/docs-v5/zh/#overview-rest-authentication 文档实现
"""

import os
import hmac
import hashlib
import base64
import json
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
            self.base_url = "https://www.okx.com"  # 沙盒环境URL
        else:
            self.base_url = "https://www.okx.com"
    
    def _get_timestamp(self):
        """获取UTC时间戳，格式为ISO 8601"""
        return datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
    
    def _generate_signature(self, timestamp, method, request_path, body=''):
        """
        生成签名
        
        根据OKX文档的签名算法：
        1. 创建prehash字符串: timestamp + method + requestPath + body
        2. 使用HMAC SHA256和SecretKey签名
        3. Base64编码
        
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
        
        根据OKX文档要求的头部信息：
        - OK-ACCESS-KEY: API密钥
        - OK-ACCESS-SIGN: 签名
        - OK-ACCESS-TIMESTAMP: 时间戳
        - OK-ACCESS-PASSPHRASE: 密码短语
        
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
        
        API端点: GET /api/v5/account/balance
        
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
            print(f"❌ API错误 (代码: {response.get('code')}): {response.get('msg', '未知错误')}")
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
            
            # 按余额从大到小排序（仅显示非零余额）
            non_zero_details = [d for d in details if float(d.get('cashBal', '0')) > 0]
            sorted_details = sorted(non_zero_details, 
                                 key=lambda x: float(x.get('cashBal', '0')), 
                                 reverse=True)
            
            if not sorted_details:
                print("   所有币种余额为0")
                continue
            
            for detail in sorted_details:
                ccy = detail.get('ccy', 'N/A')
                cash_bal = detail.get('cashBal', '0')
                available_bal = detail.get('availBal', '0')
                frozen_bal = detail.get('frozenBal', '0')
                
                print(f"   币种: {ccy}")
                print(f"   ├─ 总余额: {cash_bal}")
                print(f"   ├─ 可用余额: {available_bal}")
                print(f"   └─ 冻结余额: {frozen_bal}")
                print("   " + "-" * 30)


def load_credentials():
    """
    从环境变量加载API凭据
    
    环境变量名称：
    - OKX_API_KEY: API密钥
    - OKX_SECRET_KEY: 秘钥
    - OKX_PASSPHRASE: 密码短语
    - OKX_SANDBOX: 是否使用沙盒环境 (true/false)
    
    Returns:
        tuple: (api_key, secret_key, passphrase, is_sandbox)
    """
    api_key = os.getenv('OKX_API_KEY')
    secret_key = os.getenv('OKX_SECRET_KEY')
    passphrase = os.getenv('OKX_PASSPHRASE')
    is_sandbox = os.getenv('OKX_SANDBOX', 'false').lower() == 'true'
    
    return api_key, secret_key, passphrase, is_sandbox


def main():
    """
    主函数：演示如何使用OKX API查询账户余额
    """
    print("🚀 OKX API v5 账户余额查询示例 (安全版本)")
    print("=" * 60)
    
    # 从环境变量加载凭据
    api_key, secret_key, passphrase, is_sandbox = load_credentials()
    
    # 检查凭据是否完整
    if not all([api_key, secret_key, passphrase]):
        print("❌ 缺少必要的环境变量！")
        print("\n📝 请设置以下环境变量：")
        print("export OKX_API_KEY='your_api_key'")
        print("export OKX_SECRET_KEY='your_secret_key'")
        print("export OKX_PASSPHRASE='your_passphrase'")
        print("export OKX_SANDBOX='false'  # 可选，默认false")
        print("\n💡 在Linux/Mac上，您可以创建一个.env文件：")
        print("OKX_API_KEY=your_api_key")
        print("OKX_SECRET_KEY=your_secret_key")
        print("OKX_PASSPHRASE=your_passphrase")
        print("OKX_SANDBOX=false")
        print("\n然后使用: source .env")
        return
    
    print(f"🔧 环境: {'沙盒' if is_sandbox else '生产'}")
    
    # 创建API客户端
    client = OKXAPIClient(
        api_key=api_key,
        secret_key=secret_key,
        passphrase=passphrase,
        is_sandbox=is_sandbox
    )
    
    print("📡 正在查询账户总余额...")
    # 查询所有币种余额
    response = client.get_account_balance()
    client.format_balance_response(response)
    
    # 可选：查询特定币种
    target_currency = input("\n🔍 输入要查询的特定币种(如BTC)，或按回车跳过: ").strip().upper()
    if target_currency:
        print(f"\n📡 正在查询{target_currency}余额...")
        specific_response = client.get_account_balance(target_currency)
        client.format_balance_response(specific_response)
    
    print("\n✅ 查询完成！")
    print("\n📖 更多API文档: https://www.okx.com/docs-v5/zh/")


if __name__ == "__main__":
    main()