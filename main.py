# -*- coding: utf-8 -*-
"""
main.py - 马年送祝福（最终版）
版本：v2.6.110
开发团队：卓影工作室 · 瑾 煜
功能：
- 开屏广告轮播
- 顶部轮播图（从网络加载，支持 active 控制，自动切换）
- 两个固定标题的下拉菜单（传统佳节/阳历节日），小标签显示当前选中节日（加粗）
- 自动判断默认节日（元宵节提前3天，其他2天）
- 祝福语数据从 data/bless.json 加载
- 分享按钮动态启用，底部图标栏自动显示/隐藏（显示后3秒自动隐藏）
- 下拉菜单颜色跟随激活组变化，下拉列表美观（浅米色选项，棕色分隔线，节日氛围）
- 版本更新检查（进入主界面时静默检查，有更新自动弹窗）
- 信息页面：整合操作指南、应用功能、关于信息、反馈建议（在线提交）
"""

import kivy
import sys
import os
import json
import traceback
import re
from datetime import datetime
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.carousel import Carousel
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner, SpinnerOption
from kivy.uix.dropdown import DropDown
from kivy.uix.image import Image, AsyncImage
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.core.clipboard import Clipboard
from kivy.clock import Clock
from kivy.utils import get_color_from_hex
from kivy.core.window import Window
from kivy.metrics import dp, sp
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.core.text import LabelBase
from kivy.animation import Animation
from kivy.network.urlrequest import UrlRequest

APP_VERSION = "v2.6.110"

# ---------- 注册系统字体 ----------
system_fonts = [
    '/system/fonts/DroidSansFallback.ttf',
    '/system/fonts/NotoSansCJK-Regular.ttc',
    '/system/fonts/Roboto-Regular.ttf'
]
font_registered = False
for font_path in system_fonts:
    try:
        LabelBase.register(name='Chinese', fn_regular=font_path)
        font_registered = True
        break
    except:
        continue
if not font_registered:
    LabelBase.register(name='Chinese', fn_regular='')

# ---------- 全局异常捕获 ----------
def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    try:
        private_dir = os.getenv('ANDROID_PRIVATE', '/sdcard')
        log_path = os.path.join(private_dir, 'crash.log')
        with open(log_path, 'a') as f:
            f.write(''.join(traceback.format_exception(exc_type, exc_value, exc_traceback)))
    except:
        pass

sys.excepthook = handle_exception
Window.clearcolor = get_color_from_hex('#FFF5E6')

from jnius import autoclass
PythonActivity = autoclass('org.kivy.android.PythonActivity')
Intent = autoclass('android.content.Intent')
Toast = autoclass('android.widget.Toast')
String = autoclass('java.lang.String')
Uri = autoclass('android.net.Uri')
context = PythonActivity.mActivity

def show_toast(message):
    try:
        Toast.makeText(context, String(message), Toast.LENGTH_SHORT).show()
    except Exception as e:
        print('Toast failed:', e)

def share_text(text):
    try:
        intent = Intent()
        intent.setAction(Intent.ACTION_SEND)
        intent.putExtra(Intent.EXTRA_TEXT, String(text))
        intent.setType('text/plain')
        context.startActivity(Intent.createChooser(intent, String('分享到')))
        return True
    except Exception as e:
        print('Share failed:', e)
        return False

def open_website(url):
    try:
        intent = Intent()
        intent.setAction(Intent.ACTION_VIEW)
        intent.setData(Uri.parse(url))
        context.startActivity(intent)
    except Exception as e:
        print('Open website failed:', e)

def send_email(recipient):
    try:
        intent = Intent(Intent.ACTION_SENDTO)
        intent.setData(Uri.parse('mailto:' + recipient))
        context.startActivity(intent)
    except Exception as e:
        print('Send email failed:', e)

# ==================== 自定义下拉列表容器 ====================
class CustomDropDown(DropDown):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 背景色设为棕色，通过spacing=1显示为分隔线
        self.background_normal = ''
        self.background_down = ''
        self.background_color = get_color_from_hex('#8B4513')  # 棕色
        self.border = (0, 0, 0, 0)
        self.border_radius = [dp(5), dp(5), dp(5), dp(5)]
        self.padding = 0
        self.spacing = 1  # 1像素间隙，背景色透出作为分隔线

# ==================== 自定义 Spinner 选项（解决乱码+美化）====================
class ChineseSpinnerOption(SpinnerOption):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.font_name = 'Chinese'
        # 清除默认背景图片，使用纯色背景
        self.background_normal = ''
        self.background_down = ''
        self.background_color = get_color_from_hex('#FFF8DC')  # 玉米色
        self.background_color_down = get_color_from_hex('#FFD700')  # 金色按下反馈
        self.color = get_color_from_hex('#8B4513')  # 深棕色文字
        self.border = (0, 0, 0, 0)                  # 无边框
        self.padding = [dp(15), dp(5)]
        self.size_hint_y = None
        self.height = dp(40)                         # 固定高度

Spinner.option_cls = ChineseSpinnerOption

# ==================== 加载祝福语数据 ====================
def load_blessings():
    base_dir = os.path.dirname(__file__)
    json_path = os.path.join(base_dir, 'data', 'bless.json')
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return {}, "数据格式错误：根节点不是字典"
        if len(data) == 0:
            return {}, "数据为空"
        first_festival = list(data.keys())[0]
        if not isinstance(data[first_festival], dict):
            return {}, f"节日 '{first_festival}' 的数据不是字典"
        return data, "成功"
    except FileNotFoundError:
        return {}, f"文件不存在: {json_path}"
    except json.JSONDecodeError as e:
        return {}, f"JSON 解析错误: {e}"
    except Exception as e:
        return {}, f"未知错误: {e}"

ALL_BLESSINGS, load_error = load_blessings()

# 节日分组
TRADITIONAL = ['春节', '开工大吉','元宵节', '母亲节', '端午节', '父亲节','中秋节']
PROFESSIONAL = ["女神节", '护士节', '建军节', '教师节', '国庆节', '记者节']

# 2026年节日日期
FESTIVAL_DATES_2026 = {
    '春节': (2, 17),
    '开工大吉': (2, 24),
    '元宵节': (3, 3),
    '女神节': (3, 8),
    '端午节': (6, 19),
    '中秋节': (9, 25),
    '护士节': (5, 12),
    '母亲节': (5, 10),
    '父亲节': (6, 21),
    '建军节': (8, 1),
    '教师节': (9, 10),
    '国庆节': (10, 1),
    '记者节': (11, 8),
}

def get_default_festival():
    today = datetime.now().date()
    yuanxiao_date = datetime(2026, 3, 3).date()
    yuanxiao_delta = (yuanxiao_date - today).days
    if 0 <= yuanxiao_delta <= 3:
        return '元宵节'
    best = None
    min_days = float('inf')
    for name, (month, day) in FESTIVAL_DATES_2026.items():
        festival_date = datetime(2026, month, day).date()
        delta = (festival_date - today).days
        if 0 <= delta <= 2 and delta < min_days:
            min_days = delta
            best = name
    return best if best else '春节'

# ==================== 开屏页面 ====================
class StartScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = FloatLayout()
        splash_images = ['images/splash1.png', 'images/splash2.png', 'images/splash3.png']
        self.carousel = Carousel(direction='right', loop=True)
        for img_path in splash_images:
            img = Image(source=img_path, allow_stretch=True, keep_ratio=False)
            self.carousel.add_widget(img)
        self.carousel.bind(on_touch_down=self.on_carousel_touch_down)
        layout.add_widget(self.carousel)

        indicator_layout = BoxLayout(
            size_hint=(None, None),
            size=(dp(len(splash_images)*30), dp(30)),
            pos_hint={'center_x': 0.5, 'y': 0.05},
            spacing=dp(5)
        )
        self.indicators = []
        for i in range(len(splash_images)):
            lbl = Label(
                text='○',
                font_size=sp(20),
                color=(1,1,1,1),
                size_hint=(None, None),
                size=(dp(20), dp(20)),
                font_name='Chinese'
            )
            self.indicators.append(lbl)
            indicator_layout.add_widget(lbl)
        self.update_indicator(0)
        layout.add_widget(indicator_layout)

        top_right = BoxLayout(size_hint=(None, None), size=(dp(160), dp(40)),
                              pos_hint={'right': 1, 'top': 1}, spacing=dp(5))
        self.countdown_label = Label(
            text='3 秒',
            size_hint=(None, None),
            size=(dp(60), dp(40)),
            color=(1,1,1,1),
            bold=True,
            font_name='Chinese'
        )
        skip_btn = Button(
            text='跳过',
            size_hint=(None, None),
            size=(dp(80), dp(40)),
            background_color=get_color_from_hex('#80000000'),
            color=(1,1,1,1),
            bold=True,
            font_name='Chinese'
        )
        skip_btn.bind(on_press=self.skip_to_main)
        top_right.add_widget(self.countdown_label)
        top_right.add_widget(skip_btn)
        layout.add_widget(top_right)

        self.add_widget(layout)

        self._auto_slide_trigger = None
        self._enter_timer = None
        self._idle_timer = None
        self.countdown = 9
        self._start_auto_slide()
        self._start_enter_countdown()

    def _start_auto_slide(self):
        self._stop_auto_slide()
        self._auto_slide_trigger = Clock.schedule_interval(self._next_slide, 3)

    def _stop_auto_slide(self):
        if self._auto_slide_trigger:
            self._auto_slide_trigger.cancel()
            self._auto_slide_trigger = None

    def _start_enter_countdown(self):
        self._stop_enter_countdown()
        self.countdown = 3
        self.countdown_label.text = '3 秒'
        self._enter_timer = Clock.schedule_interval(self._tick_countdown, 1)

    def _stop_enter_countdown(self):
        if self._enter_timer:
            self._enter_timer.cancel()
            self._enter_timer = None

    def _tick_countdown(self, dt):
        self.countdown -= 1
        self.countdown_label.text = f'{self.countdown} 秒'
        if self.countdown <= 0:
            self._stop_enter_countdown()
            self.go_main()

    def _next_slide(self, dt):
        self.carousel.load_next()

    def _reset_idle_timer(self):
        if self._idle_timer:
            self._idle_timer.cancel()
        self._idle_timer = Clock.schedule_once(self._resume_after_idle, 5)

    def _resume_after_idle(self, dt):
        self._idle_timer = None
        self._start_auto_slide()
        self._start_enter_countdown()

    def on_carousel_touch_down(self, instance, touch):
        if self.carousel.collide_point(*touch.pos):
            self._stop_auto_slide()
            self._stop_enter_countdown()
            self._reset_idle_timer()

    def update_indicator(self, index):
        for i, lbl in enumerate(self.indicators):
            lbl.text = '●' if i == index else '○'

    def on_enter(self):
        self.update_indicator(0)
        self.carousel.index = 0
        self._start_auto_slide()
        self._start_enter_countdown()
        if self._idle_timer:
            self._idle_timer.cancel()
            self._idle_timer = None

    def on_leave(self):
        self._stop_auto_slide()
        self._stop_enter_countdown()
        if self._idle_timer:
            self._idle_timer.cancel()
            self._idle_timer = None

    def skip_to_main(self, instance):
        self.on_leave()
        self.manager.current = 'main'

    def go_main(self, *args):
        self.manager.current = 'main'

# ==================== 优化后的信息页面 ====================
class InfoScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name_input = None
        self.email_input = None
        self.feedback_input = None
        self.build_ui()

    def build_ui(self):
        # 主布局：FloatLayout 用于绝对定位返回按钮
        main_layout = FloatLayout()
        with main_layout.canvas.before:
            Color(*get_color_from_hex('#E0F7FA'))  # 淡青蓝
            self.bg_rect = Rectangle(pos=main_layout.pos, size=main_layout.size)
        main_layout.bind(pos=self.update_bg, size=self.update_bg)

        # 返回按钮：绝对定位在左上角
        back_btn = Button(
            text='<',
            size_hint=(None, None),
            size=(dp(50), dp(50)),
            pos_hint={'x': 0, 'top': 1},
            background_normal='',
            background_color=(0,0,0,0),
            color=(0,0,0,1),
            font_size=sp(30),
            bold=True
        )
        back_btn.bind(on_press=self.go_back)
        main_layout.add_widget(back_btn)

        # 可滚动的内容区域（留出顶部空间）
        scroll_view = ScrollView(
            size_hint=(1, 0.95),
            pos_hint={'top': 0.95},
            bar_width=dp(4),
            bar_color=(0.5,0.5,0.5,0.5)
        )
        # 主内容布局：垂直排列，左边距统一为 dp(20)，右边距 dp(15)
        content_layout = BoxLayout(
            orientation='vertical',
            size_hint_y=None,
            padding=(dp(20), dp(10), dp(15), dp(30)),  # 增加底部内边距确保按钮显示
            spacing=dp(20)
        )
        content_layout.bind(minimum_height=content_layout.setter('height'))

        # ---- 操作指南版块 ----
        content_layout.add_widget(self.create_section('📌', '操作指南'))
        guide_items = [
            ('1.', '选择节日：点击顶部下拉菜单，选择“传统佳节”或“阳历节日”下的具体节日。'),
            ('2.', '切换分类：横向滑动分类按钮，选择祝福语类别（如“给长辈”、“给朋友”等）。'),
            ('3.', '复制祝福：点击任意祝福语卡片，内容自动复制到剪贴板并高亮。'),
            ('4.', '分享祝福：复制祝福后，底部绿色按钮可用，点击可通过微信/QQ/短信分享。'),
            ('5.', '其他功能：底部图标栏可访问官网、发送反馈邮件、查看关于信息。')
        ]
        for num, text in guide_items:
            content_layout.add_widget(self.create_guide_item(num, text))

        # ---- 应用功能版块 ----
        content_layout.add_widget(self.create_section('⚙️', '应用功能'))
        func_text = (
            "• 开屏广告轮播\n"
            "• 顶部轮播图（网络加载，支持 active 控制）\n"
            "• 自动判断默认节日（元宵节提前3天，其他2天）\n"
            "• 祝福语数据从 data/bless.json 加载\n"
            "• 分享按钮动态启用，底部图标栏自动显示/隐藏\n"
            "• 下拉菜单颜色跟随激活组变化，下拉列表美观\n"
            "• 版本更新检查（进入主界面静默检查，有更新自动弹窗）"
        )
        func_label = Label(
            text=func_text,
            color=(0,0,0,0.9),
            halign='left',
            valign='top',
            size_hint_y=None,
            height=dp(140),
            text_size=(content_layout.width - dp(40), None),  # 减去左右内边距
            font_name='Chinese',
            line_height=1.5
        )
        func_label.bind(
            width=lambda *x, l=func_label: setattr(l, 'text_size', (l.width, None)),
            texture_size=lambda *x, l=func_label: setattr(l, 'height', l.texture_size[1] + dp(5))
        )
        # 内容增加左边距
        func_label_container = BoxLayout(padding=[dp(25), 0, 0, 0], size_hint_y=None)
        func_label_container.add_widget(func_label)
        func_label_container.bind(height=func_label.setter('height'))
        content_layout.add_widget(func_label_container)

        # ---- 关于信息版块 ----
        content_layout.add_widget(self.create_section('ℹ️', '关于信息'))
        about_texts = [
            f'应用名称：马年送祝福',
            f'应用版本：{APP_VERSION}',
            f'应用开发：瑾 煜',
            f'反馈邮箱：jinyu@sjinyu.com',
            f'版权所有，侵权必究！'
        ]
        for line in about_texts:
            lbl = Label(
                text=line,
                color=(0,0,0,0.9),
                halign='left',
                valign='middle',
                size_hint_y=None,
                height=dp(25),
                font_name='Chinese'
            )
            lbl.bind(width=lambda *x, l=lbl: setattr(l, 'text_size', (l.width, None)))
            # 增加左边距
            container = BoxLayout(padding=[dp(25), 0, 0, 0], size_hint_y=None)
            container.add_widget(lbl)
            container.bind(height=lbl.setter('height'))
            content_layout.add_widget(container)

        # ---- 反馈建议版块 ----
        content_layout.add_widget(self.create_section('💬', '反馈建议'))

        # 姓名
        name_label = Label(
            text='您的姓名（称呼）',
            color=(0,0,0,0.8),
            halign='left',
            size_hint_y=None,
            height=dp(25),
            font_name='Chinese'
        )
        name_label.bind(width=lambda *x, l=name_label: setattr(l, 'text_size', (l.width, None)))
        content_layout.add_widget(name_label)

        self.name_input = TextInput(
            hint_text='请输入您的姓名',
            size_hint_y=None,
            height=dp(40),
            font_name='Chinese',
            background_color=(0.96, 0.96, 0.96, 1),  # 浅灰背景
            foreground_color=(0,0,0,0.9),
            hint_text_color=(0.7,0.7,0.7,1),
            border=(0,0,0,0)  # 无边框
        )
        content_layout.add_widget(self.name_input)

        # 邮箱
        email_label = Label(
            text='联系方式（电邮）',
            color=(0,0,0,0.8),
            halign='left',
            size_hint_y=None,
            height=dp(25),
            font_name='Chinese'
        )
        email_label.bind(width=lambda *x, l=email_label: setattr(l, 'text_size', (l.width, None)))
        content_layout.add_widget(email_label)

        self.email_input = TextInput(
            hint_text='请输入您的电子邮箱',
            size_hint_y=None,
            height=dp(40),
            font_name='Chinese',
            background_color=(0.96, 0.96, 0.96, 1),
            foreground_color=(0,0,0,0.9),
            hint_text_color=(0.7,0.7,0.7,1),
            border=(0,0,0,0)
        )
        content_layout.add_widget(self.email_input)

        # 反馈内容
        feedback_label = Label(
            text='反馈与建议',
            color=(0,0,0,0.8),
            halign='left',
            size_hint_y=None,
            height=dp(25),
            font_name='Chinese'
        )
        feedback_label.bind(width=lambda *x, l=feedback_label: setattr(l, 'text_size', (l.width, None)))
        content_layout.add_widget(feedback_label)

        self.feedback_input = TextInput(
            text='请将您的反馈与建议写在这里',
            size_hint_y=None,
            height=dp(100),
            font_name='Chinese',
            background_color=(0.96, 0.96, 0.96, 1),
            foreground_color=(0.7,0.7,0.7,1),  # 初始灰色
            border=(0,0,0,0),
            multiline=True
        )
        self.feedback_input.bind(focus=self.on_feedback_focus)
        content_layout.add_widget(self.feedback_input)

        # 按钮水平居中
        btn_layout = BoxLayout(size_hint=(1, None), height=dp(40), spacing=dp(20))
        submit_btn = Button(
            text='提交',
            size_hint=(0.5, 1),
            background_color=get_color_from_hex('#4CAF50'),
            color=(1,1,1,1),
            font_name='Chinese'
        )
        submit_btn.bind(on_press=self.submit_feedback)
        cancel_btn = Button(
            text='取消',
            size_hint=(0.5, 1),
            background_color=get_color_from_hex('#9E9E9E'),
            color=(1,1,1,1),
            font_name='Chinese'
        )
        cancel_btn.bind(on_press=self.go_back)
        btn_layout.add_widget(submit_btn)
        btn_layout.add_widget(cancel_btn)
        content_layout.add_widget(btn_layout)

        # 底部额外留白
        content_layout.add_widget(Label(size_hint_y=None, height=dp(20)))

        scroll_view.add_widget(content_layout)
        main_layout.add_widget(scroll_view)

        self.add_widget(main_layout)

    def update_bg(self, instance, value):
        self.bg_rect.pos = instance.pos
        self.bg_rect.size = instance.size

    def create_section(self, icon, title):
        """创建带图标、标题和分隔线的版块标题"""
        section = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(40), spacing=dp(5))
        title_layout = BoxLayout(size_hint_y=None, height=dp(30))
        icon_label = Label(
            text=icon,
            color=get_color_from_hex('#006064'),
            font_size=sp(20),
            size_hint=(None, 1),
            width=dp(30),
            halign='center',
            valign='middle'
        )
        title_label = Label(
            text=title,
            color=get_color_from_hex('#006064'),
            bold=True,
            font_size=sp(18),
            size_hint_x=0.5,
            halign='left',
            valign='middle',
            font_name='Chinese'
        )
        title_label.bind(width=lambda *x, l=title_label: setattr(l, 'text_size', (l.width, None)))
        # 右侧分隔线
        line = Label(
            size_hint_x=0.5,
            height=dp(2),
            color=(0.8,0.8,0.8,1),
            background_color=(0.8,0.8,0.8,1)
        )
        title_layout.add_widget(icon_label)
        title_layout.add_widget(title_label)
        title_layout.add_widget(line)
        section.add_widget(title_layout)
        return section

    def create_guide_item(self, num, text):
        """创建带序号的操作指南条目"""
        item = BoxLayout(orientation='horizontal', size_hint_y=None, spacing=dp(5), padding=[dp(25), 0, 0, 0])
        num_label = Label(
            text=num,
            color=(0,0,0,0.9),
            halign='right',
            valign='top',
            size_hint=(None, None),
            width=dp(30),
            height=dp(40),
            font_name='Chinese',
            text_size=(dp(30), None)
        )
        content_label = Label(
            text=text,
            color=(0,0,0,0.9),
            halign='left',
            valign='top',
            size_hint_y=None,
            height=dp(40),
            text_size=(self.width - dp(55), None),  # 减去左边距和序号宽度
            font_name='Chinese',
            line_height=1.4
        )
        content_label.bind(
            width=lambda *x, l=content_label: setattr(l, 'text_size', (l.width, None)),
            texture_size=lambda *x, l=content_label: setattr(l, 'height', l.texture_size[1] + dp(5))
        )
        content_label.bind(height=lambda *x, layout=item: layout.setter('height')(layout, content_label.height))
        content_label.bind(height=lambda *x, nl=num_label: setattr(nl, 'height', content_label.height))

        item.add_widget(num_label)
        item.add_widget(content_label)
        return item

    def on_feedback_focus(self, instance, value):
        if value:
            if instance.text == '请将您的反馈与建议写在这里':
                instance.text = ''
                instance.foreground_color = (0,0,0,0.9)
        else:
            if not instance.text.strip():
                instance.text = '请将您的反馈与建议写在这里'
                instance.foreground_color = (0.7,0.7,0.7,1)

    def validate_email(self, email):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def submit_feedback(self, instance):
        name = self.name_input.text.strip()
        email = self.email_input.text.strip()
        content = self.feedback_input.text.strip()
        if content == '请将您的反馈与建议写在这里':
            content = ''

        if not name:
            show_toast('请输入您的姓名')
            return
        if not email:
            show_toast('请输入您的电子邮箱')
            return
        if not self.validate_email(email):
            show_toast('邮箱格式不正确')
            return
        if not content:
            show_toast('请输入反馈内容')
            return

        # 发送反馈到服务器
        url = 'https://www.sjinyu.com/tools/bless/data/feedback.php'
        data = json.dumps({
            'name': name,
            'email': email,
            'content': content
        })

        def on_success(req, result):
            show_toast('反馈提交成功，感谢您的支持！')
            self.go_back(None)

        def on_failure(req, result):
            print('❌ 提交失败，HTTP状态码:', req.resp_status)
            print('返回内容:', result)
            show_toast('提交失败，请稍后重试')

        def on_error(req, error):
            print('❌ 网络错误:', error)
            show_toast('网络错误，请检查连接')

        UrlRequest(url, req_body=data, req_headers={'Content-Type': 'application/json'},
                   on_success=on_success, on_failure=on_failure, on_error=on_error, method='POST')
        show_toast('正在提交...')

    def go_back(self, instance):
        self.manager.current = 'main'

# ==================== 主页面 ====================
class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.default_festival = get_default_festival()
        if self.default_festival in ALL_BLESSINGS:
            self.current_festival = self.default_festival
        else:
            self.current_festival = TRADITIONAL[0] if TRADITIONAL else list(ALL_BLESSINGS.keys())[0]
        festival_data = ALL_BLESSINGS.get(self.current_festival, {})
        self.current_category = list(festival_data.keys())[0] if festival_data else ''
        self.selected_item = None
        self.last_copied_text = None
        self.has_selected = False
        self.footer_visible = False
        self.last_scroll_y = 1
        self._footer_timer = None
        self._update_checked = False

        # 颜色定义
        self.DEFAULT_BTN = get_color_from_hex('#CCCC99')
        self.ACTIVE_BTN = get_color_from_hex('#FFCC99')
        self.FOOTER_BG = get_color_from_hex('#333300')

        main_layout = BoxLayout(orientation='vertical', spacing=0, padding=0)
        main_layout.size_hint_y = 1

        # ===== 顶部轮播图 =====
        self.top_carousel = Carousel(direction='right', loop=True, size_hint_y=None, height=dp(150))
        main_layout.add_widget(self.top_carousel)
        Clock.schedule_interval(lambda dt: self.top_carousel.load_next(), 3)
        self.load_top_ads()

        # ===== 两个并排的下拉菜单 =====
        spinner_layout = BoxLayout(size_hint=(1, None), height=dp(50), spacing=dp(5))
        self.traditional_spinner = Spinner(
            text='传统佳节',
            values=TRADITIONAL,
            size_hint=(0.5, 1),
            background_color=self.DEFAULT_BTN,
            color=(1,1,1,1),
            font_name='Chinese'
        )
        self.traditional_spinner.bind(text=self.on_traditional_spinner_select)
        self.professional_spinner = Spinner(
            text='阳历节日',
            values=PROFESSIONAL,
            size_hint=(0.5, 1),
            background_color=self.DEFAULT_BTN,
            color=(1,1,1,1),
            font_name='Chinese'
        )
        self.professional_spinner.bind(text=self.on_professional_spinner_select)
        self.traditional_spinner.dropdown_cls = CustomDropDown
        self.professional_spinner.dropdown_cls = CustomDropDown

        spinner_layout.add_widget(self.traditional_spinner)
        spinner_layout.add_widget(self.professional_spinner)
        main_layout.add_widget(spinner_layout)

        # ===== 分类切换按钮 =====
        self.category_scroll = ScrollView(size_hint=(1, None), height=dp(50), do_scroll_x=True, do_scroll_y=False)
        self.category_layout = BoxLayout(size_hint_x=None, height=dp(50), spacing=dp(2))
        self.category_layout.bind(minimum_width=self.category_layout.setter('width'))
        self.category_scroll.add_widget(self.category_layout)
        main_layout.add_widget(self.category_scroll)

        # ===== 当前节日标签 =====
        self.current_festival_label = Label(
            text=f"当前节日：{self.current_festival}",
            size_hint=(1, None),
            height=dp(30),
            color=(0.5,0.1,0.1,1),
            font_name='Chinese',
            halign='center',
            bold=True
        )
        main_layout.add_widget(self.current_festival_label)

        # ===== 祝福语列表 =====
        self.scroll_view = ScrollView()
        self.scroll_view.size_hint_y = 1
        self.scroll_view.bind(scroll_y=self.on_scroll)
        self.list_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(8))
        self.list_layout.bind(minimum_height=self.list_layout.setter('height'))
        self.scroll_view.add_widget(self.list_layout)
        main_layout.add_widget(self.scroll_view)

        # ===== 底部区域 =====
        bottom_container = FloatLayout(size_hint=(1, None), height=dp(80))
        self.share_btn = Button(
            text='通过微信/QQ/短信祝福好友',
            size_hint=(1, None),
            height=dp(50),
            background_normal='',
            background_color=(0.67,0.67,0.67,1),
            color=(1,1,1,1),
            font_name='Chinese',
            font_size=sp(18),
            disabled=True
        )
        self.share_btn.bind(on_press=self.share_blessings)
        self.share_btn.pos = (0, 0)
        bottom_container.add_widget(self.share_btn)

        # 图标栏
        self.footer = BoxLayout(
            orientation='vertical',
            size_hint=(1, None),
            height=dp(80),
            pos=(0, -dp(80))
        )
        with self.footer.canvas.before:
            Color(*self.FOOTER_BG)
            self.footer_bg = Rectangle(pos=self.footer.pos, size=self.footer.size)
        self.footer.bind(pos=lambda instance, value: setattr(self.footer_bg, 'pos', value))
        self.footer.bind(size=lambda instance, value: setattr(self.footer_bg, 'size', value))

        icon_layout = BoxLayout(
            size_hint=(None, None),
            size=(dp(240), dp(40)),
            pos_hint={'center_x': 0.5},
            spacing=dp(20)
        )
        web_btn = Button(
            background_normal='images/icon_web.png',
            background_down='images/icon_web.png',
            size_hint=(None, 1),
            width=dp(40),
            border=(0,0,0,0)
        )
        web_btn.bind(on_press=lambda x: open_website('https://www.sjinyu.com'))

        email_btn = Button(
            background_normal='images/icon_email.png',
            background_down='images/icon_email.png',
            size_hint=(None, 1),
            width=dp(40),
            border=(0,0,0,0)
        )
        email_btn.bind(on_press=lambda x: send_email('jinyu@sjinyu.com'))

        about_btn = Button(
            background_normal='images/icon_about.png',
            background_down='images/icon_about.png',
            size_hint=(None, 1),
            width=dp(40),
            border=(0,0,0,0)
        )
        about_btn.bind(on_press=self.go_to_info)

        help_btn = Button(
            background_normal='images/icon_help.png',
            background_down='images/icon_help.png',
            size_hint=(None, 1),
            width=dp(40),
            border=(0,0,0,0)
        )
        help_btn.bind(on_press=self.go_to_info)

        icon_layout.add_widget(web_btn)
        icon_layout.add_widget(email_btn)
        icon_layout.add_widget(about_btn)
        icon_layout.add_widget(help_btn)

        copyright_label = Label(
            text='Copyright Reserved © Sjinyu.com 2025-2026',
            size_hint=(1, None),
            height=dp(20),
            color=(1,1,1,1),
            font_size=sp(10),
            font_name='Chinese',
            halign='center'
        )

        self.footer.add_widget(icon_layout)
        self.footer.add_widget(copyright_label)
        bottom_container.add_widget(self.footer)
        main_layout.add_widget(bottom_container)

        self.add_widget(main_layout)
        self.update_category_buttons()
        self.show_current_page()
        self.update_spinner_colors()

    def go_to_info(self, instance):
        self.manager.current = 'info'

    def on_enter(self):
        if not self._update_checked:
            self._check_update_silent()
            self._update_checked = True

    # ========== 滚动控制 ==========
    def on_scroll(self, instance, value):
        try:
            if not self.footer:
                return
            if value < self.last_scroll_y - 0.01:
                self.hide_footer_animated()
            elif value > self.last_scroll_y + 0.01:
                self.show_footer_animated()
            self.last_scroll_y = value
        except Exception as e:
            print("on_scroll error:", e)

    def show_footer_animated(self):
        if not self.footer or self.footer_visible:
            return
        try:
            if self._footer_timer:
                self._footer_timer.cancel()
                self._footer_timer = None
            anim = Animation(y=0, duration=0.3, t='out_quad')
            anim.start(self.footer)
            self.footer_visible = True
            self._footer_timer = Clock.schedule_once(lambda dt: self.hide_footer_animated(), 3)
        except Exception as e:
            print("show_footer_animated error:", e)

    def hide_footer_animated(self):
        if not self.footer or not self.footer_visible:
            return
        try:
            if self._footer_timer:
                self._footer_timer.cancel()
                self._footer_timer = None
            anim = Animation(y=-dp(80), duration=0.3, t='out_quad')
            anim.start(self.footer)
            self.footer_visible = False
        except Exception as e:
            print("hide_footer_animated error:", e)

    # ========== 下拉菜单 ==========
    def update_spinner_colors(self):
        if self.current_festival in TRADITIONAL:
            self.traditional_spinner.background_color = self.ACTIVE_BTN
            self.professional_spinner.background_color = self.DEFAULT_BTN
        elif self.current_festival in PROFESSIONAL:
            self.traditional_spinner.background_color = self.DEFAULT_BTN
            self.professional_spinner.background_color = self.ACTIVE_BTN
        else:
            self.traditional_spinner.background_color = self.DEFAULT_BTN
            self.professional_spinner.background_color = self.DEFAULT_BTN

    def on_traditional_spinner_select(self, spinner, text):
        self.current_festival = text
        self.current_festival_label.text = f"当前节日：{self.current_festival}"
        festival_data = ALL_BLESSINGS.get(self.current_festival, {})
        self.current_category = list(festival_data.keys())[0] if festival_data else ''
        self.update_category_buttons()
        self.show_current_page()
        self.update_spinner_colors()

    def on_professional_spinner_select(self, spinner, text):
        self.current_festival = text
        self.current_festival_label.text = f"当前节日：{self.current_festival}"
        festival_data = ALL_BLESSINGS.get(self.current_festival, {})
        self.current_category = list(festival_data.keys())[0] if festival_data else ''
        self.update_category_buttons()
        self.show_current_page()
        self.update_spinner_colors()

    # ========== 分类按钮 ==========
    def update_category_buttons(self):
        self.category_layout.clear_widgets()
        festival_data = ALL_BLESSINGS.get(self.current_festival, {})
        categories = list(festival_data.keys())
        for cat in categories:
            btn = Button(
                text=cat,
                size_hint=(None, 1),
                width=dp(120),
                background_color=get_color_from_hex('#DAA520' if cat == self.current_category else '#8B4513'),
                color=(1,1,1,1),
                font_name='Chinese'
            )
            btn.bind(on_press=lambda x, c=cat: self.switch_category(c))
            self.category_layout.add_widget(btn)

    def switch_category(self, category):
        if category == self.current_category:
            return
        self.current_category = category
        self.update_category_buttons()
        self.show_current_page()

    # ========== 祝福语列表 ==========
    def show_current_page(self):
        self.list_layout.clear_widgets()
        festival_data = ALL_BLESSINGS.get(self.current_festival, {})
        if not festival_data:
            hint = Label(
                text="该节日暂无数据或数据格式错误",
                size_hint_y=None,
                height=dp(80),
                color=(1,0,0,1),
                font_name='Chinese'
            )
            self.list_layout.add_widget(hint)
            return
        blessings = festival_data.get(self.current_category, [])
        if not blessings:
            hint = Label(
                text="该分类暂无祝福语",
                size_hint_y=None,
                height=dp(80),
                color=(1,0,0,1),
                font_name='Chinese'
            )
            self.list_layout.add_widget(hint)
            return
        for text in blessings:
            btn = Button(
                text=text,
                size_hint_y=None,
                height=dp(80),
                background_normal='',
                background_color=(1, 1, 1, 0.9),
                color=(0.1, 0.1, 0.1, 1),
                halign='left',
                valign='top',
                padding=(dp(10), dp(5)),
                font_name='Chinese'
            )
            btn.bind(
                width=lambda *x, b=btn: b.setter('text_size')(b, (b.width - dp(20), None)),
                texture_size=lambda *x, b=btn: setattr(b, 'height', b.texture_size[1] + dp(10))
            )
            btn.bind(on_press=self.on_copy)
            btn.blessing_text = text
            btn.default_bg_color = (1, 1, 1, 0.9)
            self.list_layout.add_widget(btn)

    # ========== 复制与分享 ==========
    def on_copy(self, instance):
        try:
            print("on_copy triggered")
            text = instance.blessing_text
            if not text:
                print("错误：按钮没有 blessing_text 属性")
                return

            Clipboard.copy(text)
            print("剪贴板已复制")

            self.last_copied_text = text

            try:
                show_toast('祝福语已复制')
            except Exception as e:
                print("Toast 失败:", e)

            if self.selected_item and self.selected_item != instance:
                self.selected_item.background_color = (1, 1, 1, 0.9)
                self.selected_item.color = (0.1, 0.1, 0.1, 1)
                self.selected_item.canvas.ask_update()

            instance.background_color = (0.5, 0.1, 0.1, 1)
            instance.color = (1, 1, 0, 1)
            instance.canvas.ask_update()

            self.selected_item = instance

            if not self.has_selected:
                self.has_selected = True
                self.share_btn.background_color = get_color_from_hex('#4CAF50')
                self.share_btn.disabled = False

            print("视觉反馈已应用")
        except Exception as e:
            print("on_copy 发生异常:", e)

    def share_blessings(self, instance):
        if self.last_copied_text:
            if share_text(self.last_copied_text):
                show_toast('分享已启动')
            else:
                Clipboard.copy(self.last_copied_text)
                show_toast('分享失败，已复制到剪贴板')
        else:
            show_toast('请先选择一条祝福')

    # ========== 静默检查更新 ==========
    def parse_version(self, version_str):
        if version_str.startswith('v'):
            version_str = version_str[1:]
        parts = version_str.split('.')
        return [int(p) for p in parts]

    def is_newer_version(self, latest, current):
        return self.parse_version(latest) > self.parse_version(current)

    def _check_update_silent(self):
        url = 'https://www.sjinyu.com/tools/bless/data/update.json'

        def on_success(req, result):
            try:
                if isinstance(result, str):
                    result = json.loads(result)
                latest_version = result.get('version', '未知版本')
                message = result.get('message', '无更新说明')
                download_url = result.get('url', None)

                if self.is_newer_version(latest_version, APP_VERSION):
                    self.show_update_popup(latest_version, message, download_url, is_latest=False)
            except Exception as e:
                print('静默更新检查解析失败:', e)

        def on_failure(req, result):
            print('静默更新检查请求失败:', result)

        def on_error(req, error):
            print('静默更新检查网络错误:', error)

        UrlRequest(url, on_success=on_success, on_failure=on_failure, on_error=on_error)

    def show_update_popup(self, latest_version, message, url=None, is_latest=False):
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.button import Button
        from kivy.uix.label import Label
        from kivy.uix.popup import Popup
        from kivy.graphics import Color, RoundedRectangle, Rectangle

        popup_height = 180 if is_latest else 250
        content = BoxLayout(orientation='vertical', spacing=0, padding=0,
                            size_hint=(None, None), size=(dp(320), dp(popup_height)))
        with content.canvas.before:
            Color(1, 1, 1, 1)
            self.popup_bg = RoundedRectangle(pos=content.pos, size=content.size, radius=[dp(10)])
        content.bind(pos=lambda *x: setattr(self.popup_bg, 'pos', content.pos),
                     size=lambda *x: setattr(self.popup_bg, 'size', content.size))

        title_bar = BoxLayout(size_hint_y=None, height=dp(40), padding=(dp(10), 0))
        with title_bar.canvas.before:
            Color(0.5, 0.1, 0.1, 1)
            self.popup_title_rect = RoundedRectangle(pos=title_bar.pos, size=title_bar.size, radius=[dp(10), dp(10), 0, 0])
        title_bar.bind(pos=lambda *x: setattr(self.popup_title_rect, 'pos', title_bar.pos),
                       size=lambda *x: setattr(self.popup_title_rect, 'size', title_bar.size))

        if is_latest:
            title_text = "已是最新版"
        else:
            title_text = f"发现新版本 {latest_version}"

        title_label = Label(
            text=title_text,
            color=(1,1,1,1),
            halign='left',
            valign='middle',
            size_hint_x=0.8,
            font_name='Chinese'
        )
        close_btn = Button(
            text='X',
            size_hint=(None, None),
            size=(dp(30), dp(30)),
            pos_hint={'right':1, 'center_y':0.5},
            background_color=(0,0,0,0),
            color=(1,1,1,1),
            bold=True,
            font_name='Chinese'
        )
        close_btn.bind(on_press=lambda x: popup.dismiss())
        title_bar.add_widget(title_label)
        title_bar.add_widget(close_btn)

        content_area = BoxLayout(orientation='vertical', padding=(dp(15), dp(10)), spacing=dp(5))

        if not is_latest:
            version_label = Label(
                text=f'最新版本：{latest_version}',
                color=(0,0,0,1),
                halign='left',
                valign='middle',
                size_hint_y=None,
                height=dp(25),
                font_name='Chinese'
            )
            version_label.bind(width=lambda *x, l=version_label: setattr(l, 'text_size', (l.width, None)))
            content_area.add_widget(version_label)

        msg_label = Label(
            text=f'更新内容：{message}',
            color=(0,0,0,1),
            halign='left',
            valign='top',
            size_hint_y=None,
            height=dp(80),
            text_size=(content_area.width - dp(20), None),
            font_name='Chinese'
        )
        msg_label.bind(width=lambda *x, l=msg_label: setattr(l, 'text_size', (l.width - dp(20), None)))
        content_area.add_widget(msg_label)

        if not is_latest and url:
            button_layout = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(10), padding=(dp(10),0))
            download_btn = Button(
                text='立即下载',
                size_hint=(0.5, 1),
                background_color=get_color_from_hex('#4CAF50'),
                color=(1,1,1,1),
                font_name='Chinese'
            )
            download_btn.bind(on_press=lambda x: (popup.dismiss(), open_website(url)))
            cancel_btn = Button(
                text='以后再说',
                size_hint=(0.5, 1),
                background_color=get_color_from_hex('#9E9E9E'),
                color=(1,1,1,1),
                font_name='Chinese'
            )
            cancel_btn.bind(on_press=lambda x: popup.dismiss())
            button_layout.add_widget(download_btn)
            button_layout.add_widget(cancel_btn)
            content_area.add_widget(button_layout)

        content.add_widget(title_bar)
        content.add_widget(content_area)

        popup = Popup(
            title='',
            content=content,
            size_hint=(None, None),
            size=content.size,
            background_color=(0,0,0,0),
            auto_dismiss=False
        )
        popup.open()

    # ========== 轮播广告相关 ==========
    def load_top_ads(self):
        url = 'https://www.sjinyu.com/tools/bless/data/ads.json'

        def on_success(req, result):
            try:
                if isinstance(result, str):
                    result = json.loads(result)
                ads_list = result.get('ads', [])
                active_ads = [ad for ad in ads_list if ad.get('active') is True]
                active_ads.sort(key=lambda ad: ad.get('display_order', 999))
                self.top_carousel.clear_widgets()
                for ad in active_ads:
                    img_url = ad.get('image_url')
                    link_url = ad.get('redirect_url')
                    if img_url:
                        try:
                            img = AsyncImage(source=img_url, allow_stretch=True, keep_ratio=False)
                            if link_url:
                                img.bind(on_touch_down=lambda instance, touch, url=link_url: self.on_ad_click(instance, touch, url))
                            self.top_carousel.add_widget(img)
                        except Exception as e:
                            print(f"加载网络图片 {img_url} 失败: {e}")
                if not active_ads:
                    self.load_fallback_ads()
            except Exception as e:
                print('解析广告数据失败:', e)
                self.load_fallback_ads()

        def on_failure(req, result):
            print('广告请求失败:', result)
            self.load_fallback_ads()

        def on_error(req, error):
            print('广告请求错误:', error)
            self.load_fallback_ads()

        try:
            UrlRequest(url, on_success=on_success, on_failure=on_failure, on_error=on_error)
        except Exception as e:
            print('UrlRequest 异常:', e)
            self.load_fallback_ads()

    def load_fallback_ads(self):
        self.top_carousel.clear_widgets()
        for i in range(1, 6):
            img_path = f'images/top{i:02d}.jpg'
            if not os.path.exists(img_path):
                print(f"备用图片 {img_path} 不存在，已跳过")
                continue
            try:
                img = Image(source=img_path, allow_stretch=True, keep_ratio=False)
                img.bind(on_touch_down=lambda instance, touch, path=img_path: self.on_fallback_ad_click(instance, touch))
                self.top_carousel.add_widget(img)
            except Exception as e:
                print(f"加载备用图片 {img_path} 失败: {e}")

    def on_fallback_ad_click(self, instance, touch):
        try:
            if instance.collide_point(*touch.pos):
                open_website('https://www.sjinyu.com')
        except Exception as e:
            print("on_fallback_ad_click 异常:", e)

    def on_ad_click(self, instance, touch, url):
        try:
            if instance.collide_point(*touch.pos):
                open_website(url)
        except Exception as e:
            print("on_ad_click 异常:", e)


class BlessApp(App):
    def build(self):
        # 强制隐藏状态栏，确保全屏显示
        try:
            from jnius import autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            WindowManager = autoclass('android.view.WindowManager')
            View = autoclass('android.view.View')
            activity = PythonActivity.mActivity
            if activity:
                # 添加全屏标志
                activity.getWindow().addFlags(WindowManager.LayoutParams.FLAG_FULLSCREEN)
                # 隐藏导航栏并启用沉浸模式
                decor_view = activity.getWindow().getDecorView()
                ui_options = (
                    View.SYSTEM_UI_FLAG_HIDE_NAVIGATION |
                    View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY |
                    View.SYSTEM_UI_FLAG_FULLSCREEN
                )
                decor_view.setSystemUiVisibility(ui_options)
        except Exception as e:
            print("设置全屏标志失败:", e)

        Window.borderless = True
        Window.fullscreen = True
        Window.size = Window.system_size
        # 强制窗口位置归零（确保贴顶）
        Window.top = 0
        Window.left = 0

        sm = ScreenManager()
        sm.add_widget(StartScreen(name='start'))
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(InfoScreen(name='info'))
        return sm

    def on_start(self):
        """应用启动后再次确保全屏"""
        try:
            from jnius import autoclass
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            WindowManager = autoclass('android.view.WindowManager')
            View = autoclass('android.view.View')
            activity = PythonActivity.mActivity
            if activity:
                activity.getWindow().addFlags(WindowManager.LayoutParams.FLAG_FULLSCREEN)
                decor_view = activity.getWindow().getDecorView()
                ui_options = (
                    View.SYSTEM_UI_FLAG_HIDE_NAVIGATION |
                    View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY |
                    View.SYSTEM_UI_FLAG_FULLSCREEN
                )
                decor_view.setSystemUiVisibility(ui_options)
        except Exception as e:
            print("on_start 全屏设置失败:", e)

        # 打印窗口位置用于调试
        print(f"Window position: top={Window.top}, left={Window.left}, size={Window.size}")

if __name__ == '__main__':
    BlessApp().run()
