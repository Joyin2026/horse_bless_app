# -*- coding: utf-8 -*-
"""
main.py - 马年元宵祝福应用（最终版）
版本：v1.7.2
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
- 首次使用引导（四步气泡，可选不再显示）
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
from kivy.uix.checkbox import CheckBox
from kivy.core.clipboard import Clipboard
from kivy.clock import Clock
from kivy.utils import get_color_from_hex
from kivy.core.window import Window
from kivy.metrics import dp, sp
from kivy.graphics import Color, Rectangle, RoundedRectangle
from kivy.core.text import LabelBase
from kivy.storage.jsonstore import JsonStore

# ---------- 全局常量 ----------
APP_VERSION = "1.7.2"   # 更新版本号

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
    """使用 Android Intent 分享文本（添加标志优化返回行为）"""
    try:
        intent = Intent()
        intent.setAction(Intent.ACTION_SEND)
        intent.putExtra(Intent.EXTRA_TEXT, String(text))
        intent.setType('text/plain')
        # 添加 NEW_TASK 标志，有助于返回时恢复原应用
        intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
        context.startActivity(Intent.createChooser(intent, String('分享到')))
        return True
    except Exception as e:
        print('Share failed:', e)
        return False

# ---------- 祝福语数据（与您之前的 Emoji 版完全相同，此处省略以节省篇幅，实际使用时请保留）----------
# 为保持代码简洁，此处省略 BLESSINGS_SPRING、BLESSINGS_LANTERN、BLESSINGS_RANDOM 的完整定义，
# 实际代码中请保持您之前添加了 Emoji 的版本。
# 此处仅作示意，您需要将之前完整的祝福语数据复制到此处。
# ...（祝福语数据部分不变，完全沿用您上次提供的版本）

FESTIVALS = ['春节祝福', '元宵节祝福', '随机祝福']


class StartScreen(Screen):
    """可滑动开屏广告页，带跳过按钮和底部指示点，自动轮播，用户滑动时暂停"""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = FloatLayout()

        # 轮播图片列表
        splash_images = ['images/splash1.png', 'images/splash2.png', 'images/splash3.png']
        self.carousel = Carousel(direction='right', loop=True)
        for img_path in splash_images:
            img = Image(source=img_path, allow_stretch=True, keep_ratio=False)
            self.carousel.add_widget(img)
        # 监听触摸事件（用户手动滑动时会触发）
        self.carousel.bind(on_touch_down=self.on_carousel_touch_down)
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

        # 跳过按钮和倒计时（水平布局）
        top_right = BoxLayout(size_hint=(None, None), size=(dp(160), dp(40)),
                              pos_hint={'right': 1, 'top': 1}, spacing=dp(5))
        # 倒计时标签
        self.countdown_label = Label(
            text='6 秒',
            size_hint=(None, None),
            size=(dp(60), dp(40)),
            color=(1,1,1,1),
            bold=True,
            font_name='Chinese'
        )
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
        top_right.add_widget(self.countdown_label)
        top_right.add_widget(skip_btn)
        layout.add_widget(top_right)

        self.add_widget(layout)

        # 定时器管理
        self._auto_slide_trigger = None   # 自动轮播定时器（每3秒切换）
        self._enter_timer = None           # 进入主屏倒计时定时器（每秒更新）
        self._idle_timer = None            # 无操作5秒后恢复的定时器

        # 初始状态：启动自动轮播和6秒倒计时
        self.countdown = 6
        self._start_auto_slide()
        self._start_enter_countdown()

    def _start_auto_slide(self):
        """启动自动轮播，每3秒切换一张"""
        self._stop_auto_slide()
        self._auto_slide_trigger = Clock.schedule_interval(self._next_slide, 3)

    def _stop_auto_slide(self):
        if self._auto_slide_trigger:
            self._auto_slide_trigger.cancel()
            self._auto_slide_trigger = None

    def _start_enter_countdown(self):
        """启动进入主屏倒计时，每秒递减，归零后跳转"""
        self._stop_enter_countdown()
        self.countdown = 6
        self.countdown_label.text = '6 秒'
        self._enter_timer = Clock.schedule_interval(self._tick_countdown, 1)  # 每秒更新

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
        """重置无操作定时器：取消当前定时，启动5秒后恢复的定时"""
        if self._idle_timer:
            self._idle_timer.cancel()
        self._idle_timer = Clock.schedule_once(self._resume_after_idle, 5)

    def _resume_after_idle(self, dt):
        """5秒无操作后，恢复自动轮播和倒计时"""
        self._idle_timer = None
        self._start_auto_slide()
        self._start_enter_countdown()

    def on_carousel_touch_down(self, instance, touch):
        """当用户触摸Carousel时触发（包括滑动、点击等）"""
        # 判断触摸点是否在Carousel区域内（防止误触其他区域）
        if self.carousel.collide_point(*touch.pos):
            # 停止自动轮播和倒计时
            self._stop_auto_slide()
            self._stop_enter_countdown()
            # 重置无操作定时器（5秒后恢复）
            self._reset_idle_timer()

    def update_indicator(self, index):
        for i, lbl in enumerate(self.indicators):
            lbl.text = '●' if i == index else '○'

    def on_enter(self):
        """进入屏幕时（每次显示）重置状态"""
        self.update_indicator(0)
        self.carousel.index = 0  # 确保从第一张开始
        self._start_auto_slide()
        self._start_enter_countdown()
        # 确保任何残留的空闲定时器被取消
        if self._idle_timer:
            self._idle_timer.cancel()
            self._idle_timer = None

    def on_leave(self):
        """离开屏幕时停止所有定时器"""
        self._stop_auto_slide()
        self._stop_enter_countdown()
        if self._idle_timer:
            self._idle_timer.cancel()
            self._idle_timer = None

    def skip_to_main(self, instance):
        """点击跳过，立即进入主页面"""
        self.on_leave()  # 清理定时器
        self.manager.current = 'main'

    def go_main(self, *args):
        self.manager.current = 'main'


class GuideOverlay(FloatLayout):
    """首次使用引导覆盖层，包含四步引导，支持“不再显示”"""
    def __init__(self, main_screen, **kwargs):
        super().__init__(**kwargs)
        self.main_screen = main_screen
        self.current_step = 0

        # 半透明背景
        with self.canvas.before:
            Color(0, 0, 0, 0.6)
            self.bg_rect = Rectangle(size=self.size, pos=self.pos)
        self.bind(pos=self.update_bg, size=self.update_bg)

        # 定义四个步骤的目标和说明文字
        self.steps = [
            (main_screen.spring_btn, "第一步：选择节日"),
            (self._get_humor_button(), "第二步：选择祝福语分类"),
            (self._get_first_blessing_button(), "第三步：点击选定祝福语"),
            (main_screen.share_btn, "第四步：点击立马发送")
        ]
        self.create_step_ui()

    def update_bg(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size

    def _get_humor_button(self):
        """从分类布局中找到文字为“幽默搞怪”的按钮"""
        for child in self.main_screen.category_layout.children:
            if isinstance(child, Button) and child.text == '幽默搞怪':
                return child
        return None  # 如果找不到（极少情况），则指向分类布局本身

    def _get_first_blessing_button(self):
        """获取祝福语列表中的第一条按钮（位于最上方）"""
        if self.main_screen.list_layout.children:
            # children 列表的第一个是最后添加的（底部），最后一个是最先添加的（顶部）
            return self.main_screen.list_layout.children[-1]
        return None

    def create_step_ui(self):
        self.clear_widgets()
        if self.current_step >= len(self.steps):
            self.dismiss()
            return

        target, text = self.steps[self.current_step]
        if target is None:
            # 如果目标不存在，跳过此步（容错）
            self.next_step()
            return

        # 计算目标在窗口中的位置
        win_pos = target.to_window(*target.pos)
        target_center_x = win_pos[0] + target.width / 2
        target_top = win_pos[1] + target.height

        # 创建气泡（指示框）
        bubble = BoxLayout(orientation='vertical', size_hint=(None, None),
                           size=(dp(220), dp(100)), padding=dp(10), spacing=dp(5))
        with bubble.canvas.before:
            Color(1, 1, 1, 1)
            RoundedRectangle(pos=bubble.pos, size=bubble.size, radius=[dp(10)])
        bubble_label = Label(text=text, color=(0,0,0,1), size_hint_y=0.6,
                             halign='center', valign='middle', font_name='Chinese')
        bubble_label.bind(size=lambda s, w: setattr(bubble_label, 'text_size', (bubble_label.width, None)))

        # 按钮区域
        btn_layout = BoxLayout(size_hint_y=0.4, spacing=dp(10))
        if self.current_step == len(self.steps) - 1:
            # 最后一步：显示复选框 + 完成按钮
            check_layout = BoxLayout(size_hint_x=0.6)
            chk = CheckBox(size_hint_x=0.3)
            chk_label = Label(text='下次不再显示', color=(0,0,0,1), size_hint_x=0.7, font_name='Chinese')
            chk_label.bind(size=lambda s, w: setattr(chk_label, 'text_size', (chk_label.width, None)))
            check_layout.add_widget(chk)
            check_layout.add_widget(chk_label)
            btn_layout.add_widget(check_layout)
            next_btn = Button(text='完成', size_hint_x=0.4, background_color=(0.5,0.1,0.1,1), color=(1,1,1,1), font_name='Chinese')
            next_btn.bind(on_press=lambda x: self.finish(chk.active))
        else:
            next_btn = Button(text='下一步', size_hint_x=1, background_color=(0.5,0.1,0.1,1), color=(1,1,1,1), font_name='Chinese')
            next_btn.bind(on_press=lambda x: self.next_step())
            btn_layout.add_widget(next_btn)

        bubble.add_widget(bubble_label)
        bubble.add_widget(btn_layout)

        # 将气泡添加到覆盖层
        self.add_widget(bubble)

        # 计算气泡位置：默认放在目标上方，如果超出屏幕则放在下方
        bubble_x = target_center_x - bubble.width / 2
        bubble_y = target_top + dp(10)
        # 检查右边界
        if bubble_x + bubble.width > self.width:
            bubble_x = self.width - bubble.width - dp(10)
        if bubble_x < 0:
            bubble_x = dp(10)
        # 检查上边界，如果超出则放在目标下方
        if bubble_y + bubble.height > self.height:
            bubble_y = win_pos[1] - bubble.height - dp(10)
        if bubble_y < 0:
            bubble_y = dp(10)
        bubble.pos = (bubble_x, bubble_y)

    def next_step(self):
        self.current_step += 1
        self.create_step_ui()

    def finish(self, dont_show):
        """最后一步完成，根据复选框状态存储设置，并关闭引导"""
        if dont_show:
            # 存储到 JsonStore，表示用户选择不再显示引导
            store = JsonStore(App.get_running_app().user_data_dir + '/guide.json')
            store.put('guide', dont_show_again=True)
        self.dismiss()

    def dismiss(self):
        if self.parent:
            self.parent.remove_widget(self)

    def on_touch_down(self, touch):
        # 阻止触摸事件传递到底层控件
        return True


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

        # 顶部图片
        top_container = FloatLayout(size_hint_y=None, height=dp(150))
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

        # 祝福语列表（可滚动）
        self.scroll_view = ScrollView()
        self.scroll_view.size_hint_y = 1
        self.list_layout = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(8))
        self.list_layout.bind(minimum_height=self.list_layout.setter('height'))
        self.scroll_view.add_widget(self.list_layout)
        main_layout.add_widget(self.scroll_view)

        # 底部功能按钮
        bottom_layout = BoxLayout(size_hint=(1, None), height=dp(50), spacing=dp(8))
        self.share_btn = Button(
            text='发给微信好友',
            background_color=get_color_from_hex('#4CAF50'),
            color=(1,1,1,1),
            font_name='Chinese'
        )
        self.share_btn.bind(on_press=self.share_blessings)
        bottom_layout.add_widget(self.share_btn)
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
        self.show_current_page()

    def on_enter(self):
        """每次进入主屏幕时，检查是否需要显示引导"""
        # 检查存储中是否有“不再显示”标记
        try:
            store = JsonStore(App.get_running_app().user_data_dir + '/guide.json')
            if store.exists('guide') and store.get('guide')['dont_show_again']:
                # 用户已选择不再显示，跳过引导
                return
        except:
            pass
        # 未标记，显示引导（延迟一帧确保布局完成）
        Clock.schedule_once(lambda dt: self.show_guide(), 0)

    def show_guide(self):
        """显示引导覆盖层"""
        overlay = GuideOverlay(self)
        self.add_widget(overlay)

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
        # 一次性加载所有祝福语，不分页
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

        # 恢复上一个选中的条目背景色
        if self.selected_item and self.selected_item != instance:
            self.selected_item.background_color = self.selected_item.default_bg_color
            self.selected_item.color = (0.1, 0.1, 0.1, 1)

        # 设置当前条目为选中状态（暗红色背景，亮黄色文字）
        instance.background_color = (0.5, 0.1, 0.1, 1)  # 暗红色
        instance.color = (1, 1, 0, 1)                   # 亮黄色
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
        """显示关于弹窗，暗红标题栏、白色内容、圆角"""
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

        # 内容区域：左内边距 20dp
        content_area = BoxLayout(orientation='vertical', padding=(dp(20), dp(15), dp(15), dp(15)), spacing=dp(5))
        with content_area.canvas.before:
            Color(1, 1, 1, 1)
            self.content_rect = Rectangle(pos=content_area.pos, size=content_area.size)
        content_area.bind(pos=lambda *x: setattr(self.content_rect, 'pos', content_area.pos),
                          size=lambda *x: setattr(self.content_rect, 'size', content_area.size))

        # 使用全局常量 APP_VERSION
        info_texts = [
            '应用名称：马年新春祝福',
            '应用版本：' + APP_VERSION,
            '应用开发：瑾 煜',
            '反馈建议：contactme@sjinyu.com',
            '版权所有，侵权必究！'
        ]
        for line in info_texts:
            lbl = Label(text=line, font_name='Chinese', color=(0,0,0,1),
                        halign='left', valign='middle', size_hint_y=None, height=dp(25))
            # 绑定 width 设置 text_size 确保左对齐
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
        # 强制全屏，隐藏系统栏
        Window.borderless = True
        Window.fullscreen = True
        # 设置窗口大小为屏幕实际大小
        Window.size = Window.system_size

        sm = ScreenManager()
        sm.add_widget(StartScreen(name='start'))
        sm.add_widget(MainScreen(name='main'))
        return sm


if __name__ == '__main__':
    BlessApp().run()



