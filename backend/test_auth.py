import requests
import hashlib
from datetime import datetime

# 模拟配置中的 ROLE_ADMIN (建议从 .env 读取，此处为示例)
ROLE_ADMIN = '9a2722e6-023f-472b-95a8-304a22ba43e4'

def test_permission():
    # 获取当前时间
    current_time = datetime.now().strftime('%Y%m%d%H%M')
    print(f"Current time: {current_time}")
    
    # 计算预期哈希
    data_to_hash = ROLE_ADMIN + current_time
    expected_hash = hashlib.sha1(data_to_hash.encode()).hexdigest()
    print(f"Expected hash: {expected_hash}")
    
    # 调用 API
    url = f'http://127.0.0.1:8000/api/v1/auth/check-permission?userrole={expected_hash}'
    print(f"Testing URL: {url}")
    
    try:
        r = requests.get(url)
        print(f"Response: {r.status_code} - {r.json()}")
    except Exception as e:
        print(f"Error calling API: {e}")

if __name__ == "__main__":
    test_permission()
