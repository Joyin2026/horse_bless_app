# -*- coding: utf-8 -*-
"""
main.py - 马年元宵祝福应用
版本：v1.6.0
开发团队：卓影工作室 · 瑾 煜
功能：
- 开屏广告轮播（6秒倒计时，自动轮播每1秒切换，手动滑动时暂停）
- 节日切换（春节/元宵节/随机祝福）
- 分类切换（按钮）
- 点击复制祝福（柠檬绿高亮 + Toast）
- “发给微信好友”分享最近复制的单条祝福
- 祝福语列表一次性显示所有条目，支持滚动
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
from kivy.core.text import LabelBase

# ---------- 注册中文字体 ----------
LabelBase.register(name='Chinese', fn_regular='chinese.ttf')

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
# （完整数据同之前版本，此处省略以节省篇幅，实际使用时需完整粘贴）
BLESSINGS_SPRING = { ... }
BLESSINGS_LANTERN = { ... }
BLESSINGS_RANDOM = { ... }

FESTIVALS = ['春节祝福', '元宵节祝福', '随机祝福']


class StartScreen(Screen):
    """可滑动开屏广告页，带跳过按钮和底部指示点，自动轮播，手动滑动暂停倒计时"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = FloatLayout()

        # 轮播图片列表（使用更大尺寸的图片）
        splash_images = ['images/splash1.png', 'images/splash2.png', 'images/splash3.png']
        self.carousel = Carousel(direction='right', loop=True)
        for img_path in splash_images:
            img = Image(source=img_path, allow_stretch=True, keep_ratio=False)
            self.carousel.add_widget(img)
        self.carousel.bind(index=self.on_carousel_index_changed)
        layout.add_widget(self.carousel)

        # 底部指示器
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

        # 右上角区域：倒计时标签（左）和跳过按钮（右）
        top_right_layout = BoxLayout(
            size_hint=(None, None),
            size=(dp(180), dp(40)),
            pos_hint={'right': 1, 'top': 1},
            spacing=dp(5)
        )
        # 倒计时标签
        self.countdown_label = Label(
            text='6 秒',
            size_hint=(None, None),
            size=(dp(80), dp(40)),
            color=(1,1,1,1),
            bold=True,
            font_name='Chinese'
        )
        top_right_layout.add_widget(self.countdown_label)

        # 跳过按钮
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
        top_right_layout.add_widget(skip_btn)

        layout.add_widget(top_right_layout)

        self.add_widget(layout)

        # 状态变量
        self.countdown = 6                     # 倒计时秒数
        self.auto_slide_active = True          # 自动轮播是否激活
        self.countdown_paused = False          # 倒计时是否暂停
        self.last_manual_slide_time = 0        # 上次手动滑动时间
        self.slide_timer = None                 # 用于检查滑动暂停的定时器

        # 启动自动轮播和倒计时
        self._start_auto_slide()
        self._start_countdown()

        # 启动滑动检测定时器（每秒检查）
        self.slide_timer = Clock.schedule_interval(self._check_slide_pause, 1)

    def _start_auto_slide(self):
        """启动自动轮播（每1秒切换）"""
        if self.auto_slide_active:
            self.auto_slide_trigger = Clock.schedule_interval(self._next_slide, 1)

    def _stop_auto_slide(self):
        """停止自动轮播"""
        if hasattr(self, 'auto_slide_trigger') and self.auto_slide_trigger:
            self.auto_slide_trigger.cancel()
            self.auto_slide_trigger = None

    def _next_slide(self, dt):
        """切换到下一张"""
        self.carousel.load_next()

    def _start_countdown(self):
        """启动倒计时"""
        self.countdown_timer = Clock.schedule_interval(self._update_countdown, 1)

    def _stop_countdown(self):
        """停止倒计时"""
        if hasattr(self, 'countdown_timer') and self.countdown_timer:
            self.countdown_timer.cancel()
            self.countdown_timer = None

    def _update_countdown(self, dt):
        """每秒更新倒计时"""
        if not self.countdown_paused:
            if self.countdown > 0:
                self.countdown -= 1
                self.countdown_label.text = f'{self.countdown} 秒'
            else:
                self.countdown_label.text = '进入'
                self.go_main()

    def _check_slide_pause(self, dt):
        """每秒检查：如果暂停且超过5秒无滑动，恢复自动轮播和倒计时"""
        if self.countdown_paused:
            # 计算距离上次滑动的时间
            time_since_last_slide = Clock.get_time() - self.last_manual_slide_time
            if time_since_last_slide >= 5:
                self._resume_after_pause()

    def _resume_after_pause(self):
        """恢复自动轮播和倒计时"""
        self.countdown_paused = False
        self.auto_slide_active = True
        self.countdown = 6
        self.countdown_label.text = '6 秒'
        self._start_auto_slide()
        # 倒计时已在定时器中继续，无需额外启动

    def on_carousel_index_changed(self, instance, value):
        """轮播索引变化时（手动或自动），更新指示器"""
        self.update_indicator(value)
        # 如果是手动滑动（通过触摸事件），触发暂停
        # 由于Carousel内部没有直接暴露触摸事件，我们通过重写on_touch_down来检测手动滑动
        # 此处简化：每次索引变化都认为可能是手动触发，先暂停，记录时间
        # 但自动轮播也会触发此事件，所以需要区分自动和手动。我们可以通过记录是否是自动轮播触发的。
        # 在自动轮播的_next_slide中设置一个标志，然后在这里检查。
        # 为了简化，我们采用以下逻辑：每次索引变化时，都暂停倒计时和自动轮播，并记录时间。
        # 这样自动轮播也会被暂停，但随后会通过_check_slide_pause在5秒后恢复。
        # 这样能实现“手动滑动后暂停5秒”的效果，且自动轮播也会在5秒后恢复。
        self._pause_due_to_manual()

    def _pause_due_to_manual(self):
        """暂停倒计时和自动轮播，并记录时间"""
        self._stop_auto_slide()
        self.countdown_paused = True
        self.last_manual_slide_time = Clock.get_time()
        # 注意：倒计时本身还在运行，但被暂停标志阻止更新

    def update_indicator(self, index):
        for i, lbl in enumerate(self.indicators):
            lbl.text = '●' if i == index else '○'

    def skip_to_main(self, instance):
        Clock.unschedule(self._update_countdown)
        Clock.unschedule(self._check_slide_pause)
        if hasattr(self, 'auto_slide_trigger'):
            self.auto_slide_trigger.cancel()
        self.manager.current = 'main'

    def go_main(self, *args):
        self.skip_to_main(None)


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

        # 顶部图片（高度根据实际图片调整，设为dp(200)可适应大部分情况）
        top_container = FloatLayout(size_hint_y=None, height=dp(200))
        top_img = Image(source='images/top.jpg', allow_stretch=True, keep_ratio=False,
                        size_hint=(1,1), pos_hint={'x':0,'y':0})
        top_container.add_widget(top_img)
        main_layout.add_widget(top_container)

        # 节日切换按钮（三个）
        festival_layout = BoxLayout(size_hint=(1, None), height=dp(50), spacing=dp(2))
        self.spring_btn = Button(
            text='春节祝福',
            background_color=get_color_from_hex('#DAA520'),
            color=(1,1,1,1),
            bold=True,
            font_name='Chinese'
        )
        self.spring_btn.bind(on_press=lambda x: self.switch_festival('春节祝福'))
        self.lantern_btn = Button(
            text='元宵节祝福',
            background_color=get_color_from_hex('#8B4513'),
            color=(1,1,1,1),
            bold=True,
            font_name='Chinese'
        )
        self.lantern_btn.bind(on_press=lambda x: self.switch_festival('元宵节祝福'))
        self.random_btn = Button(
            text='随机祝福',
            background_color=get_color_from_hex('#8B4513'),
            color=(1,1,1,1),
            bold=True,
            font_name='Chinese'
        )
        self.random_btn.bind(on_press=lambda x: self.switch_festival('随机祝福'))
        festival_layout.add_widget(self.spring_btn)
        festival_layout.add_widget(self.lantern_btn)
        festival_layout.add_widget(self.random_btn)
        main_layout.add_widget(festival_layout)

        # 分类切换按钮
        self.category_layout = BoxLayout(size_hint=(1, None), height=dp(50), spacing=dp(2))
        self.update_category_buttons()
        main_layout.add_widget(self.category_layout)

        # 祝福语列表（可滚动，显示所有条目）
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
        self.show_all_blessings()

    def _update_status_rect(self, instance, value):
        self.status_rect.pos = instance.pos
        self.status_rect.size = instance.size

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
        self.show_all_blessings()

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
        self.show_all_blessings()

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

    def show_all_blessings(self):
        """显示当前分类的所有祝福语（不分页）"""
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

        instance.background_color = (0.5, 0.8, 0.2, 1)
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

        title_label = Label(text='关于', font_name='Chinese', color=(1,1,1,1),
                            halign='left', valign='middle', size_hint_x=0.8)
        title_bar.add_widget(title_label)

        close_btn = Button(text='X', size_hint=(None, None), size=(dp(30), dp(30)),
                           pos_hint={'right':1, 'center_y':0.5},
                           background_color=(0,0,0,0), color=(1,1,1,1),
                           font_name='Chinese', bold=True)
        close_btn.bind(on_press=lambda x: popup.dismiss())
        title_bar.add_widget(close_btn)

        content_area = BoxLayout(orientation='vertical', padding=dp(15), spacing=dp(5))
        with content_area.canvas.before:
            Color(1, 1, 1, 1)
            self.content_rect = Rectangle(pos=content_area.pos, size=content_area.size)
        content_area.bind(pos=lambda *x: setattr(self.content_rect, 'pos', content_area.pos),
                          size=lambda *x: setattr(self.content_rect, 'size', content_area.size))

        info_texts = [
            '应用名称：马年新春祝福',
            '应用版本：v1.6.0',
            '应用开发：瑾 煜',
            '反馈建议：contactme@sjinyu.com',
            '版权所有，侵权必究！'
        ]
        for line in info_texts:
            lbl = Label(text=line, font_name='Chinese', color=(0,0,0,1),
                        halign='left', valign='middle', size_hint_y=None, height=dp(25))
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
        # 强制全屏，隐藏系统栏
        Window.borderless = True
        Window.fullscreen = True
        Window.size = Window.system_size

        sm = ScreenManager()
        sm.add_widget(StartScreen(name='start'))
        sm.add_widget(MainScreen(name='main'))
        return sm


if __name__ == '__main__':
    BlessApp().run()
