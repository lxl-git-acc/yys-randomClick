import pyautogui
import time
import random
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import threading

# 设置中文显示
pyautogui.FAILSAFE = True  # 启用故障安全功能，鼠标移动到左上角可停止程序

class RandomClicker:
    def __init__(self, root):
        self.root = root
        self.root.title("随机鼠标点击器")
        self.root.geometry("500x650")  # 增加窗口高度
        self.root.resizable(True, True)  # 允许窗口调整大小
        self.root.configure(bg="#f0f0f0")
        
        # 配置样式
        style = ttk.Style()
        style.configure("TLabel", font=("SimHei", 10), background="#f0f0f0")
        style.configure("TButton", font=("SimHei", 10, "bold"))
        style.configure("TEntry", font=("SimHei", 10))
        
        # 变量初始化
        self.is_running = False
        self.click_thread = None
        self.region_selected = False
        self.region = (0, 0, 0, 0)  # (x1, y1, x2, y2)
        
        # 创建主框架
        main_frame = ttk.Frame(root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 创建标题
        title_label = ttk.Label(main_frame, text="随机鼠标点击器V1.0.5", font=("SimHei", 16, "bold"))
        title_label.pack(pady=10)
        
        # 创建设置区域
        settings_frame = ttk.LabelFrame(main_frame, text="设置", padding="10")
        settings_frame.pack(fill=tk.X, pady=10)
        
        # 最小间隔设置
        ttk.Label(settings_frame, text="最小时间间隔(秒):").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.min_interval_var = tk.StringVar(value="1.0")
        ttk.Entry(settings_frame, textvariable=self.min_interval_var, width=10).grid(row=0, column=1, sticky=tk.W, pady=5)
        
        # 最大间隔设置
        ttk.Label(settings_frame, text="最大时间间隔(秒):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.max_interval_var = tk.StringVar(value="2.0")
        ttk.Entry(settings_frame, textvariable=self.max_interval_var, width=10).grid(row=1, column=1, sticky=tk.W, pady=5)
        
        # 点击次数设置
        ttk.Label(settings_frame, text="点击次数(-1为无限):").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.click_count_var = tk.StringVar(value="-1")
        ttk.Entry(settings_frame, textvariable=self.click_count_var, width=10).grid(row=2, column=1, sticky=tk.W, pady=5)
        
        # 点击方式设置
        ttk.Label(settings_frame, text="点击方式:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.click_type_var = tk.StringVar(value="左键")
        click_type_combo = ttk.Combobox(settings_frame, textvariable=self.click_type_var, values=["左键", "右键", "中键", "双击"], state="readonly", width=8)
        click_type_combo.grid(row=3, column=1, sticky=tk.W, pady=5)
        
        # 自定义次数后固定间隔设置
        ttk.Label(settings_frame, text="每点击次数(次):").grid(row=4, column=0, sticky=tk.W, pady=5)
        self.interval_count_var = tk.StringVar(value="3")
        ttk.Entry(settings_frame, textvariable=self.interval_count_var, width=5).grid(row=4, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(settings_frame, text="蘸豆时长(秒):").grid(row=4, column=2, sticky=tk.W, pady=5, padx=(20, 0))
        self.fixed_interval_var = tk.StringVar(value="20.0")
        ttk.Entry(settings_frame, textvariable=self.fixed_interval_var, width=10).grid(row=4, column=3, sticky=tk.W, pady=5)
        
        # 休息设置
        ttk.Label(settings_frame, text="每X轮后休息(轮):").grid(row=5, column=0, sticky=tk.W, pady=5)
        self.rest_interval_var = tk.StringVar(value="100")
        ttk.Entry(settings_frame, textvariable=self.rest_interval_var, width=5).grid(row=5, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(settings_frame, text="休息时长(秒):").grid(row=5, column=2, sticky=tk.W, pady=5, padx=(20, 0))
        self.rest_duration_var = tk.StringVar(value="300.0")
        ttk.Entry(settings_frame, textvariable=self.rest_duration_var, width=10).grid(row=5, column=3, sticky=tk.W, pady=5)
        
        # 为了避免控件被遮挡，将随机操作设置放在单独的一行
        ttk.Label(settings_frame, text="").grid(row=6, column=0)  # 添加空行分隔
        
        # 随机操作设置
        self.random_action_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(settings_frame, text="启用点击后随机操作", variable=self.random_action_var).grid(row=7, column=0, columnspan=4, sticky=tk.W, pady=5)
        
        # 区域选择按钮
        region_frame = ttk.LabelFrame(main_frame, text="点击区域", padding="10")
        region_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(region_frame, text="选择点击区域", command=self.select_region).pack(pady=10)
        self.region_label_var = tk.StringVar(value="未选择区域")
        ttk.Label(region_frame, textvariable=self.region_label_var).pack(pady=5)
        
        # 控制按钮
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=20, anchor=tk.CENTER)  # 居中对齐
        
        # 创建一个容器来居中按钮
        button_container = ttk.Frame(button_frame)
        button_container.pack()
        
        self.start_button = ttk.Button(button_container, text="开始点击", command=self.start_clicking, width=15)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(button_container, text="停止点击", command=self.stop_clicking, state=tk.DISABLED, width=15)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # 状态标签
        self.status_var = tk.StringVar(value="就绪")
        status_label = ttk.Label(main_frame, textvariable=self.status_var, font=("SimHei", 10, "italic"))
        status_label.pack(pady=5)
        
    def select_region(self):
        """选择点击区域"""
        # 创建一个半透明的全屏窗口用于选择区域
        self.region_window = tk.Toplevel(self.root)
        self.region_window.attributes("-alpha", 0.3)
        self.region_window.attributes("-fullscreen", True)
        self.region_window.configure(bg="black")
        self.region_window.attributes("-topmost", True)
        
        self.start_x = self.start_y = 0
        self.rect = None
        # 修改Canvas背景设置，确保它能正确捕获鼠标事件
        self.canvas = tk.Canvas(self.region_window, cursor="cross", bg="black", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # 确保窗口获得焦点
        self.region_window.focus_set()
        
        # 绑定鼠标事件
        self.canvas.bind("<Button-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)
        
        # 显示提示信息
        self.info_text = self.canvas.create_text(
            self.region_window.winfo_screenwidth() // 2,
            self.region_window.winfo_screenheight() // 2,
            text="按住鼠标左键并拖动选择点击区域\n松开鼠标完成选择",
            fill="white",
            font=("SimHei", 14)
        )
    
    def on_mouse_down(self, event):
        """鼠标按下事件"""
        self.start_x = event.x_root
        self.start_y = event.y_root
        if self.rect:
            self.canvas.delete(self.rect)
        self.canvas.delete(self.info_text)
    
    def on_mouse_drag(self, event):
        """鼠标拖动事件"""
        if self.rect:
            self.canvas.delete(self.rect)
        x1, y1 = min(self.start_x, event.x_root), min(self.start_y, event.y_root)
        x2, y2 = max(self.start_x, event.x_root), max(self.start_y, event.y_root)
        self.rect = self.canvas.create_rectangle(x1, y1, x2, y2, outline="white", width=2)
    
    def on_mouse_up(self, event):
        """鼠标释放事件"""
        end_x, end_y = event.x_root, event.y_root
        x1, y1 = min(self.start_x, end_x), min(self.start_y, end_y)
        x2, y2 = max(self.start_x, end_x), max(self.start_y, end_y)
        
        # 检查区域是否有效
        if x1 == x2 or y1 == y2:
            messagebox.showwarning("警告", "请选择有效的区域")
        else:
            self.region = (x1, y1, x2, y2)
            self.region_selected = True
            self.region_label_var.set(f"区域: X({x1}-{x2}), Y({y1}-{y2})")
        
        self.region_window.destroy()
    
    def start_clicking(self):
        """开始随机点击"""
        # 检查设置是否有效
        try:
            min_interval = float(self.min_interval_var.get())
            max_interval = float(self.max_interval_var.get())
            fixed_interval = float(self.fixed_interval_var.get())
            click_count = int(self.click_count_var.get())
            # 获取间隔次数参数
            interval_count = int(self.interval_count_var.get())
            if interval_count < 1:
                messagebox.showerror("参数错误", "点击次数必须大于0！")
                return
            
            # 获取休息设置参数
            rest_interval = int(self.rest_interval_var.get())
            rest_duration = float(self.rest_duration_var.get())
            if rest_interval < 1:
                messagebox.showerror("参数错误", "休息间隔轮数必须大于0！")
                return
            if rest_duration < 0:
                messagebox.showerror("参数错误", "休息时长不能为负数！")
                return
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数值")
            return
        
        # 检查时间间隔是否合理
        if min_interval < 0 or max_interval < 0 or min_interval > max_interval or fixed_interval < 0:
            messagebox.showerror("错误", "请输入有效的时间间隔")
            return
        
        # 检查是否选择了区域
        if not self.region_selected:
            messagebox.showerror("错误", "请先选择点击区域")
            return
        
        # 开始点击线程
        self.is_running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_var.set("运行中...")
        
        self.click_thread = threading.Thread(
            target=self.random_click, 
            args=(min_interval, max_interval, fixed_interval, click_count, interval_count, rest_interval, rest_duration)
        )
        self.click_thread.daemon = True
        self.click_thread.start()
    
    def stop_clicking(self):
        """停止随机点击"""
        self.is_running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.status_var.set("已停止")
    
    def random_click(self, min_interval, max_interval, fixed_interval, click_count, interval_count, rest_interval, rest_duration):
        """执行随机点击"""
        count = 0
        round_count = 0  # 记录完成的轮数
        
        while self.is_running and (click_count == -1 or count < click_count):
            # 生成随机位置
            x = random.randint(self.region[0], self.region[2])
            y = random.randint(self.region[1], self.region[3])
            
            # 生成随机时间间隔
            interval = random.uniform(min_interval, max_interval)
            
            # 移动鼠标并点击
            try:
                pyautogui.moveTo(x, y, duration=0.1)
                
                # 根据选择的点击方式执行点击
                click_type = self.click_type_var.get()
                if click_type == "左键":
                    pyautogui.click()
                elif click_type == "右键":
                    pyautogui.rightClick()
                elif click_type == "中键":
                    pyautogui.middleClick()
                elif click_type == "双击":
                    # 第一次点击
                    pyautogui.click()
                    # 生成0.3到0.5秒之间的随机间隔
                    double_click_interval = random.uniform(0.3, 0.5)
                    # 等待随机间隔后进行第二次点击
                    time.sleep(double_click_interval)
                    pyautogui.click()
                
                # 执行随机操作（如果启用）
                if self.random_action_var.get():
                    # 随机选择操作类型（字母按键或滚轮滚动）
                    action_type = random.choice(['keyboard', 'scroll'])
                    
                    if action_type == 'keyboard':
                        # 随机选择一个字母
                        letter = random.choice('abcdefghijklmnopqrstuvwxyz')
                        # 按下并释放字母键
                        pyautogui.press(letter)
                    elif action_type == 'scroll':
                        # 随机选择滚动方向和幅度
                        scroll_amount = random.randint(-10, 10)  # 负数表示向上滚动，正数表示向下滚动
                        pyautogui.scroll(scroll_amount)
                
                count += 1
                self.status_var.set(f"已点击 {count} 次")
                
                # 再等待随机时间间隔
                wait_time = 0
                while wait_time < interval and self.is_running:
                    time.sleep(0.1)
                    wait_time += 0.1
                
                # 每执行指定次数点击后，等待固定时间间隔
                if fixed_interval > 0 and (count % interval_count == 0):
                    wait_time = 0
                    while wait_time < fixed_interval and self.is_running:
                        time.sleep(0.1)
                        wait_time += 0.1
                         
                    # 检查是否在固定等待期间被停止
                    if not self.is_running:
                        break
                        
                    # 更新轮数计数
                    round_count += 1
                    
                    # 检查是否需要休息
                    if rest_duration > 0 and (round_count % rest_interval == 0):
                        self.root.after(0, lambda: self.status_var.set(f"休息中... 剩余{rest_duration:.1f}秒"))
                        wait_time = 0
                        while wait_time < rest_duration and self.is_running:
                            time.sleep(0.1)
                            wait_time += 0.1
                            # 更新剩余休息时间显示
                            if self.is_running:
                                remaining = rest_duration - wait_time
                                self.root.after(0, lambda r=remaining: self.status_var.set(f"休息中... 剩余{r:.1f}秒"))
                        
                        # 检查是否在休息期间被停止
                        if not self.is_running:
                            break
                        
                        # 休息结束，恢复状态显示
                        if self.is_running:
                            self.root.after(0, lambda c=count: self.status_var.set(f"已点击 {c} 次"))
            except Exception as e:
                print(f"点击出错: {e}")
                break
        
        # 如果是因为完成了点击次数而停止
        if self.is_running:
            self.root.after(0, self.stop_clicking)
            self.root.after(0, lambda: messagebox.showinfo("完成", f"已完成 {count} 次点击"))

if __name__ == "__main__":
    root = tk.Tk()
    app = RandomClicker(root)
    root.mainloop()