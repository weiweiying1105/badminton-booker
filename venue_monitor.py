import requests
import time
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import schedule

class SHSportsVenueMonitor:
    def __init__(self, config_file: str = 'config.json'):
        self.config = self.load_config(config_file)
        self.setup_logging()
        self.session = requests.Session()
        self.setup_headers()
        
    def load_config(self, config_file: str) -> Dict:
        """加载配置文件"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logging.error(f"配置文件 {config_file} 不存在")
            return {}
    
    def setup_logging(self):
        """设置日志"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('venue_monitor.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def setup_headers(self):
        """设置请求头，模拟小程序请求"""
        default_headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.29(0x18001d2f) NetType/WIFI Language/zh_CN',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Referer': self.config.get('referer', ''),
        }
        
        # 合并配置中的headers
        if 'headers' in self.config:
            default_headers.update(self.config['headers'])
            
        self.session.headers.update(default_headers)
    
    def refresh_access_token(self) -> bool:
        """刷新access_token"""
        try:
            token_url = "https://map.shsports.cn/api/oauth/token"
            params = {
                "client_id": "30d3b25db72041879c180593ebf9d0c6",
                "grant_type": "wxmp_code",
                "client_secret": "20ec787ba2ce4832aa4f3a9b08d4abbb",
                "code": "0c3TA4100VwsQU1T8p000ql52d1TA41A"
            }
            
            self.logger.info("正在刷新access_token...")
            response = requests.get(token_url, params=params, timeout=10, verify=False)
            response.raise_for_status()
            
            token_data = response.json()
            
            if 'access_token' in token_data:
                new_token = token_data['access_token']
                self.logger.info(f"获取到新的access_token: {new_token[:20]}...")
                
                # 更新session headers中的Authorization
                self.session.headers['Authorization'] = f"Bearer {new_token}"
                
                # 更新config中的token（可选，用于下次启动）
                if 'headers' not in self.config:
                    self.config['headers'] = {}
                self.config['headers']['Authorization'] = f"Bearer {new_token}"
                
                return True
            else:
                self.logger.error(f"token响应中没有access_token: {token_data}")
                return False
                
        except Exception as e:
            self.logger.error(f"刷新access_token失败: {e}")
            return False
    
    def make_authenticated_request(self, method: str, url: str, **kwargs) -> Optional[Dict]:
        """带token刷新的请求方法"""
        max_retries = 2
        
        for attempt in range(max_retries):
            try:
                if method.upper() == 'GET':
                    response = self.session.get(url, verify=False, **kwargs)
                elif method.upper() == 'POST':
                    response = self.session.post(url, verify=False, **kwargs)
                else:
                    raise ValueError(f"不支持的HTTP方法: {method}")
                
                response.raise_for_status()
                return response.json()
                
            except requests.RequestException as e:
                self.logger.warning(f"请求失败 (尝试 {attempt + 1}/{max_retries}): {e}")
                
                # 如果是认证相关错误，尝试刷新token
                if attempt < max_retries - 1 and (response.status_code in [401, 403] if 'response' in locals() else True):
                    self.logger.info("尝试刷新token后重试...")
                    if self.refresh_access_token():
                        continue
                
                if attempt == max_retries - 1:
                    self.logger.error(f"请求最终失败: {e}")
                    return None
            except json.JSONDecodeError as e:
                self.logger.error(f"解析响应JSON失败: {e}")
                return None
        
        return None
    
    def check_bookable_status(self, venue_id: str, date: str) -> Dict:
        """第一步：检查场馆是否开放预定"""
        try:
            url = f"https://map.shsports.cn/order/v3/map/stadiumItem/bookable/{venue_id}/{date}"
            self.logger.info(f"检查预定开放状态: {url}")
            
            data = self.make_authenticated_request('GET', url, timeout=10)
            if data:
                self.logger.info(f"预定开放状态: {data}")
                return data
            else:
                return {}
                
        except Exception as e:
            self.logger.error(f"检查预定开放状态异常: {e}")
            return {}
    
    def get_venue_resources(self, venue_id: str, date: str) -> Dict:
        """第二步：获取场馆具体时段信息"""
        try:
            url = f"https://map.shsports.cn/api/stadium/resources/{venue_id}/matrix"
            params = {
                'stadiumItemId': venue_id,
                'date': date
            }
            
            # self.logger.info(f"获取场馆资源信息: {url} - 参数: {params}")
            
            data = self.make_authenticated_request('GET', url, params=params, timeout=10)
            if data:
                self.logger.debug(f"场馆资源响应: {json.dumps(data, ensure_ascii=False, indent=2)[:1000]}")
                return data
            else:
                return {}
                
        except Exception as e:
            self.logger.error(f"获取场馆资源信息异常: {e}")
            return {}
    
    def minutes_to_time_string(self, minutes: int) -> str:
        """将分钟数转换为时间字符串"""
        hours = minutes // 60
        mins = minutes % 60
        return f"{hours:02d}:{mins:02d}"
    
    def parse_available_slots(self, resources_data: Dict) -> List[Dict]:
        """解析可用时段，只返回8:00-22:00时间段的场地"""
        available_slots = []
        
        try:
            if 'data' not in resources_data:
                self.logger.warning("响应中没有找到data字段")
                return available_slots
            
            fields_data = resources_data['data']
            
            for field in fields_data:
                field_id = field.get('fieldId', '')
                field_name = field.get('fieldName', '未知场地')
                field_resources = field.get('fieldResource', [])
                
                self.logger.info(f"检查场地: {field_name} ({field_id})")
                
                for resource in field_resources:
                    status = resource.get('status', '')
                    
                    # 检查是否可预定（过滤掉ORDERED和LOCKED状态）
                    if status not in ['ORDERED', 'LOCKED']:
                        start_minutes = resource.get('start', 0)
                        end_minutes = resource.get('end', 0)
                        
                        # 添加时间范围过滤：只监控18:00之后的时段 (18:00 = 1080分钟)
                        if start_minutes < 1080:
                            continue  # 跳过18:00之前的时段
                        
                        price = resource.get('price', 0)
                        record_id = resource.get('recordId')
                        
                        start_time = self.minutes_to_time_string(start_minutes)
                        end_time = self.minutes_to_time_string(end_minutes)
                        time_slot = f"{start_time}-{end_time}"
                        
                        available_slot = {
                            'field_id': field_id,
                            'field_name': field_name,
                            'time': time_slot,
                            'start_minutes': start_minutes,
                            'end_minutes': end_minutes,
                            'price': price / 100,  # 价格从分转换为元
                            'status': status,
                            'record_id': record_id,
                            'raw_data': resource
                        }
                        
                        available_slots.append(available_slot)
                        self.logger.info(f"找到可用时段: {field_name} {time_slot} - 状态: {status} - 价格: ¥{price/100}")
                
        except Exception as e:
            self.logger.error(f"解析可用时段时出错: {e}")
            self.logger.debug(f"原始数据: {json.dumps(resources_data, ensure_ascii=False, indent=2)}")
        
        return available_slots
    
    def send_notification(self, message: str, available_slots: List[Dict], venue_name: str, date: str):
        """发送通知"""
        notification_methods = self.config.get('notifications', {})
        
        if notification_methods.get('email', {}).get('enabled', False):
            self.send_email_notification(message, available_slots, venue_name, date)
        
        if notification_methods.get('webhook', {}).get('enabled', False):
            self.send_webhook_notification(message, available_slots, venue_name, date)
    
    def send_email_notification(self, message: str, available_slots: List[Dict], venue_name: str, date: str):
        """发送邮件通知"""
        try:
            email_config = self.config['notifications']['email']
            
            msg = MIMEMultipart()
            msg['From'] = email_config['from_email']
            msg['To'] = email_config['to_email']
            msg['Subject'] = f"🏸 {venue_name} {date} 场馆预定提醒"
            
            # 构建邮件内容
            body = f"{message}\n\n📅 日期: {date}\n🏟️ 场馆: {venue_name}\n\n可用时段：\n"
            
            for slot in available_slots:
                body += f"🏸 {slot['field_name']} - {slot['time']} - ¥{slot['price']} - 状态: {slot['status']}\n"
            
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            # 发送邮件
            server = smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port'])
            server.starttls()
            server.login(email_config['from_email'], email_config['password'])
            server.send_message(msg)
            server.quit()
            
            self.logger.info("邮件通知发送成功")
            
        except Exception as e:
            self.logger.error(f"邮件发送失败: {e}")
    
    def send_webhook_notification(self, message: str, available_slots: List[Dict], venue_name: str, date: str):
        """发送Webhook通知（钉钉、企业微信等）"""
        try:
            webhook_config = self.config['notifications']['webhook']
            webhook_url = webhook_config['url']
            
            # 构建通知内容
            if available_slots:
                slots_text = "\n".join([
                    f"🏸🏸🏸🏸🏸🏸🏸 {slot['field_name']} - {slot['time']} - ¥{slot['price']} - {slot['status']}"
                    for slot in available_slots
                ])
                full_message = f"{message}\n\n📅 日期: {date}\n🏟️ 场馆: {venue_name}\n\n{slots_text}"
            else:
                # 处理各种无时段的情况（暂无时段、请求失败、未开放等）
                if "❌" in message:
                    # 错误情况
                    full_message = f"{message}\n\n📅 日期: {date}\n🏟️ 场馆: {venue_name}\n\n🔧 请检查网络连接或稍后重试"
                elif "⏳" in message:
                    # 未开放预定
                    full_message = f"{message}\n\n📅 日期: {date}\n🏟️ 场馆: {venue_name}\n\n🔄 将继续监控开放状态"
                else:
                    # 暂无可用时段
                    full_message = f"{message}\n\n📅 日期: {date}\n🏟️ 场馆: {venue_name}\n\n⏰ 监控时间段: 18:00之后\n🔄 将继续监控，有可用时段时会立即通知"
            
            # 钉钉机器人格式
            if 'dingtalk' in webhook_url or 'oapi.dingtalk.com' in webhook_url:
                payload = {
                    "msgtype": "text",
                    "text": {
                        "content": full_message
                    }
                }
            # 企业微信机器人格式
            elif 'qyapi.weixin.qq.com' in webhook_url:
                payload = {
                    "msgtype": "text",
                    "text": {
                        "content": full_message
                    }
                }
            else:
                # 通用格式
                payload = {
                    "message": message,
                    "venue_name": venue_name,
                    "date": date,
                    "available_slots": available_slots,
                    "text": full_message
                }
            
            # 添加SSL验证跳过，解决证书验证问题
            response = requests.post(webhook_url, json=payload, timeout=10, verify=False)
            response.raise_for_status()
            
            self.logger.info("Webhook通知发送成功")
            
        except Exception as e:
            self.logger.error(f"Webhook通知发送失败: {e}")
    
    def monitor_venue(self, venue_id: str, date: str, venue_name: str = ""):
        """监控单个场馆"""
        display_name = venue_name or venue_id
        self.logger.info(f"开始监控场馆 {display_name} 在 {date} 的预定情况")
        
        # 第一步：检查是否开放预定
        bookable_data = self.check_bookable_status(venue_id, date)
        if not bookable_data:
            self.logger.warning(f"无法获取场馆 {display_name} 的预定开放状态")
            return
        
        # 检查是否开放预定
        is_bookable = bookable_data.get('bookable', False)
        if not is_bookable:
            msg_code = bookable_data.get('msg', 'unknown')
            self.logger.info(f"场馆 {display_name} 在 {date} 尚未开放预定 (msg: {msg_code})")
            return
        
        self.logger.info(f"场馆 {display_name} 在 {date} 已开放预定，获取具体时段信息")
        
        # 第二步：获取具体时段信息
        resources_data = self.get_venue_resources(venue_id, date)
        if not resources_data:
            self.logger.warning(f"无法获取场馆 {display_name} 的资源信息")
            return
        
        # 检查API响应状态
        if resources_data.get('code') != 200:
            self.logger.warning(f"获取场馆资源失败: {resources_data.get('msg', 'unknown error')}")
            return
        
        # 解析可用时段
        available_slots = self.parse_available_slots(resources_data)
        
        if available_slots:
            message = f"🎉🎉🎉🎉🎉 {display_name} 在 {date} 有 {len(available_slots)} 个可用时段！"
            self.logger.info(message)
            self.send_notification(message, available_slots, display_name, date)
        # else:
            # 修改这里：暂无可用时段时也发送通知
            # message = f"😔 {display_name} 在 {date} 暂无可用时段"
            # self.logger.info(message)
            # 发送暂无时段的通知，传入空的available_slots列表
            # self.send_notification(message, [], display_name, date)
    
    def run_monitor(self):
        """运行监控任务"""
        venues = self.config.get('venues', [])
        
        if not venues:
            self.logger.error("配置文件中没有找到要监控的场馆")
            return
        
        for venue in venues:
            venue_id = venue['id']
            venue_name = venue.get('name', venue_id)
            dates = venue.get('dates', [datetime.now().strftime('%Y-%m-%d')])
            
            for date in dates:
                try:
                    self.monitor_venue(venue_id, date, venue_name)
                    time.sleep(2)  # 避免请求过于频繁
                except Exception as e:
                    self.logger.error(f"监控场馆 {venue_name} 时出错: {e}")
    
    def start_scheduled_monitoring(self):
        """启动定时监控"""
        interval = self.config.get('check_interval', 60)  # 默认60秒检查一次
        
        self.logger.info(f"启动上海体育场馆定时监控，检查间隔: {interval}秒")
        self.logger.info(f"监控的场馆数量: {len(self.config.get('venues', []))}")
        
        # 立即执行一次
        self.run_monitor()
        
        # 设置定时任务
        schedule.every(interval).seconds.do(self.run_monitor)
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            self.logger.info("监控已停止")

if __name__ == "__main__":
    monitor = SHSportsVenueMonitor()
    monitor.start_scheduled_monitoring()