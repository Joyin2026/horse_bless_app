# -*- coding: utf-8 -*-
"""
main.py - 马年送祝福（最终版）
版本：v2.6.102
开发团队：卓影工作室 · 瑾 煜
功能：
- 开屏广告轮播
- 顶部轮播图（从网络加载，支持 active 控制，自动切换）
- 两个固定标题的下拉菜单（传统佳节/行业节日），小标签显示当前选中节日（加粗）
- 自动判断默认节日（元宵节提前8天，其他5天）
- 祝福语数据从 data/bless.json 加载
- 分享按钮动态启用，底部图标栏自动显示/隐藏
- 下拉菜单颜色跟随激活组变化
- 版本更新检查（从网络获取，正确判断有无更新）
"""

import kivy
import sys
import os
import json
import traceback
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
from kivy.uix.image import Image, AsyncImage
from kivy.uix.popup import Popup
from kivy.core.clipboard import Clipboard
from kivy.clock import Clock
from kivy.utils import get_color_from_hex
from kivy.core.window import Window
from kivy.metrics import dp, sp
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.core.text import LabelBase
from kivy.animation import Animation
from kivy.network.urlrequest import UrlRequest

APP_VERSION = "v2.6.102"

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

# ==================== 自定义 Spinner 选项（解决乱码）====================
class ChineseSpinnerOption(SpinnerOption):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.font_name = 'Chinese'

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
PROFESSIONAL = ['护士节', '建军节', '教师节', '国庆节', '记者节']

# 2026年节日日期
FESTIVAL_DATES_2026 = {
    '春节': (2, 17),
    '开工大吉': (2, 24),
    '元宵节': (3, 3),
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
    if 0 <= yuanxiao_delta <= 8:
        return '元宵节'
    best = None
    min_days = float('inf')
    for name, (month, day) in FESTIVAL_DATES_2026.items():
        festival_date = datetime(2026, month, day).date()
        delta = (festival_date - today).days
        if 0 <= delta <= 5 and delta < min_days:
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
            text='6 秒',
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
        self.countdown = 6
        self.countdown_label.text = '6 秒'
        self._enter_timer = Clock.schedule_interval(self._tick_countdown, 3)

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

        # 颜色定义
        self.DEFAULT_BTN = get_color_from_hex('#CCCC99')
        self.ACTIVE_BTN = get_color_from_hex('#FFCC99')
        self.FOOTER_BG = get_color_from_hex('#333300')

        main_layout = BoxLayout(orientation='vertical', spacing=0, padding=0)
        main_layout.size_hint_y = 1

        # ===== 顶部轮播图 =====
        self.top_carousel = Carousel(direction='right', loop=True, size_hint_y=None, height=dp(150))
        main_layout.add_widget(self.top_carousel)

        # 启动自动轮播（每3秒切换）
        Clock.schedule_interval(lambda dt: self.top_carousel.load_next(), 3)

        # 加载轮播广告（网络优先）
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
            text='行业节日',
            values=PROFESSIONAL,
            size_hint=(0.5, 1),
            background_color=self.DEFAULT_BTN,
            color=(1,1,1,1),
            font_name='Chinese'
        )
        self.professional_spinner.bind(text=self.on_professional_spinner_select)
        spinner_layout.add_widget(self.traditional_spinner)
        spinner_layout.add_widget(self.professional_spinner)
        main_layout.add_widget(spinner_layout)

        # ===== 分类切换按钮（横向滚动）=====
        self.category_scroll = ScrollView(size_hint=(1, None), height=dp(50), do_scroll_x=True, do_scroll_y=False)
        self.category_layout = BoxLayout(size_hint_x=None, height=dp(50), spacing=dp(2))
        self.category_layout.bind(minimum_width=self.category_layout.setter('width'))
        self.category_scroll.add_widget(self.category_layout)
        main_layout.add_widget(self.category_scroll)

        # ===== 当前节日标签（移至分类按钮下方，加粗）=====
        self.current_festival_label = Label(
            text=f"当前节日：{self.current_festival}",
            size_hint=(1, None),
            height=dp(30),
            color=(0.5,0.1,0.1,1),
            font_name='Chinese',
            halign='center',
            bold=True  # 加粗
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
        
        # 分享按钮
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
        about_btn.bind(on_press=self.show_about_popup)
        update_btn = Button(
            background_normal='images/icon_update.png',
            background_down='images/icon_update.png',
            size_hint=(None, 1),
            width=dp(40),
            border=(0,0,0,0)
        )
        update_btn.bind(on_press=self.check_update)

        icon_layout.add_widget(web_btn)
        icon_layout.add_widget(email_btn)
        icon_layout.add_widget(about_btn)
        icon_layout.add_widget(update_btn)

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
            anim = Animation(y=0, duration=0.3, t='out_quad')
            anim.start(self.footer)
            self.footer_visible = True
        except Exception as e:
            print("show_footer_animated error:", e)

    def hide_footer_animated(self):
        if not self.footer or not self.footer_visible:
            return
        try:
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

    # ========== 关于弹窗 ==========
    def show_about_popup(self, instance):
        content = BoxLayout(orientation='vertical', spacing=0, padding=0,
                            size_hint=(None, None), size=(dp(320), dp(220)))
        with content.canvas.before:
            Color(1, 1, 1, 1)
            self.bg_rect = RoundedRectangle(pos=content.pos, size=content.size, radius=[dp(10)])
        content.bind(pos=lambda *x: setattr(self.bg_rect, 'pos', content.pos),
                     size=lambda *x: setattr(self.bg_rect, 'size', content.size))

        title_bar = BoxLayout(size_hint_y=None, height=dp(40), padding=(dp(10), 0))
        with title_bar.canvas.before:
            Color(0.5, 0.1, 0.1, 1)
            self.title_rect = Rectangle(pos=title_bar.pos, size=title_bar.size)
        title_bar.bind(pos=lambda *x: setattr(self.title_rect, 'pos', title_bar.pos),
                       size=lambda *x: setattr(self.title_rect, 'size', title_bar.size))

        title_label = Label(
            text='关于',
            color=(1,1,1,1),
            halign='left',
            valign='middle',
            size_hint_x=0.8,
            font_name='Chinese'
        )
        title_bar.add_widget(title_label)

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
        title_bar.add_widget(close_btn)

        content_area = BoxLayout(orientation='vertical', padding=(dp(20), dp(15), dp(15), dp(15)), spacing=dp(5))
        with content_area.canvas.before:
            Color(1, 1, 1, 1)
            self.content_rect = Rectangle(pos=content_area.pos, size=content_area.size)
        content_area.bind(pos=lambda *x: setattr(self.content_rect, 'pos', content_area.pos),
                          size=lambda *x: setattr(self.content_rect, 'size', content_area.size))

        info_texts = [
            '应用名称：马年送祝福',
            '应用版本：' + APP_VERSION,
            '应用开发：瑾 煜',
            '反馈建议：jinyu@sjinyu.com',
            '版权所有，侵权必究！'
        ]
        for line in info_texts:
            lbl = Label(
                text=line,
                color=(0,0,0,1),
                halign='left',
                valign='middle',
                size_hint_y=None,
                height=dp(25),
                font_name='Chinese'
            )
            lbl.bind(width=lambda *x, l=lbl: setattr(l, 'text_size', (l.width, None)))
            content_area.add_widget(lbl)

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

    # ========== 版本更新 ==========
    def check_update(self, instance):
        url = 'https://www.sjinyu.com/tools/bless/data/update.json'
        show_toast('正在检查更新...')

    def on_success(req, result):
        try:
            if isinstance(result, str):
                result = json.loads(result)
        latest_version = result.get('version', '未知版本')
        message = result.get('message', '无更新说明')
        download_url = result.get('url', None)

        # 正确比较版本号
        if not is_newer_version(latest_version, APP_VERSION):
            # 已是最新版
            self.show_update_popup(latest_version, message, None, is_latest=True)
        else:
            # 有更新
            self.show_update_popup(latest_version, message, download_url, is_latest=False)
        except Exception as e:
            show_toast('解析更新信息失败')
            print('Update parse error:', e)

        def on_failure(req, result):
            show_toast('检查更新失败，请稍后重试')
            print('Update request failed:', result)

        def on_error(req, error):
            show_toast('网络连接错误')
            print('Update request error:', error)

        UrlRequest(url, on_success=on_success, on_failure=on_failure, on_error=on_error)

    def show_update_popup(self, latest_version, message, url=None, is_latest=False):
        """显示更新信息的弹窗，根据 is_latest 决定标题和按钮"""
        from kivy.uix.boxlayout import BoxLayout
        from kivy.uix.button import Button
        from kivy.uix.label import Label
        from kivy.uix.popup import Popup
        from kivy.graphics import Color, RoundedRectangle, Rectangle

        content = BoxLayout(orientation='vertical', spacing=0, padding=0,
                            size_hint=(None, None), size=(dp(320), dp(250)))
        with content.canvas.before:
            Color(1, 1, 1, 1)
            self.popup_bg = RoundedRectangle(pos=content.pos, size=content.size, radius=[dp(10)])
        content.bind(pos=lambda *x: setattr(self.popup_bg, 'pos', content.pos),
                     size=lambda *x: setattr(self.popup_bg, 'size', content.size))

        title_bar = BoxLayout(size_hint_y=None, height=dp(40), padding=(dp(10), 0))
        with title_bar.canvas.before:
            Color(0.5, 0.1, 0.1, 1)
            self.popup_title_rect = Rectangle(pos=title_bar.pos, size=title_bar.size)
        title_bar.bind(pos=lambda *x: setattr(self.popup_title_rect, 'pos', title_bar.pos),
                       size=lambda *x: setattr(self.popup_title_rect, 'size', title_bar.size))

        # 根据是否最新设置标题
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
        with content_area.canvas.before:
            Color(1, 1, 1, 1)
            self.popup_content_rect = Rectangle(pos=content_area.pos, size=content_area.size)
        content_area.bind(pos=lambda *x: setattr(self.popup_content_rect, 'pos', content_area.pos),
                          size=lambda *x: setattr(self.popup_content_rect, 'size', content_area.size))

        # 版本信息
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

        # 更新内容
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

        button_layout = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(10), padding=(dp(10),0))
        if not is_latest and url:
            download_btn = Button(
                text='立即下载',
                size_hint=(0.5, 1),
                background_color=get_color_from_hex('#4CAF50'),
                color=(1,1,1,1),
                font_name='Chinese'
            )
            download_btn.bind(on_press=lambda x: (popup.dismiss(), open_website(url)))
            button_layout.add_widget(download_btn)

        cancel_btn = Button(
            text='以后再说',
            size_hint=(0.5, 1),
            background_color=get_color_from_hex('#9E9E9E'),
            color=(1,1,1,1),
            font_name='Chinese'
        )
        cancel_btn.bind(on_press=lambda x: popup.dismiss())
        button_layout.add_widget(cancel_btn)

        if is_latest or not url:
            cancel_btn.size_hint_x = 1
            # 如果只有取消按钮，可以调整布局，这里简单处理：按钮占满
            # 但为了美观，可以移除之前添加的按钮并重新添加占满的取消按钮
            button_layout.clear_widgets()
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
        """从网络加载顶部轮播图，仅显示 active 为 true 的广告并按顺序显示"""
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
        """备用加载本地图片，文件名与服务器一致：top01.jpg ~ top05.jpg"""
        self.top_carousel.clear_widgets()
        for i in range(1, 6):
            img_path = f'images/top{i:02d}.jpg'  # 生成 top01.jpg, top02.jpg, ...
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
        """备用广告点击事件"""
        try:
            if instance.collide_point(*touch.pos):
                open_website('https://www.sjinyu.com')
        except Exception as e:
            print("on_fallback_ad_click 异常:", e)

    def on_ad_click(self, instance, touch, url):
        """点击轮播图时打开链接"""
        try:
            if instance.collide_point(*touch.pos):
                open_website(url)
        except Exception as e:
            print("on_ad_click 异常:", e)


class BlessApp(App):
    def build(self):
        Window.borderless = True
        Window.fullscreen = True
        Window.size = Window.system_size
        sm = ScreenManager()
        sm.add_widget(StartScreen(name='start'))
        sm.add_widget(MainScreen(name='main'))
        return sm

if __name__ == '__main__':
    BlessApp().run()
