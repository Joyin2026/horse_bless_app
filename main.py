# -*- coding: utf-8 -*-
"""
main.py - 马年送祝福（最终版）
版本：v2.0.0
开发团队：卓影工作室 · 瑾 煜
功能：
- 开屏广告轮播
- 两个固定标题的下拉菜单（传统佳节/行业节日），小标签显示当前选中节日
- 自动判断默认节日（元宵节提前8天，其他5天）
- 祝福语数据从 data/bless.json 加载，并在界面显示加载状态
- 修复下拉菜单乱码，添加加载失败提示
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
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.core.clipboard import Clipboard
from kivy.clock import Clock
from kivy.utils import get_color_from_hex
from kivy.core.window import Window
from kivy.metrics import dp, sp
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.core.text import LabelBase

APP_VERSION = "v2.0.0"

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

# ==================== 自定义 Spinner 选项（解决乱码）====================
class ChineseSpinnerOption(SpinnerOption):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.font_name = 'Chinese'

Spinner.option_cls = ChineseSpinnerOption

# ==================== 加载祝福语数据 ====================
def load_blessings():
    import os
    base_dir = os.path.dirname(__file__)
    json_path = os.path.join(base_dir, 'data', 'bless.json')
    # 为了在界面上显示错误，我们返回一个元组 (data, error_message)
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        # 验证数据结构是否包含节日和分类
        if not isinstance(data, dict):
            return {}, "数据格式错误：根节点不是字典"
        if len(data) == 0:
            return {}, "数据为空"
        # 可选：检查第一个节日的结构
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

# 加载数据，同时获取错误信息
ALL_BLESSINGS, load_error = load_blessings()

# 节日分组
TRADITIONAL = ['春节', '元宵节', '端午节', '中秋节']
PROFESSIONAL = ['护士节', '母亲节', '父亲节', '建军节', '教师节', '国庆节', '记者节']

# 2026年节日日期
FESTIVAL_DATES_2026 = {
    '春节': (2, 17),
    '元宵节（正月十五）': (3, 3),
    '端午节（五月初五）': (6, 19),
    '中秋节（八月十五）': (9, 25),
    '护士节（5月12日）': (5, 12),
    '母亲节（5月10日）': (5, 10),
    '父亲节（6月21日）': (6, 21),
    '建军节（8月1日）': (8, 1),
    '教师节（9月10日）': (9, 10),
    '国庆节（10月1日）': (10, 1),
    '记者节（11月8日）': (11, 8),
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

        main_layout = BoxLayout(orientation='vertical', spacing=0, padding=0)
        main_layout.size_hint_y = 1

        # 顶部图片
        top_container = FloatLayout(size_hint_y=None, height=dp(150))
        top_img = Image(source='images/top.jpg', allow_stretch=True, keep_ratio=False,
                        size_hint=(1,1), pos_hint={'x':0,'y':0})
        top_container.add_widget(top_img)
        main_layout.add_widget(top_container)
       
        # 两个并排的下拉菜单（固定标题）
        spinner_layout = BoxLayout(size_hint=(1, None), height=dp(50), spacing=dp(5))
        self.traditional_spinner = Spinner(
            text='传统佳节',
            values=TRADITIONAL,
            size_hint=(0.5, 1),
            background_color=get_color_from_hex('#DAA520'),
            color=(1,1,1,1),
            font_name='Chinese'
        )
        self.traditional_spinner.bind(text=self.on_traditional_spinner_select)
        self.professional_spinner = Spinner(
            text='行业节日',
            values=PROFESSIONAL,
            size_hint=(0.5, 1),
            background_color=get_color_from_hex('#8B4513'),
            color=(1,1,1,1),
            font_name='Chinese'
        )
        self.professional_spinner.bind(text=self.on_professional_spinner_select)
        spinner_layout.add_widget(self.traditional_spinner)
        spinner_layout.add_widget(self.professional_spinner)
        main_layout.add_widget(spinner_layout)

        # 当前选中节日的小标签
        self.current_festival_label = Label(
            text=f"当前节日：{self.current_festival}",
            size_hint=(1, None),
            height=dp(30),
            color=(0.5,0.1,0.1,1),
            font_name='Chinese',
            halign='center'
        )
        main_layout.add_widget(self.current_festival_label)

        # 分类切换按钮（横向滚动）
        self.category_scroll = ScrollView(size_hint=(1, None), height=dp(50), do_scroll_x=True, do_scroll_y=False)
        self.category_layout = BoxLayout(size_hint_x=None, height=dp(50), spacing=dp(2))
        self.category_layout.bind(minimum_width=self.category_layout.setter('width'))
        self.category_scroll.add_widget(self.category_layout)
        main_layout.add_widget(self.category_scroll)

        # 祝福语列表
        self.scroll_view = ScrollView()
        self.scroll_view.size_hint_y = 1
        self.list_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(8))
        self.list_layout.bind(minimum_height=self.list_layout.setter('height'))
        self.scroll_view.add_widget(self.list_layout)
        main_layout.add_widget(self.scroll_view)

        # 底部功能按钮
        bottom_layout = BoxLayout(size_hint=(1, None), height=dp(50), spacing=dp(8))
        share_btn = Button(
            text='发给微信好友',
            background_color=get_color_from_hex('#4CAF50'),
            color=(1,1,1,1),
            font_name='Chinese'
        )
        share_btn.bind(on_press=self.share_blessings)
        bottom_layout.add_widget(share_btn)
        main_layout.add_widget(bottom_layout)

        # 底部状态栏
        status_bar = BoxLayout(size_hint=(1, None), height=dp(30), padding=0)
        with status_bar.canvas.before:
            Color(0.2, 0.2, 0.2, 1)
            self.status_rect = Rectangle(size=status_bar.size, pos=status_bar.pos)
        status_bar.bind(size=self._update_status_rect, pos=self._update_status_rect)
        copyright_btn = Button(
            text='Copyright © 2026 卓影工作室·瑾煜. All Rights Reserved',
            color=get_color_from_hex('#DAA520'),
            font_size=sp(8),
            background_color=(0,0,0,0),
            bold=True,
            font_name='Chinese'
        )
        copyright_btn.bind(on_press=self.show_about_popup)
        status_bar.add_widget(copyright_btn)
        main_layout.add_widget(status_bar)

        self.add_widget(main_layout)
        self.update_category_buttons()
        self.show_current_page()

    def on_traditional_spinner_select(self, spinner, text):
        self.current_festival = text
        self.current_festival_label.text = f"当前节日：{self.current_festival}"
        festival_data = ALL_BLESSINGS.get(self.current_festival, {})
        self.current_category = list(festival_data.keys())[0] if festival_data else ''
        self.update_category_buttons()
        self.show_current_page()

    def on_professional_spinner_select(self, spinner, text):
        self.current_festival = text
        self.current_festival_label.text = f"当前节日：{self.current_festival}"
        festival_data = ALL_BLESSINGS.get(self.current_festival, {})
        self.current_category = list(festival_data.keys())[0] if festival_data else ''
        self.update_category_buttons()
        self.show_current_page()

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

    def _update_status_rect(self, instance, value):
        self.status_rect.pos = instance.pos
        self.status_rect.size = instance.size

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

    def on_copy(self, instance):
        text = instance.blessing_text
        Clipboard.copy(text)
        self.last_copied_text = text
        show_toast('祝福语已复制')
        if self.selected_item and self.selected_item != instance:
            self.selected_item.background_color = self.selected_item.default_bg_color
            self.selected_item.color = (0.1, 0.1, 0.1, 1)
        instance.background_color = (0.5, 0.1, 0.1, 1)
        instance.color = (1, 1, 0, 1)
        self.selected_item = instance

    def share_blessings(self, instance):
        if self.last_copied_text:
            if share_text(self.last_copied_text):
                show_toast('分享已启动')
            else:
                Clipboard.copy(self.last_copied_text)
                show_toast('分享失败，已复制到剪贴板')
        else:
            show_toast('请先选择一条祝福')

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
            '反馈建议：contactme@sjinyu.com',
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


