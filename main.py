# -*- coding: utf-8 -*-
"""
main.py - 马年元宵祝福应用
版本：v1.0.9
开发团队：卓影工作室 · 瑾 煜
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
from kivy.uix.spinner import Spinner
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.core.clipboard import Clipboard
from kivy.clock import Clock
from kivy.utils import get_color_from_hex
from kivy.core.window import Window
from kivy.metrics import dp, sp
from kivy.graphics import Color, Rectangle
from kivy.core.text import LabelBase

# ---------- 注册中文字体 ----------
# 假设字体文件放在 fonts/chinese.ttf
LabelBase.register(name='Chinese', fn_regular='fonts/chinese.ttf')

# 创建支持中文的标签类
class ChineseLabel(Label):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.font_name = 'Chinese'

# 全局异常捕获
def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    try:
        log_path = os.path.join(os.getenv('EXTERNAL_STORAGE', '/sdcard'), 'crash.log')
        with open(log_path, 'a') as f:
            f.write(''.join(traceback.format_exception(exc_type, exc_value, exc_traceback)))
    except:
        pass

sys.excepthook = handle_exception

Window.clearcolor = get_color_from_hex('#FFF5E6')

# ---------- 导入plyer和pyjnius ----------
try:
    from plyer import toast
except ImportError:
    toast = None

try:
    from jnius import autoclass
    PythonActivity = autoclass('org.kivy.android.PythonActivity')
    Intent = autoclass('android.content.Intent')
    Uri = autoclass('android.net.Uri')
    context = PythonActivity.mActivity
    share_available = True
except Exception:
    share_available = False

# 祝福语数据（完整，此处省略以节省篇幅，请从之前版本复制）
# 请确保完整复制之前的 BLESSINGS_SPRING 和 BLESSINGS_LANTERN 数据
# 为保持代码可读性，这里仅保留框架，实际使用时必须包含所有100条祝福语
BLESSINGS_SPRING = {
    '幽默搞怪': [ ... ],
    '深情走心': [ ... ],
    '文艺唯美': [ ... ],
    '事业搞钱': [ ... ],
    '长辈安康': [ ... ]
}
BLESSINGS_LANTERN = {
    '温馨团圆·家人亲友': [ ... ],
    '喜庆吉利·通用祝福': [ ... ],
    '温柔治愈·走心文艺': [ ... ],
    '雅致大气·高级文案': [ ... ],
    '商务得体·职场祝福': [ ... ]
}
FESTIVALS = ['春节祝福', '元宵节祝福']


class StartScreen(Screen):
    """可滑动开屏广告页"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = FloatLayout()

        # 轮播图片列表
        splash_images = ['images/splash1.png', 'images/splash2.png', 'images/splash3.png']
        self.carousel = Carousel(direction='right', loop=True)
        for img_path in splash_images:
            img = Image(source=img_path, allow_stretch=True, keep_ratio=False)
            self.carousel.add_widget(img)
        self.carousel.bind(current_slide=self.on_slide_changed)
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
            lbl = ChineseLabel(text='○', font_size=sp(20), color=(1,1,1,1),
                               size_hint=(None, None), size=(dp(20), dp(20)))
            self.indicators.append(lbl)
            indicator_layout.add_widget(lbl)
        self.update_indicator(0)
        layout.add_widget(indicator_layout)

        # 跳过按钮
        skip_btn = Button(
            text='跳过',
            size_hint=(None, None),
            size=(dp(80), dp(40)),
            pos_hint={'right': 1, 'top': 1},
            background_color=get_color_from_hex('#80000000'),
            color=(1,1,1,1),
            bold=True,
            font_name='Chinese'
        )
        skip_btn.bind(on_press=self.skip_to_main)
        layout.add_widget(skip_btn)

        # 倒计时标签
        self.countdown_label = ChineseLabel(
            text='3 秒',
            size_hint=(None, None),
            size=(dp(80), dp(30)),
            pos_hint={'right': 1, 'top': 0.9},
            color=(1,1,1,1),
            bold=True
        )
        layout.add_widget(self.countdown_label)

        self.add_widget(layout)

        self.countdown = 3
        self.update_countdown()
        Clock.schedule_interval(self.update_countdown, 1)
        Clock.schedule_once(self.go_main, 3)

    def update_countdown(self, dt=None):
        if self.countdown > 0:
            self.countdown_label.text = f'{self.countdown} 秒'
            self.countdown -= 1
        else:
            self.countdown_label.text = '进入'
            return False

    def on_slide_changed(self, carousel, index):
        self.update_indicator(index)

    def update_indicator(self, index):
        for i, lbl in enumerate(self.indicators):
            lbl.text = '●' if i == index else '○'

    def skip_to_main(self, instance):
        Clock.unschedule(self.update_countdown)
        Clock.unschedule(self.go_main)
        self.manager.current = 'main'

    def go_main(self, *args):
        self.manager.current = 'main'


class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_festival = FESTIVALS[0]
        self.current_category = list(BLESSINGS_SPRING.keys())[0]
        self.current_page = 0
        self.total_pages = 2
        self.update_category_list()

        main_layout = BoxLayout(orientation='vertical', spacing=0, padding=0)

        # 顶部图片
        top_container = FloatLayout(size_hint_y=None, height=dp(200))
        top_img = Image(source='images/top.jpg', allow_stretch=True, keep_ratio=False,
                        size_hint=(1,1), pos_hint={'x':0,'y':0})
        top_container.add_widget(top_img)
        main_layout.add_widget(top_container)

        # 节日切换按钮
        festival_layout = BoxLayout(size_hint=(1, None), height=dp(50), spacing=0)
        self.spring_btn = Button(text='春节祝福', background_color=get_color_from_hex('#DAA520'),
                                  color=(1,1,1,1), bold=True, font_name='Chinese')
        self.spring_btn.bind(on_press=lambda x: self.switch_festival('春节祝福'))
        self.lantern_btn = Button(text='元宵节祝福', background_color=get_color_from_hex('#8B4513'),
                                   color=(1,1,1,1), bold=True, font_name='Chinese')
        self.lantern_btn.bind(on_press=lambda x: self.switch_festival('元宵节祝福'))
        festival_layout.add_widget(self.spring_btn)
        festival_layout.add_widget(self.lantern_btn)
        main_layout.add_widget(festival_layout)

        # 分类 Spinner（注意 Spinner 的文本不支持直接设置字体，但可以通过 style 或 kv 语言，这里用默认）
        self.category_spinner = Spinner(
            text=self.current_category,
            values=self.category_list,
            size_hint=(1, None),
            height=dp(45),
            background_color=get_color_from_hex('#8B4513'),
            color=(1,1,1,1)
        )
        self.category_spinner.bind(text=self.on_category_change)
        main_layout.add_widget(self.category_spinner)

        # 翻页区域
        page_layout = BoxLayout(size_hint=(1, None), height=dp(40), spacing=0)
        self.prev_btn = Button(text='上一页', on_press=self.prev_page, disabled=True, font_name='Chinese')
        self.page_label = ChineseLabel(text='第1页/共2页', color=(0.2,0.2,0.2,1))
        self.next_btn = Button(text='下一页', on_press=self.next_page, font_name='Chinese')
        page_layout.add_widget(self.prev_btn)
        page_layout.add_widget(self.page_label)
        page_layout.add_widget(self.next_btn)
        main_layout.add_widget(page_layout)

        # 祝福语列表
        self.scroll_view = ScrollView()
        self.list_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(2))
        self.list_layout.bind(minimum_height=self.list_layout.setter('height'))
        self.scroll_view.add_widget(self.list_layout)
        main_layout.add_widget(self.scroll_view)

        # 底部功能按钮
        bottom_buttons = BoxLayout(size_hint=(1, None), height=dp(50), spacing=0)
        send_btn = Button(text='发送祝福', background_color=get_color_from_hex('#DAA520'),
                          color=(1,1,1,1), font_name='Chinese')
        send_btn.bind(on_press=self.send_blessings)
        share_btn = Button(text='发给微信好友', background_color=get_color_from_hex('#4CAF50'),
                           color=(1,1,1,1), font_name='Chinese')
        share_btn.bind(on_press=self.share_blessings)
        bottom_buttons.add_widget(send_btn)
        bottom_buttons.add_widget(share_btn)
        main_layout.add_widget(bottom_buttons)

        # 底部状态栏（版权信息，可点击）
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
        else:
            self.spring_btn.background_color = get_color_from_hex('#8B4513')
            self.lantern_btn.background_color = get_color_from_hex('#DAA520')
        self.update_category_list()
        self.category_spinner.values = self.category_list
        self.current_category = self.category_list[0]
        self.category_spinner.text = self.current_category
        self.current_page = 0
        self.update_page_buttons()
        self.show_current_page()

    def update_category_list(self):
        if self.current_festival == '春节祝福':
            self.category_list = list(BLESSINGS_SPRING.keys())
        else:
            self.category_list = list(BLESSINGS_LANTERN.keys())

    def get_current_blessings_dict(self):
        if self.current_festival == '春节祝福':
            return BLESSINGS_SPRING
        else:
            return BLESSINGS_LANTERN

    def on_category_change(self, spinner, text):
        self.current_category = text
        self.current_page = 0
        self.update_page_buttons()
        self.show_current_page()

    def show_current_page(self):
        self.list_layout.clear_widgets()
        blessings_dict = self.get_current_blessings_dict()
        blessings = blessings_dict[self.current_category]
        start = self.current_page * 5
        end = min(start + 5, len(blessings))
        page_items = blessings[start:end]

        for text in page_items:
            item_box = BoxLayout(orientation='horizontal', size_hint_y=None, spacing=0)
            with item_box.canvas.before:
                Color(1, 1, 1, 0.9)
                self.rect = Rectangle(size=item_box.size, pos=item_box.pos)
            item_box.bind(size=self._update_item_rect, pos=self._update_item_rect)

            label = ChineseLabel(
                text=text,
                size_hint_x=0.8,
                size_hint_y=None,
                halign='left',
                valign='top',
                color=(0.1,0.1,0.1,1),
                markup=True
            )
            label.bind(
                width=lambda *x, lbl=label: lbl.setter('text_size')(lbl, (lbl.width, None)),
                texture_size=lambda *x, lbl=label: setattr(lbl, 'height', lbl.texture_size[1] + dp(8))
            )
            copy_btn = Button(
                text='📋',
                size_hint_x=0.2,
                size_hint_y=None,
                height=dp(40),
                background_normal='',
                background_color=(0.2,0.6,1,1),
                font_name='Chinese'
            )
            copy_btn.bind(on_press=lambda btn, t=text: self.copy_to_clipboard(t))

            item_box.add_widget(label)
            item_box.add_widget(copy_btn)
            label.bind(height=lambda *x, box=item_box: setattr(box, 'height', label.height + dp(8)))
            self.list_layout.add_widget(item_box)

    def _update_item_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def copy_to_clipboard(self, text):
        Clipboard.copy(text)
        if toast:
            toast('已复制')
        else:
            print('复制成功:', text)

    def prev_page(self, instance):
        if self.current_page > 0:
            self.current_page -= 1
            self.update_page_buttons()
            self.show_current_page()

    def next_page(self, instance):
        if self.current_page < self.total_pages - 1:
            self.current_page += 1
            self.update_page_buttons()
            self.show_current_page()

    def update_page_buttons(self):
        self.prev_btn.disabled = (self.current_page == 0)
        self.next_btn.disabled = (self.current_page == self.total_pages - 1)
        self.page_label.text = f'第{self.current_page+1}页/共{self.total_pages}页'

    def send_blessings(self, instance):
        blessings_dict = self.get_current_blessings_dict()
        blessings = blessings_dict[self.current_category]
        start = self.current_page * 5
        end = min(start + 5, len(blessings))
        page_items = blessings[start:end]
        full_text = '\n---\n'.join(page_items)
        Clipboard.copy(full_text)
        if toast:
            toast('已复制当前页所有祝福')
        else:
            print('复制当前页所有祝福:\n', full_text)

    def share_blessings(self, instance):
        """使用 Android Intent 分享文本"""
        blessings_dict = self.get_current_blessings_dict()
        blessings = blessings_dict[self.current_category]
        start = self.current_page * 5
        end = min(start + 5, len(blessings))
        page_items = blessings[start:end]
        full_text = '\n---\n'.join(page_items)

        if share_available:
            try:
                intent = Intent()
                intent.setAction(Intent.ACTION_SEND)
                intent.putExtra(Intent.EXTRA_TEXT, full_text)
                intent.setType('text/plain')
                # 指定分享到微信（可选）
                # intent.setPackage('com.tencent.mm')
                context.startActivity(Intent.createChooser(intent, '分享到'))
                if toast:
                    toast('分享已启动')
            except Exception as e:
                if toast:
                    toast('分享失败')
                print('分享失败:', e)
        else:
            Clipboard.copy(full_text)
            if toast:
                toast('分享功能不可用，已复制到剪贴板')

    def show_about_popup(self, instance):
        content = BoxLayout(orientation='vertical', spacing=dp(10), padding=dp(20))
        content.add_widget(ChineseLabel(
            text='马年祝福APP\n版本：v1.0.9\n开发团队：卓影工作室 · 瑾 煜',
            halign='center',
            valign='middle',
            size_hint_y=None,
            height=dp(120)
        ))
        close_btn = Button(text='关闭', size_hint=(None, None), size=(dp(100), dp(40)), font_name='Chinese')
        close_btn.bind(on_press=lambda x: popup.dismiss())
        content.add_widget(close_btn)

        popup = Popup(
            title='关于',
            title_font='Chinese',
            content=content,
            size_hint=(0.8, 0.4),
            auto_dismiss=False
        )
        popup.open()


class BlessApp(App):
    def build(self):
        Window.size = (1440, 3200)
        sm = ScreenManager()
        sm.add_widget(StartScreen(name='start'))
        sm.add_widget(MainScreen(name='main'))
        return sm


if __name__ == '__main__':
    BlessApp().run()
