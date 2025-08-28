import requests
import json

def test_shsports_complete_flow():
    """测试上海体育完整API流程"""
    venue_id = "23ddcbea5edb11ec853f6c92bf4651ca"
    date = "2025-08-28"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.29(0x18001d2f) NetType/WIFI Language/zh_CN',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9',
    }
    
    # 第一步：检查是否开放预定
    print("=== 第一步：检查预定开放状态 ===")
    bookable_url = f"https://map.shsports.cn/order/v3/map/stadiumItem/bookable/{venue_id}/{date}"
    print(f"请求URL: {bookable_url}")
    
    try:
        response = requests.get(bookable_url, headers=headers, timeout=10)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            bookable_data = response.json()
            print(f"预定开放状态: {json.dumps(bookable_data, ensure_ascii=False, indent=2)}")
            
            # 检查是否可预定
            if bookable_data.get('bookable', False):
                print("✅ 场馆已开放预定，继续获取时段信息")
                
                # 第二步：获取具体时段信息
                print("\n=== 第二步：获取场馆时段信息 ===")
                resources_url = f"https://map.shsports.cn/api/stadium/resources/{venue_id}/matrix"
                params = {
                    'stadiumItemId': venue_id,
                    'date': date
                }
                print(f"请求URL: {resources_url}")
                print(f"参数: {params}")
                
                response2 = requests.get(resources_url, params=params, headers=headers, timeout=10)
                print(f"状态码: {response2.status_code}")
                
                if response2.status_code == 200:
                    resources_data = response2.json()
                    print(f"场馆资源信息: {json.dumps(resources_data, ensure_ascii=False, indent=2)[:2000]}...")
                    
                    # 分析可用时段
                    if 'data' in resources_data:
                        available_count = 0
                        for field in resources_data['data']:
                            field_name = field.get('fieldName', '未知')
                            print(f"\n场地: {field_name}")
                            
                            for resource in field.get('fieldResource', []):
                                status = resource.get('status', '')
                                start = resource.get('start', 0)
                                end = resource.get('end', 0)
                                price = resource.get('price', 0)
                                
                                start_time = f"{start//60:02d}:{start%60:02d}"
                                end_time = f"{end//60:02d}:{end%60:02d}"
                                
                                if status != 'ORDERED':
                                    available_count += 1
                                    print(f"  ✅ {start_time}-{end_time} - ¥{price/100} - {status}")
                                else:
                                    print(f"  ❌ {start_time}-{end_time} - ¥{price/100} - {status}")
                        
                        print(f"\n总计可用时段: {available_count} 个")
                else:
                    print(f"获取场馆资源失败: {response2.text}")
            else:
                msg_code = bookable_data.get('msg', 'unknown')
                print(f"❌ 场馆尚未开放预定 (msg: {msg_code})")
        else:
            print(f"检查预定开放状态失败: {response.text}")
            
    except Exception as e:
        print(f"测试失败: {e}")

if __name__ == "__main__":
    test_shsports_complete_flow()