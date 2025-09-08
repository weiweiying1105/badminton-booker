import pyautogui
import cv2
import numpy as np
from PIL import Image
import time
import pytesseract
import os
import psutil

# 设置Tesseract路径和数据目录
pytesseract.pytesseract.tesseract_cmd = r'D:\installs\Tesseract-OCR\tesseract.exe'
os.environ['TESSDATA_PREFIX'] = r'D:\installs\Tesseract-OCR\tessdata'

class WeChatAutomation:
    def __init__(self):
        # 设置安全延迟
        pyautogui.PAUSE = 1
        pyautogui.FAILSAFE = True
        
        # 滚动配置
        self.scroll_config = {
            'default_start_x': None,
            'default_start_y': None,
            'use_percentage': True,
            'x_percent': 50,  # 屏幕宽度的50%
            'y_percent': 30   # 屏幕高度的30%
        }
    
    def find_button_by_image(self, button_image_path):
        """通过图像识别找到按钮位置"""
        try:
            # 截取屏幕
            screenshot = pyautogui.screenshot()
            
            # 查找按钮
            button_location = pyautogui.locateOnScreen(button_image_path, confidence=0.8)
            
            if button_location:
                return pyautogui.center(button_location)
            return None
        except Exception as e:
            print(f"图像识别失败: {e}")
            return None
    
    def find_button_by_text(self, text="立即预定"):
        """通过OCR文字识别找到按钮"""
        try:
            # 截取屏幕
            screenshot = pyautogui.screenshot()
            
            # OCR识别文字
            text_data = pytesseract.image_to_data(screenshot, output_type=pytesseract.Output.DICT)
            
            for i, detected_text in enumerate(text_data['text']):
                if text in detected_text:
                    x = text_data['left'][i]
                    y = text_data['top'][i]
                    w = text_data['width'][i]
                    h = text_data['height'][i]
                    return (x + w//2, y + h//2)
            
            return None
        except Exception as e:
            print(f"OCR识别失败: {e}")
            return None
    
    def find_button_by_text_with_color_check(self, button_texts):
        """通过文字识别按钮，并检查按钮是否可用"""
        try:
            screenshot = pyautogui.screenshot()
            screenshot_np = np.array(screenshot)
            
            # OCR识别文字
            data = pytesseract.image_to_data(screenshot, output_type=pytesseract.Output.DICT, lang='chi_sim')
            
            for i, text in enumerate(data['text']):
                if any(btn_text in text for btn_text in button_texts):
                    x = data['left'][i]
                    y = data['top'][i]
                    w = data['width'][i]
                    h = data['height'][i]
                    
                    # 获取按钮区域的颜色信息
                    button_region = screenshot_np[y:y+h, x:x+w]
                    
                    # 检查是否为蓝色按钮（可用状态）
                    if self.is_button_active(button_region):
                        center_x = x + w // 2
                        center_y = y + h // 2
                        print(f"找到可用按钮: {text} 位置: ({center_x}, {center_y})")
                        return (center_x, center_y)
                    else:
                        print(f"跳过禁用按钮: {text}")
            
            return None
            
        except Exception as e:
            print(f"OCR识别失败: {e}")
            return None
    
    def is_button_active(self, button_region):
        """检查按钮区域是否为可用状态（蓝色）"""
        try:
            # 转换为HSV
            hsv = cv2.cvtColor(button_region, cv2.COLOR_RGB2HSV)
            
            # 蓝色范围
            lower_blue = np.array([100, 50, 50])
            upper_blue = np.array([130, 255, 255])
            
            # 检查蓝色像素比例
            blue_mask = cv2.inRange(hsv, lower_blue, upper_blue)
            blue_ratio = np.sum(blue_mask > 0) / blue_mask.size
            
            # 如果蓝色像素超过30%，认为是可用按钮
            return blue_ratio > 0.3
            
        except Exception as e:
            print(f"按钮状态检查失败: {e}")
            return False
    
    def find_button_by_text(self, text="立即预定"):
        """通过OCR文字识别找到按钮"""
        try:
            # 截取屏幕
            screenshot = pyautogui.screenshot()
            
            # OCR识别文字
            text_data = pytesseract.image_to_data(screenshot, output_type=pytesseract.Output.DICT)
            
            for i, detected_text in enumerate(text_data['text']):
                if text in detected_text:
                    x = text_data['left'][i]
                    y = text_data['top'][i]
                    w = text_data['width'][i]
                    h = text_data['height'][i]
                    return (x + w//2, y + h//2)
            
            return None
        except Exception as e:
            print(f"OCR识别失败: {e}")
            return None
    
    def find_button_by_text(self, text="立即预定"):
        """通过OCR文字识别找到按钮"""
        try:
            # 截取屏幕
            screenshot = pyautogui.screenshot()
            
            # OCR识别文字
            text_data = pytesseract.image_to_data(screenshot, output_type=pytesseract.Output.DICT)
            
            for i, detected_text in enumerate(text_data['text']):
                if text in detected_text:
                    x = text_data['left'][i]
                    y = text_data['top'][i]
                    w = text_data['width'][i]
                    h = text_data['height'][i]
                    return (x + w//2, y + h//2)
            
            return None
        except Exception as e:
            print(f"OCR识别失败: {e}")
            return None
    
    def find_active_button(self):
        """查找可用的（蓝色）按钮"""
        try:
            # 截取屏幕
            screenshot = pyautogui.screenshot()
            screenshot_np = np.array(screenshot)
            screenshot_bgr = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
            
            # 定义蓝色按钮的HSV范围
            hsv = cv2.cvtColor(screenshot_bgr, cv2.COLOR_BGR2HSV)
            
            # 蓝色范围 (可能需要根据实际情况调整)
            lower_blue = np.array([100, 50, 50])
            upper_blue = np.array([130, 255, 255])
            
            # 创建蓝色掩码
            blue_mask = cv2.inRange(hsv, lower_blue, upper_blue)
            
            # 查找轮廓
            contours, _ = cv2.findContours(blue_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # 查找最大的蓝色区域（可能是按钮）
            if contours:
                largest_contour = max(contours, key=cv2.contourArea)
                
                # 获取边界框
                x, y, w, h = cv2.boundingRect(largest_contour)
                
                # 计算中心点
                center_x = x + w // 2
                center_y = y + h // 2
                
                # 检查区域大小是否合理（避免误识别小的蓝色点）
                if w > 50 and h > 20:  # 按钮最小尺寸
                    print(f"找到蓝色按钮位置: ({center_x}, {center_y}), 尺寸: {w}x{h}")
                    return (center_x, center_y)
            
            print("未找到蓝色按钮")
            return None
            
        except Exception as e:
            print(f"颜色识别失败: {e}")
            return None
    
    def scroll_page_simple(self):
        """使用滚轮进行简单的页面滑动"""
        try:
            print("执行页面滑动操作...")
            
            # 向下滚动（相当于向下滑动300像素）
            pyautogui.scroll(-20)  # 负数向下滚动
            time.sleep(1)
            
            # 获取当前鼠标位置
            current_x, current_y = pyautogui.position()
            
            # 向左移动鼠标（模拟向左滑动）
            pyautogui.moveTo(current_x - 500, current_y, duration=1)
            
            print("✅ 页面滑动完成")
            
        except Exception as e:
            print(f"❌ 页面滑动失败: {e}")
    
    def click_booking_button(self):
        """点击立即预定按钮"""
        button_found = False
        button_position = None
        
        try:
            print("🔍 开始查找立即预定按钮...")
            
            # 1. 优先使用精确颜色匹配
            button_position = self.find_booking_button_by_exact_color()
            if button_position:
                button_found = True
                print("✅ 使用精确颜色识别成功")
            
            # 2. 备用方案：HSV颜色范围
            if not button_found:
                button_position = self.find_booking_button_by_hsv_range()
                if button_position:
                    button_found = True
                    print("✅ 使用HSV范围识别成功")
            
            # 3. 备用方案：文字识别
            if not button_found:
                button_position = self.find_button_by_text("立即预定")
                if button_position:
                    button_found = True
                    print("✅ 使用文字识别成功")
            
            # 4. 最后备用方案：图像匹配
            if not button_found:
                button_position = self.find_button_by_image("booking_button.png")
                if button_position:
                    button_found = True
                    print("✅ 使用图像匹配成功")
            
            if button_found and button_position:
                print(f"📍 按钮位置: {button_position}")
                pyautogui.click(button_position[0], button_position[1])
                print("✅ 按钮点击成功")
                time.sleep(2)
                
                # 点击成功后执行触控板滑动
                print("🎯 开始执行触控板滑动操作")
                self.swipe_up_and_left()
                
                return True
            else:
                print("❌ 未找到立即预定按钮")
                return False
                
        except Exception as e:
            print(f"❌ 点击按钮操作失败: {e}")
            return False
    
    def wait_for_wechat_window(self):
        """等待微信窗口激活"""
        # 查找微信进程
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if 'WeChat' in proc.info['name'] or '微信' in proc.info['name']:
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return False
    
    def verify_page_change(self):
        """验证页面是否发生变化"""
        try:
            # 等待页面加载
            time.sleep(2)
            
            # 截取当前屏幕
            screenshot = pyautogui.screenshot()
            
            # 检查是否出现了新的页面元素（比如预订表单）
            # 可以通过OCR查找特定文字来判断
            text = pytesseract.image_to_string(screenshot, lang='chi_sim')
            
            # 检查是否包含预订相关的文字
            success_keywords = ['预订', '选择时间', '确认', '提交', '场地']
            for keyword in success_keywords:
                if keyword in text:
                    print(f"页面跳转成功，检测到关键词: {keyword}")
                    return True
            
            print("页面可能未跳转，未检测到预期的关键词")
            return False
            
        except Exception as e:
            print(f"页面验证失败: {e}")
            return False
    
    def run_automation(self):
        """运行自动化流程"""
        input("请手动打开微信小程序到预订页面，然后按回车继续...")
        
        # 尝试点击预订按钮（只执行一次，点击成功后就退出）
        if self.click_booking_button():
            print("✅ 预订按钮点击成功，流程完成")
            return True
        else:
            print("❌ 未能找到或点击预订按钮")
            return False

# 主程序入口
if __name__ == "__main__":
    automation = WeChatAutomation()
    
    if automation.wait_for_wechat_window():
        print("检测到微信窗口")
        
        # 运行自动化流程
        success = automation.run_automation()
        
        if success:
            print("🎉 自动化流程执行成功！")
        else:
            print("⚠️ 自动化流程执行失败")
    else:
        print("未检测到微信窗口")

    def scroll_from_screen_percentage(self, x_percent=50, y_percent=50, direction="down", distance=800):
        """从屏幕百分比位置开始滚动"""
        try:
            # 获取屏幕尺寸
            screen_width, screen_height = pyautogui.size()
            
            # 计算实际坐标
            start_x = int(screen_width * x_percent / 100)
            start_y = int(screen_height * y_percent / 100)
            
            print(f"屏幕尺寸: {screen_width}x{screen_height}")
            print(f"从屏幕 {x_percent}%,{y_percent}% 位置 ({start_x}, {start_y}) 开始滚动")
            
            # 调用固定位置滚动方法
            self.scroll_from_position(start_x, start_y, direction, distance)
            
        except Exception as e:
            print(f"❌ 百分比滚动失败: {e}")
    
    def scroll_from_position(self, start_x, start_y, direction="down", distance=300):
        """从指定位置开始滚动"""
        try:
            print(f"从位置 ({start_x}, {start_y}) 开始滚动")
            
            # 移动鼠标到指定起始位置
            pyautogui.moveTo(start_x, start_y, duration=0.5)
            time.sleep(0.2)
            
            if direction == "down":
                end_y = start_y + distance
                pyautogui.drag(start_x, start_y, start_x, end_y, duration=1.5)
            elif direction == "up":
                end_y = start_y - distance
                pyautogui.drag(start_x, start_y, start_x, end_y, duration=1.5)
            elif direction == "left":
                end_x = start_x - distance
                pyautogui.drag(start_x, start_y, end_x, start_y, duration=1.5)
            elif direction == "right":
                end_x = start_x + distance
                pyautogui.drag(start_x, start_y, end_x, start_y, duration=1.5)
            
            print(f"✅ 滚动完成")
            
        except Exception as e:
            print(f"❌ 滚动操作失败: {e}")


    def get_safe_scroll_position(self):
        """获取安全的滚动起始位置"""
        screen_width, screen_height = pyautogui.size()
        
        # 避开屏幕边缘，选择中心偏上的位置
        safe_x = screen_width // 2
        safe_y = screen_height // 3  # 屏幕上1/3处
        
        return safe_x, safe_y
    
    def smart_scroll_page(self, direction="down", distance=300):
        """智能选择滚动起始位置"""
        try:
            # 获取安全的滚动位置
            start_x, start_y = self.get_safe_scroll_position()
            
            print(f"智能选择滚动起始位置: ({start_x}, {start_y})")
            
            # 执行滚动
            self.scroll_from_position(start_x, start_y, direction, distance)
            
        except Exception as e:
            print(f"❌ 智能滚动失败: {e}")


    def get_configured_scroll_position(self):
        """获取配置的滚动位置"""
        if self.scroll_config['use_percentage']:
            screen_width, screen_height = pyautogui.size()
            x = int(screen_width * self.scroll_config['x_percent'] / 100)
            y = int(screen_height * self.scroll_config['y_percent'] / 100)
        else:
            x = self.scroll_config['default_start_x'] or pyautogui.size()[0] // 2
            y = self.scroll_config['default_start_y'] or pyautogui.size()[1] // 3
        
        return x, y
    
    def scroll_page_down_and_left(self, start_x=None, start_y=None):
        """页面向下滑动800像素，向左滑动500像素"""
        try:
            # 如果没有指定起始位置，使用配置的位置
            if start_x is None or start_y is None:
                start_x, start_y = self.get_configured_scroll_position()
            
            print(f"滑动起始位置: ({start_x}, {start_y})")
            
            # 移动到起始位置
            pyautogui.moveTo(start_x, start_y, duration=0.5)
            time.sleep(0.2)
            
            # 1. 向下滑动800像素
            print("执行向下滑动800像素...")
            end_y = start_y + 800
            pyautogui.drag(start_x, start_y, start_x, end_y, duration=1.5)
            time.sleep(1)
            
            # 2. 从新位置向左滑动500像素
            print("执行向左滑动500像素...")
            print(f"向左滑动起始触点: ({start_x}, {end_y})")
            end_x = start_x - 500
            pyautogui.drag(start_x, end_y, end_x, end_y, duration=1.5)
            time.sleep(1)
            
            print(f"✅ 滑动完成，最终位置: ({end_x}, {end_y})")
            
        except Exception as e:
            print(f"❌ 页面滑动操作失败: {e}")


    def simulate_touchpad_swipe(self, direction="up", distance=800, start_x=None, start_y=None):
        """模拟触控板滑动手势"""
        try:
            # 获取屏幕尺寸
            screen_width, screen_height = pyautogui.size()
            
            # 设置默认起始位置（屏幕中心）
            if start_x is None:
                start_x = screen_width // 2
            if start_y is None:
                start_y = screen_height // 2
                
            print(f"开始触控板滑动: 方向={direction}, 距离={distance}像素")
            print(f"起始位置: ({start_x}, {start_y})")
            
            # 移动到起始位置
            pyautogui.moveTo(start_x, start_y, duration=0.2)
            time.sleep(0.1)
            
            # 按下鼠标左键开始拖拽
            pyautogui.mouseDown()
            time.sleep(0.1)
            
            # 根据方向计算终点位置
            if direction == "up":
                end_x, end_y = start_x, start_y - distance
            elif direction == "down":
                end_x, end_y = start_x, start_y + distance
            elif direction == "left":
                end_x, end_y = start_x - distance, start_y
            elif direction == "right":
                end_x, end_y = start_x + distance, start_y
            else:
                raise ValueError(f"不支持的滑动方向: {direction}")
                
            # 执行滑动动作（模拟触控板手势）
            pyautogui.moveTo(end_x, end_y, duration=1.0)
            time.sleep(0.1)
            
            # 释放鼠标
            pyautogui.mouseUp()
            time.sleep(0.5)
            
            print(f"✅ 触控板滑动完成: 从({start_x}, {start_y})到({end_x}, {end_y})")
            
        except Exception as e:
            print(f"❌ 触控板滑动失败: {e}")
            # 确保鼠标释放
            try:
                pyautogui.mouseUp()
            except:
                pass
    
    def swipe_up_and_left(self, up_distance=800, left_distance=500):
        """向上滑动后向左滑动"""
        try:
            print("执行组合滑动: 向上 + 向左")
            
            # 获取屏幕中心位置
            screen_width, screen_height = pyautogui.size()
            center_x = screen_width // 2
            center_y = screen_height // 2
            
            # 1. 先向上滑动
            print(f"第1步: 向上滑动 {up_distance} 像素")
            self.simulate_touchpad_swipe("up", up_distance, center_x, center_y)
            time.sleep(1)  # 等待页面响应
            
            # 2. 再向左滑动
            print(f"第2步: 向左滑动 {left_distance} 像素")
            self.simulate_touchpad_swipe("left", left_distance, center_x, center_y)
            time.sleep(1)  # 等待页面响应
            
            print("✅ 组合滑动操作完成")
        except Exception as e:
            print(f"❌ 组合滑动操作失败: {e}")


    def find_booking_button_by_exact_color(self):
        """根据精确的颜色值查找立即预定按钮"""
        try:
            # 截取当前屏幕
            screenshot = pyautogui.screenshot()
            screenshot_np = np.array(screenshot)
            
            # 目标颜色 #1aabff 转换为 RGB
            target_color = np.array([26, 171, 255])  # #1aabff
            
            # 创建颜色容差范围（允许一定的颜色偏差）
            tolerance = 20
            lower_bound = np.maximum(target_color - tolerance, 0)
            upper_bound = np.minimum(target_color + tolerance, 255)
            
            # 创建颜色掩码
            mask = cv2.inRange(screenshot_np, lower_bound, upper_bound)
            
            # 查找轮廓
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if contours:
                # 按面积排序，选择最大的轮廓
                largest_contour = max(contours, key=cv2.contourArea)
                
                # 计算轮廓的边界框
                x, y, w, h = cv2.boundingRect(largest_contour)
                
                # 过滤太小的区域（可能是噪点）
                if w > 50 and h > 20:  # 按钮最小尺寸
                    center_x = x + w // 2
                    center_y = y + h // 2
                    print(f"✅ 通过精确颜色找到按钮: ({center_x}, {center_y})")
                    return (center_x, center_y)
            
            print("❌ 未找到匹配精确颜色的按钮")
            return None
            
        except Exception as e:
            print(f"❌ 精确颜色识别失败: {e}")
            return None
    
    def find_booking_button_by_hsv_range(self):
        """使用HSV颜色空间查找按钮（作为备用方案）"""
        try:
            screenshot = pyautogui.screenshot()
            screenshot_np = np.array(screenshot)
            hsv = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2HSV)
            
            # #1aabff 对应的HSV范围
            # H: 蓝色色调范围
            # S: 高饱和度
            # V: 中高亮度
            lower_hsv = np.array([200, 180, 200])  # 调整后的HSV下限
            upper_hsv = np.array([220, 255, 255])  # 调整后的HSV上限
            
            mask = cv2.inRange(hsv, lower_hsv, upper_hsv)
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if contours:
                largest_contour = max(contours, key=cv2.contourArea)
                x, y, w, h = cv2.boundingRect(largest_contour)
                
                if w > 50 and h > 20:
                    center_x = x + w // 2
                    center_y = y + h // 2
                    print(f"✅ 通过HSV范围找到按钮: ({center_x}, {center_y})")
                    return (center_x, center_y)
            
            return None
            
        except Exception as e:
            print(f"❌ HSV颜色识别失败: {e}")
            return None