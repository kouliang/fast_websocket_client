#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OKX API v5 签名算法测试
验证签名生成是否符合官方文档要求
"""

import hmac
import hashlib
import base64
from datetime import datetime


def generate_signature(timestamp, method, request_path, body, secret_key):
    """
    根据OKX文档生成签名
    
    Args:
        timestamp (str): 时间戳
        method (str): HTTP方法
        request_path (str): 请求路径  
        body (str): 请求体
        secret_key (str): 秘钥
    
    Returns:
        str: Base64编码的签名
    """
    # 创建prehash字符串: timestamp + method + requestPath + body
    prehash = timestamp + method.upper() + request_path + body
    print(f"📝 Pre-hash 字符串: '{prehash}'")
    
    # 使用HMAC SHA256和SecretKey签名
    signature = hmac.new(
        secret_key.encode('utf-8'),
        prehash.encode('utf-8'), 
        hashlib.sha256
    ).digest()
    
    # Base64编码
    encoded_signature = base64.b64encode(signature).decode('utf-8')
    print(f"🔐 生成的签名: {encoded_signature}")
    
    return encoded_signature


def test_signature_with_official_example():
    """
    使用官方文档中的示例测试签名生成
    """
    print("🧪 测试签名算法（使用官方示例）")
    print("=" * 60)
    
    # 官方文档示例数据（需要根据实际文档调整）
    timestamp = "2020-12-08T09:08:57.715Z"
    method = "GET"
    request_path = "/api/v5/account/balance"
    body = ""
    secret_key = "22582BD0CFF14C41EDBF1AB98506286D"  # 示例秘钥
    
    print(f"⏰ 时间戳: {timestamp}")
    print(f"🔄 方法: {method}")
    print(f"📍 路径: {request_path}")
    print(f"📦 请求体: '{body}' (空字符串)")
    print(f"🔑 秘钥: {secret_key}")
    print()
    
    signature = generate_signature(timestamp, method, request_path, body, secret_key)
    
    # 这里应该与官方文档的期望值进行比较
    # expected_signature = "official_expected_signature_here"
    # if signature == expected_signature:
    #     print("✅ 签名验证成功！")
    # else:
    #     print("❌ 签名验证失败！")
    #     print(f"期望: {expected_signature}")
    #     print(f"实际: {signature}")
    
    print("\n📋 生成的请求头示例:")
    print(f"OK-ACCESS-KEY: your_api_key")
    print(f"OK-ACCESS-SIGN: {signature}")
    print(f"OK-ACCESS-TIMESTAMP: {timestamp}")
    print(f"OK-ACCESS-PASSPHRASE: your_passphrase")


def test_current_timestamp():
    """
    测试使用当前时间戳的签名生成
    """
    print("\n🕐 测试当前时间戳签名")
    print("=" * 60)
    
    # 生成当前时间戳
    current_timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
    
    method = "GET"
    request_path = "/api/v5/account/balance"
    body = ""
    secret_key = "YOUR_SECRET_KEY"  # 占位符
    
    print(f"⏰ 当前时间戳: {current_timestamp}")
    print(f"🔄 方法: {method}")
    print(f"📍 路径: {request_path}")
    print(f"📦 请求体: '{body}' (空字符串)")
    print()
    
    if secret_key == "YOUR_SECRET_KEY":
        print("⚠️  请将 secret_key 替换为您的真实秘钥以测试实际签名")
        return
    
    signature = generate_signature(current_timestamp, method, request_path, body, secret_key)
    
    print(f"\n📋 完整的请求头:")
    print(f"OK-ACCESS-KEY: YOUR_API_KEY")
    print(f"OK-ACCESS-SIGN: {signature}")
    print(f"OK-ACCESS-TIMESTAMP: {current_timestamp}")
    print(f"OK-ACCESS-PASSPHRASE: YOUR_PASSPHRASE")


def test_with_query_parameters():
    """
    测试带查询参数的签名生成
    """
    print("\n🔍 测试带查询参数的签名")
    print("=" * 60)
    
    timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'
    method = "GET"
    request_path = "/api/v5/account/balance?ccy=BTC"  # 带参数
    body = ""
    secret_key = "22582BD0CFF14C41EDBF1AB98506286D"  # 示例秘钥
    
    print(f"⏰ 时间戳: {timestamp}")
    print(f"🔄 方法: {method}")
    print(f"📍 路径（含参数）: {request_path}")
    print(f"📦 请求体: '{body}' (空字符串)")
    print()
    
    signature = generate_signature(timestamp, method, request_path, body, secret_key)
    
    print(f"\n💡 注意: 查询参数包含在 requestPath 中，而不是 body 中")


def main():
    """
    主函数：运行所有签名测试
    """
    print("🚀 OKX API v5 签名算法测试")
    print("根据官方文档: https://www.okx.com/docs-v5/zh/#overview-rest-authentication")
    print("=" * 80)
    
    # 测试1：使用官方示例
    test_signature_with_official_example()
    
    # 测试2：当前时间戳
    test_current_timestamp()
    
    # 测试3：带查询参数
    test_with_query_parameters()
    
    print("\n" + "=" * 80)
    print("✅ 签名测试完成！")
    print("\n📖 签名算法说明:")
    print("1. 按顺序拼接: timestamp + method + requestPath + body")
    print("2. 使用 HMAC SHA256 和 SecretKey 进行签名")  
    print("3. 将签名结果进行 Base64 编码")
    print("4. 将编码后的签名放入 OK-ACCESS-SIGN 请求头")
    
    print("\n⚠️  重要提醒:")
    print("- GET 请求的 body 为空字符串")
    print("- 查询参数包含在 requestPath 中")
    print("- 时间戳格式为 ISO 8601，精确到毫秒")
    print("- 方法名必须大写（GET, POST, etc.）")


if __name__ == "__main__":
    main()