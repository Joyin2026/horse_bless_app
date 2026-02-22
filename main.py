# -*- coding: utf-8 -*-
"""
main.py - 马年元宵祝福应用（最终版）
版本：v1.7.8
开发团队：卓影工作室 · 瑾 煜
功能：
- 开屏广告轮播（6秒倒计时，每1秒自动切换，用户滑动时暂停，5秒无操作后恢复）
- 节日切换（春节/元宵节/随机祝福）
- 分类切换（按钮）
- 点击复制祝福（暗红色背景 + 亮黄色文字 + Toast）
- “发给微信好友”分享最近复制的单条祝福
- 祝福语列表无限滚动（不分页）
- 关于弹窗（暗红标题栏、白色内容、圆角）
- 全屏显示，无顶部空白
"""
import kivy
import sys
import os
import traceback
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.carousel import Carousel
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.core.clipboard import Clipboard
from kivy.clock import Clock
from kivy.utils import get_color_from_hex
from kivy.core.window import Window
from kivy.metrics import dp, sp
from kivy.graphics import Color, Rectangle, RoundedRectangle

# ---------- 全局常量 ----------
APP_VERSION = "v1.7.8"

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

# ---------- 导入 jnius ----------
from jnius import autoclass
PythonActivity = autoclass('org.kivy.android.PythonActivity')
Intent = autoclass('android.content.Intent')
Toast = autoclass('android.widget.Toast')
String = autoclass('java.lang.String')
context = PythonActivity.mActivity

def show_toast(message):
    """显示 Android 原生 Toast"""
    try:
        Toast.makeText(context, String(message), Toast.LENGTH_SHORT).show()
    except Exception as e:
        print('Toast failed:', e)

def share_text(text):
    """使用 Android Intent 分享文本"""
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

# ---------- 祝福语数据 ----------
# 春节祝福语（5类，每类10条）
BLESSINGS_SPRING = {
    '深情走心': [ ... 内容省略，保持你原来的 ... ],
    '文艺唯美': [ ... ],
    '事业搞钱': [ ... ],
    '幽默搞怪': [ ... ],
    '长辈安康': [ ... ]
}

# 元宵节祝福语
BLESSINGS_LANTERN = {
    '温馨团圆': [ ... ],
    '喜庆吉利': [ ... ],
    '温柔治愈': [ ... ],
    '雅致大气': [ ... ],
    '商务得体': [ ... ]
}

# 随机祝福语
BLESSINGS_RANDOM = {
    '暖心话语': [ ... ],
    '励志金句': [ ... ],
    '幽默风趣': [ ... ],
    '唯美诗意': [ ... ],
    '简短精炼': [ ... ]
}

FESTIVALS = ['春节祝福', '元宵节祝福', '随机祝福']


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
                size=(dp(20), dp(20))
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
            bold=True
        )
        skip_btn = Button(
            text='跳过',
            size_hint=(None, None),
            size=(dp(80), dp(40)),
            background_color=get_color_from_hex('#80000000'),
            color=(1,1,1,1),
            bold=True
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


class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_festival = FESTIVALS[0]
        self.current_category = list(BLESSINGS_SPRING.keys())[0]
        self.update_category_list()
        self.selected_item = None
        self.last_copied_text = None

        main_layout = BoxLayout(orientation='vertical', spacing=0, padding=0)
        main_layout.size_hint_y = 1

        top_container = FloatLayout(size_hint_y=None, height=dp(150))
        top_img = Image(source='images/top.jpg', allow_stretch=True, keep_ratio=False,
                        size_hint=(1,1), pos_hint={'x':0,'y':0})
        top_container.add_widget(top_img)
        main_layout.add_widget(top_container)

        festival_layout = BoxLayout(size_hint=(1, None), height=dp(50), spacing=dp(2))
        self.spring_btn = Button(
            text='春节祝福',
            background_color=get_color_from_hex('#DAA520'),
            color=(1,1,1,1),
            bold=True
        )
        self.spring_btn.bind(on_press=lambda x: self.switch_festival('春节祝福'))
        self.lantern_btn = Button(
            text='元宵节祝福',
            background_color=get_color_from_hex('#8B4513'),
            color=(1,1,1,1),
            bold=True
        )
        self.lantern_btn.bind(on_press=lambda x: self.switch_festival('元宵节祝福'))
        self.random_btn = Button(
            text='随机祝福',
            background_color=get_color_from_hex('#8B4513'),
            color=(1,1,1,1),
            bold=True
        )
        self.random_btn.bind(on_press=lambda x: self.switch_festival('随机祝福'))
        festival_layout.add_widget(self.spring_btn)
        festival_layout.add_widget(self.lantern_btn)
        festival_layout.add_widget(self.random_btn)
        main_layout.add_widget(festival_layout)

        self.category_layout = BoxLayout(size_hint=(1, None), height=dp(50), spacing=dp(2))
        self.update_category_buttons()
        main_layout.add_widget(self.category_layout)

        self.scroll_view = ScrollView()
        self.scroll_view.size_hint_y = 1
        self.list_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(8))
        self.list_layout.bind(minimum_height=self.list_layout.setter('height'))
        self.scroll_view.add_widget(self.list_layout)
        main_layout.add_widget(self.scroll_view)

        bottom_layout = BoxLayout(size_hint=(1, None), height=dp(50), spacing=dp(8))
        share_btn = Button(
            text='发给微信好友',
            background_color=get_color_from_hex('#4CAF50'),
            color=(1,1,1,1)
        )
        share_btn.bind(on_press=self.share_blessings)
        bottom_layout.add_widget(share_btn)
        main_layout.add_widget(bottom_layout)

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
            bold=True
        )
        copyright_btn.bind(on_press=self.show_about_popup)
        status_bar.add_widget(copyright_btn)
        main_layout.add_widget(status_bar)

        self.add_widget(main_layout)
        self.show_current_page()

    def update_category_buttons(self):
        self.category_layout.clear_widgets()
        if self.current_festival == '春节祝福':
            categories = list(BLESSINGS_SPRING.keys())
        elif self.current_festival == '元宵节祝福':
            categories = list(BLESSINGS_LANTERN.keys())
        else:
            categories = list(BLESSINGS_RANDOM.keys())

        for cat in categories:
            btn = Button(
                text=cat,
                size_hint_x=1/len(categories),
                background_color=get_color_from_hex('#DAA520' if cat == self.current_category else '#8B4513'),
                color=(1,1,1,1)
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

    def switch_festival(self, festival):
        if festival == self.current_festival:
            return
        self.current_festival = festival

        if festival == '春节祝福':
            self.spring_btn.background_color = get_color_from_hex('#DAA520')
            self.lantern_btn.background_color = get_color_from_hex('#8B4513')
            self.random_btn.background_color = get_color_from_hex('#8B4513')
        elif festival == '元宵节祝福':
            self.spring_btn.background_color = get_color_from_hex('#8B4513')
            self.lantern_btn.background_color = get_color_from_hex('#DAA520')
            self.random_btn.background_color = get_color_from_hex('#8B4513')
        else:
            self.spring_btn.background_color = get_color_from_hex('#8B4513')
            self.lantern_btn.background_color = get_color_from_hex('#8B4513')
            self.random_btn.background_color = get_color_from_hex('#DAA520')

        self.update_category_list()
        self.current_category = self.category_list[0]
        self.update_category_buttons()
        self.show_current_page()

    def update_category_list(self):
        if self.current_festival == '春节祝福':
            self.category_list = list(BLESSINGS_SPRING.keys())
        elif self.current_festival == '元宵节祝福':
            self.category_list = list(BLESSINGS_LANTERN.keys())
        else:
            self.category_list = list(BLESSINGS_RANDOM.keys())

    def get_current_blessings_dict(self):
        if self.current_festival == '春节祝福':
            return BLESSINGS_SPRING
        elif self.current_festival == '元宵节祝福':
            return BLESSINGS_LANTERN
        else:
            return BLESSINGS_RANDOM

    def show_current_page(self):
        self.list_layout.clear_widgets()
        blessings_dict = self.get_current_blessings_dict()
        blessings = blessings_dict[self.current_category]
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
                padding=(dp(10), dp(5))
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

        title_label = Label(text='关于', color=(1,1,1,1),
                            halign='left', valign='middle', size_hint_x=0.8)
        title_bar.add_widget(title_label)

        close_btn = Button(text='X', size_hint=(None, None), size=(dp(30), dp(30)),
                           pos_hint={'right':1, 'center_y':0.5},
                           background_color=(0,0,0,0), color=(1,1,1,1), bold=True)
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
            lbl = Label(text=line, color=(0,0,0,1),
                        halign='left', valign='middle', size_hint_y=None, height=dp(25))
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
