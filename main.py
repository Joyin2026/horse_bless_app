# -*- coding: utf-8 -*-
"""
main.py - 马年送祝福（最终版）
版本：v1.7.7
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
from kivy.core.text import LabelBase
from kivy.resources import resource_add_path

# 立即输出到 stderr 和文件
print("=== DEBUG: main.py STARTED ===", file=sys.stderr)
sys.stderr.flush()

try:
    with open('/sdcard/debug.txt', 'w') as f:
        f.write('main.py started at ' + str(os.getpid()))
except Exception as e:
    print("Failed to write debug file:", e, file=sys.stderr)

# ---------- 全局常量 ----------
APP_VERSION = "v1.7.7"   # 统一版本定义

# 添加当前目录到资源路径，确保能找到字体文件
resource_add_path(os.path.dirname(__file__))

# 只注册中文字体，不涉及 Emoji
try:
    LabelBase.register(name='MainFont', fn_regular='chinese.ttf')
    print("Chinese font loaded successfully.")
except Exception as e:
    print(f"Chinese font failed to load: {e}")
    # 如果连 chinese.ttf 都没有，注册系统默认字体（防止崩溃）
    LabelBase.register(name='MainFont', fn_regular='')
        
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
       '深情走心': [
        "岁月匆匆，又是一年。在这个喜庆的马年春节，特意给你发去这条祝福。感谢你这么多年的陪伴与包容，无论距离远近，你永远是我心里最重要的人。愿你马年平安喜乐，万事胜意。",
        "马蹄声声，踏碎旧岁的尘埃，迎来新岁的曙光。很庆幸，新的一年依然有你在身边。2026丙午年，愿我们的情谊如骏马般坚韧，如老酒般醇厚。新年快乐，我的老朋友。",
        "距离阻挡不了祝福的脚步，马年的钟声已经敲响。远方的你，还好吗？希望这条信息能给你带去一丝温暖。愿你在新的一年里，有人爱，有事做，有所期待，所有的奔赴都有意义。",
        "亲爱的，马年快乐！这是我们一起度过的又一个春节。愿你在2026年，既有策马奔腾的豪情，也有细嗅蔷薇的温柔。不管未来如何，我都会陪你一起，看遍世间风景。",
        "时光不老，我们不散。马年到了，给你拜个年。愿你在这个充满活力的年份里，不忘初心，方得始终。累了就停下来歇歇，我永远是你可以停靠的港湾。",
        "还记得小时候一起放鞭炮的日子吗？转眼又是马年。虽然现在各忙各的，但心里的牵挂从未减少。祝你和家人新春快乐，阖家幸福，希望咱们今年能多聚聚！",
        "新春佳节，最想念的还是你。愿你马年行大运，把过去一年的疲惫都卸下，把所有的希望都装满。愿你眼里有光，心中有爱，脚下有路，一生向阳。",
        "每到过年，最开心的就是给你发祝福。2026是马年，象征着奔腾与希望。愿你像千里马一样，奔向属于自己的星辰大海。无论何时，记得照顾好自己，新年快乐！",
        "一份祝福，一份牵挂。在这个金马贺岁的日子里，愿你所有的梦想都能“马上”开花结果。感谢你出现在我的生命里，祝你马年吉祥，幸福安康，岁岁年年常相见。",
        "旧岁已展千重锦，新年再进百尺竿。马年到了，祝你在新的一年里，收获满满的幸福。不管世界怎么变，我的祝福永远不变。春节快乐，平安顺遂！"
    ],
    '文艺唯美': [
        "春风得意马蹄疾，一日看尽长安花。2026丙午马年，愿你阅尽世间美好，不负韶华。在奔赴未来的路上，既有策马扬鞭的勇气，也有老马识途的智慧。新年快乐！",
        "金马踏春，万物复苏。愿你在这个生机勃勃的年份里，如骏马般驰骋，越过山丘，遇见彩虹。愿你历经千帆，归来仍是少年，心中有梦，眼底有光。",
        "马蹄踏碎旧年霜，春风送来新岁光。新的一年，愿你心有暖阳，何惧风霜。在时光的旷野里，策马奔腾，以此启程，山河远阔，人间值得。",
        "岁序更替，华章日新。马年到了，愿你拥有“骐骥一跃”的爆发力，也有“驽马十驾”的坚持。脚踏实地，终抵星河，所有的美好都将如期而至。",
        "愿你有骏马驰骋的自由，也有老马识途的从容。2026年，愿你且歌且行，一路生花。将过往的遗憾化作春泥，滋养出新年的繁花似锦。",
        "烟火起，照人间，喜悦无边，举杯敬此年。马年新春，愿你三餐四季温暖有趣，生活如旋转木马般充满浪漫。平安喜乐，万事胜意，喜乐长安。",
        "凛冬散尽，星河长明。在这个马年，愿你策马扬鞭，奔赴山海。不恋过往，不畏将来，在自己的节奏里，活成自己喜欢的样子。",
        "以梦为马，不负韶华。2026年，愿你在追梦的路上，一马当先，马到成功。即使前路漫漫，也要勇往直前，因为美好的事物都值得等待。",
        "新年的钟声，是启程的号角。愿你如骏马般，挣脱束缚，奔向自由。愿你的世界，既有烟火俗常，也有诗意清欢，马年大吉！",
        "鲜衣怒马少年时，不负韶华行且知。马年到了，祝你意气风发，前程似锦。愿你所有的努力都不被辜负，所有的期待都能落地生根。"
    ],
    '事业搞钱': [
        "**总，马年大吉！给您和家人拜年了。感谢过去一年对我的提携与信任。2026年，祝您策马扬鞭再创辉煌，事业如骏马奔腾，势不可挡！愿公司业绩一马当先，财源万马奔腾！",
        "王经理，新年好！金马贺岁，商机无限。感谢您一直以来的支持与关照。祝您马年行大运，财运亨通，生意兴隆！愿我们在新的一年里继续并驾齐驱，携手共赢！",
        "亲爱的同事，马年快乐！过去一年，感谢有你并肩作战。2026年，愿我们工作上一马当先，配合默契；生活上龙马精神，多姿多彩。祝你升职加薪“马上”兑现，年终奖拿到手软！",
        "创业伙伴，新春快乐！厉兵秣马又一年，马年是我们大展宏图的好时机。愿你在商海中策马奔腾，独占鳌头！所有的项目都马到成功，所有的付出都能换来丰厚的回报。",
        "祝你马年事业步步高升！2026年，愿你职场之路一马平川，没有坎坷。遇到好机遇要一马当先，抓住好运气要马不停蹄。愿你早日实现财富自由，事业爱情双丰收！",
        "马年到，好运照！祝你在新的一年里，业绩突飞猛进，能力一日千里。在这个充满活力的年份里，愿你马力全开，搞定所有难题，成为行业里的千里马！",
        "开工大吉（预祝）！马年新气象，愿你在工作中如鱼得水，如骏马奔腾。不仅要“马”上有钱，更要“马”上有闲。祝你工作顺利，身体健康，万事顺心！",
        "致正在求职的你：马年是转运年！愿你像千里马一样，早日遇到赏识你的伯乐。求职之路一马平川，面试邀约马不停蹄，早日拿到心仪的Offer，开启人生新篇章！",
        "电商同行，马年发财！祝你店铺流量一马当先，销量万马奔腾。所有的爆款都“马上”出，所有的订单都“马上”发。愿你2026年赚得盆满钵满！",
        "自由职业者，新年快乐！马年愿你灵感如泉涌，客户排队来。愿你策马奔腾在自由的职业天地里，收入翻倍，时间自由，活成自己最喜欢的样子！"
    ],
    '长辈安康': [
        "爸妈，马年快乐！今天是大年初一，孩儿给二老拜年了。丙午年象征着活力与健康，愿这股瑞气永远围绕着你们。希望爸妈龙马精神，身体硬朗，吃得香睡得好，我在外一切都好，勿念！",
        "爷爷奶奶，给您二老磕头拜年啦！马蹄声声报平安，瑞雪纷飞兆丰年。马年到了，祝您福如东海长流水，寿比南山不老松。愿您二老精神矍铄，笑口常开，每天都开开心心！",
        "叔叔阿姨，新年好！金马贺岁，喜气洋洋。祝您全家马年大吉大利！新的一年，愿您身体康健，龙马精神；事业顺心，马到成功；家庭和睦，其乐融融。感谢您一直以来的关心！",
        "外公外婆，春节快乐！马年到了，给您送来最真挚的祝福。愿您二老在新的一年里，腿脚灵便，像骏马一样有活力。想吃啥就吃啥，想玩啥就玩啥，岁月静好，健康常伴！",
        "舅舅，马年吉祥！祝您和舅妈新春快乐，阖家幸福。愿您在2026年，生意兴隆通四海，财源茂盛达三江。身体健健康康，心情舒舒畅畅，万事皆如意！",
        "姑姑，过年好！金马纳福，好运连连。祝您马年行大运，身体倍儿棒，气色红润。愿您的退休生活丰富多彩，像千里马一样驰骋在快乐的草原上，去想去的地方，看想看的风景。",
        "致尊敬的长辈：新春佳节，给您拜年了。祝您马年龙马精神，福寿安康。愿您在新的一年里，远离疾病，远离烦恼，儿孙绕膝，尽享天伦之乐。2026年，平安喜乐！",
        "老师，马年快乐！感谢您的谆谆教诲，您辛苦了。祝您在新的一年里，桃李满天下，春晖遍四方。愿您身体硬朗，精神饱满，继续在教育的草原上策马奔腾，培育更多千里马！",
        "退休的大伯，新年好！马年到了，祝您退休生活更加精彩。愿您龙马精神，积极乐观。没事养养花、遛遛鸟，享受悠闲时光。祝您福如东海，寿比南山！",
        "致家族长辈：金马迎春，福气盈门。在这个喜庆的日子里，祝您和家人马年大吉！愿您身体安康，精神矍铄；家庭和睦，万事兴旺。愿您岁岁有今朝，年年如今日！"
    ],
 '幽默搞怪': [
        "马年到，好运“马”不停蹄向你奔来！2026年，祝你搞钱速度堪比千里马，摸鱼技术练得炉火纯青。不做职场牛马，只做快乐野马，钱包鼓鼓，烦恼全无，咱们继续相爱相杀！",
        "你的丙午马年专属好运已送达，请签收！新的一年，主打一个“马上”系列：马上暴富，马上变瘦，马上脱单。最重要的是，马上实现财务自由，带我一起飞！",
        "兄弟，马年快乐！祝你在新的一年里，发际线像马尾一样浓密，银行卡余额像马蹄声一样数不清。工作上一马当先，酒桌上千杯不醉，今年咱们必须红红火火！",
        "集美，马年大吉！听说马年是咱们的主场，愿你胡吃海喝不长肉，熬夜追剧不爆痘。桃花朵朵开，烂桃花滚远点，所有的美好都“马上”发生在你身上！",
        "嘚驾！好运马正向你狂奔，请注意避让烦恼，张开双臂迎接暴富。2026年，希望你依然保持那份天真，像小马驹一样在快乐草原上撒欢，永远做个快乐的小孩。",
        "马年许愿：愿你赚钱不费力，生活不费心，爱情不费神。做一匹脱缰的野马，在自由的天地里驰骋，去哪里都顺路，做什么都成功！",
        "过年好！马年到了，祝你智商在线，颜值爆表，钱包鼓包。拒绝内卷，拒绝内耗，马力全开享受生活，把去年的遗憾都变成今年的惊喜！",
        "特批你马年“带薪快乐”一年！愿你在2026年，老板不找茬，客户不磨叽，同事不甩锅。每天都是元气满满的一天，所有的好事都排队来找你！",
        "马年到，送你一匹“神马”！它能驮着你避开所有弯路，直达幸福终点。祝你今年买彩票中头奖，打游戏必吃鸡，吃火锅永远有毛肚，快乐加倍！",
        "虽然你不属马，但我祝你马年“马”力十足！追得上高铁，哄得好爱人，打得过生活的小怪兽。2026，咱们一起策马奔腾，活得潇潇洒洒！"
    ]
}

# 元宵节祝福语（5类，每类10条）
BLESSINGS_LANTERN = {
    '温馨团圆': [
        "元宵良辰至，灯火照人间，圆月当空，汤圆香甜，愿一家人平安相伴、喜乐相随，日子有盼头，生活有温暖，岁岁常团圆，年年皆安康。",
        "灯火映万家，团圆共此时，又是一年元宵节，愿春风吹走所有烦恼，月光照亮所有美好，家人闲坐，灯火可亲，所求皆如愿，所行皆坦途。",
        "月圆人圆事事圆，花好灯好年年好，愿你在这个温暖的节日里，有家人陪伴，有朋友关心，有健康身体，有顺遂生活，幸福常在身边，平安岁岁年年。",
        "一盏花灯寄深情，一碗汤圆暖人心，愿你走过山河万里，仍有人等你回家；历经人间烟火，依旧眼里有光、心中有爱，一生被温柔以待。",
        "元宵之夜月色温柔，灯火璀璨，愿所有思念都有回应，所有牵挂都有归宿，愿家人平安健康，日子安稳舒心，生活有滋有味，岁岁无忧无愁。",
        "月圆映团圆，灯火照心安，愿新的一年里，家庭和睦、笑语常伴，烦恼随风而去，好运步步靠近，生活如汤圆般圆满，日子如春夜般温柔。",
        "花灯千盏送美好，圆月一轮照人间，愿你和家人在这个元宵佳节，平安相伴、喜乐相随，心中常怀希望，眼前皆是光明，余生皆有温暖。",
        "良宵共度，团圆难得，愿时光慢一点，温柔多一点，幸福久一点，健康长一点，愿一家人平平安安，一年事顺顺利利，一生心欢欢喜喜。",
        "元宵佳节，暖意融融，愿你三餐四季皆安稳，岁岁年年皆无忧，有人懂你悲欢，有人陪你朝夕，生活不慌不忙，幸福如约而至。",
        "灯火阑珊处，最暖是人间，愿你此夜有团圆，此生有安稳，年年元宵年年喜，岁岁平安岁岁欢，福气常满，好运常伴，喜乐常存。"
    ],
    '喜庆吉利': [
        "元宵花灯照前程，春风如意伴君行，愿你新岁财源广、福气多、好运长、万事顺，事业步步高升，生活顺心如意，日子红红火火，人生处处精彩。",
        "月圆添吉庆，灯火送安康，愿你新的一年顺风顺水，所求皆所得，所想皆成真，出门遇贵人，在家听喜报，平安喜乐常相随，吉祥好运伴全年。",
        "吃一碗香甜汤圆，盼一年万事圆满，愿你财运亨通、福运绵长、好运连连，工作不辛苦，生活不疲惫，心情常明媚，人生常欢喜。",
        "元宵启新程，万事皆可期，愿你前路光明、万事顺遂、心想事成，所有努力不被辜负，所有梦想终会实现，所有美好如约而至。",
        "花灯映福运，圆月照安康，愿你在新的一年里，福气满满、财气滔滔、喜气洋洋，事事有回音，件件有着落，处处有惊喜。",
        "良宵美景庆元宵，欢歌笑语迎好兆，愿你日子有光、心中有梦、身边有爱，一路春暖花开，一生顺遂无忧，一年更比一年好。",
        "月圆人安，岁岁吉祥，愿你无病无灾、平安自在，有钱有闲、喜乐开怀，忙时有动力，闲时有温馨，生活有期待，人生有光芒。",
        "元宵佳节好运到，吉祥如意身边绕，愿你每一次付出都有收获，每一次期盼都有回应，每一次等待都有结果，万事顺心，皆得圆满。",
        "灯火千盏，福满人间，愿你新岁多喜乐、长安宁、常安康，事业有起色，生活有奔头，家庭有欢笑，未来有希望。",
        "月圆映好梦，灯火暖人心，愿你往后余生，风雨有伞，归途有灯，心中有梦，眼中有光，生活温柔以待，人生步步生花。"
    ],
    '温柔治愈': [
        "月光温柔，灯火可亲，人间烟火，最抚人心。愿你在元宵良夜里，放下疲惫与焦虑，拥抱温暖与美好，愿生活善待你，岁月不辜负你。",
        "一盏灯，照亮归途；一碗汤圆，甜满心头。愿你历经世事沧桑，依旧眼里有星光，心中有山海，笑里有坦荡，一生清澈明朗。",
        "月色如水，灯影如梦，愿你在喧嚣人间，守住一份从容，留得一份心安，不慌不忙，静静成长，慢慢发光，平安喜乐，自在从容。",
        "元宵之夜，愿所有烦恼随夜色消散，所有美好随灯火降临，愿你被世界温柔以待，被幸福紧紧包围，被平安时时守护。",
        "人间最美是团圆，世间最暖是心安，愿这满城灯火，为你照亮前路；愿这一轮明月，为你带来温柔，愿你岁岁常欢愉，年年皆胜意。",
        "花灯摇曳，春风轻拂，愿你心中有光，不管走到哪里，都能被温暖照亮；愿你心中有爱，不管经历什么，都能被善意环绕。",
        "月圆映初心，温暖赴人生，愿你保持热爱，奔赴下一场山海；心存期待，迎接每一个清晨，生活温柔有趣，人生平安顺遂。",
        "灯火映诗行，月色满心房，愿你日子清净，抬头皆是温柔，所见皆是美好，所念皆得所期，所想皆能成真，所爱皆可相守。",
        "元宵月圆，愿所有奔赴都有意义，所有坚持都有回报，所有遗憾都能释怀，所有美好都不缺席，平安喜乐，万事胜意。",
        "愿这一盏盏花灯，照亮你一整年的好运；愿这一碗碗汤圆，甜满你一整年的幸福，愿你眼里有笑、心中有暖、身边有爱。"
    ],
    '雅致大气': [
        "灯树千光照，明月逐人来，元宵良辰，愿山河无恙，人间皆安，家和国盛，万事顺遂，愿你此生尽兴，赤诚善良，平安喜乐。",
        "华灯初上，夜色阑珊，月光如水，灯火如画。愿你于人间烟火中坚守初心，于岁月流转中保持从容，不负时光，不负自己，不负佳期。",
        "月满元宵，灯映人间，愿你前路光明，万事圆满，心中有山海，眼底有星辰，行至水穷处，坐看云起时，一生安然，岁岁无忧。",
        "一城灯火，一夜元宵，一轮明月，一份心安。愿你历经千帆，归来仍是少年；尝遍百味，依旧热爱生活，岁岁常安康，年年皆欢喜。",
        "月色皎洁，花灯璀璨，人间良辰，喜乐平安。愿时光清浅，许你安然；愿岁月悠长，护你周全；愿人生圆满，伴你年年。",
        "灯影摇红，夜暖风寒，元宵佳节，愿你以梦为马，不负韶华；以心为舟，不负流年，万事皆如意，余生皆安康。",
        "月圆映良辰，花灯照好梦，愿世间所有美好，都与你不期而遇；愿人生所有圆满，都为你如约而至。",
        "良宵一刻值千金，月圆花好庆新春。愿你有闲赏灯，有心团圆，有福安康，有梦追寻，生活有诗意，心中有光芒。",
        "灯火照人间，吉祥伴流年，愿你平安向暖，喜乐从容，人生如花灯般绚烂，日子如月光般温柔，岁岁无忧，年年圆满。",
        "元宵之夜，月色入怀，灯火入心。愿你眼中有光、笑里有糖、心中有爱，生活不拥挤，笑容不缺席，一生顺遂，一世安宁。"
    ],
    '商务得体': [
        "元宵佳节，月圆人圆，祝您新的一年事业蒸蒸日上，前程似锦宏图展，万事顺心步步高，家庭和睦常幸福，平安喜乐常相伴。",
        "灯火映新程，团圆赴佳期，感谢一路支持与信任，愿新的一年合作更加顺畅，前景更加广阔，事业更上一层楼，财源广进达四方。",
        "月圆添吉庆，灯火启新章，祝您工作顺利、事事顺心、步步高升、前途光明，身体安康、家庭美满、福气常满、好运常临。",
        "良宵共度，万象更新，愿您在新的一年里，目标清晰、步履坚定、事业有成、名利双收，所有努力皆有回报，所有付出皆有成果。",
        "元宵送福，灯火传喜，祝您新岁大吉、万事亨通、生意兴隆、财源滚滚，团队同心，其利断金，携手共进，再创佳绩。",
        "月圆人安，事业长安，愿您新的一年顺风顺水，机遇常在，贵人相助，平台更广，道路更宽，未来可期，前程无限。",
        "佳节良宵，灯火璀璨，祝您工作舒心、生活暖心、家人安心、万事放心，愿所有美好如期而至，所有幸运不期而遇。",
        "元宵启新岁，携手赴新程，感谢一路同行，愿我们在新的一年里同心同向、同力同行，攻坚克难，共赢未来，万事圆满。",
        "月圆映初心，灯火照前程，祝您新的一年事业兴旺、家庭幸福、身体健康、万事顺遂，好运连连，福气绵绵。",
        "元宵佳节，喜乐安康，愿您新岁多喜多福多好运，少烦少忧少疲惫，事业稳进，生活安稳，心境安然，万事圆满。"
    ]
}

# 随机祝福语（5类，每类20条，重写为时尚活泼带Emoji版）
BLESSINGS_RANDOM = {
    '暖心话语': [
        "愿你三冬暖，愿你春不寒；愿你天黑有灯，下雨有伞。愿你一路上，有良人相伴。❤️☀️",
        "愿时光能缓，愿故人不散；愿你惦念的人能和你道晚安，愿你独闯的日子里不觉得孤单。✨🌙",
        "愿你往后余生，冷暖有相知，喜乐有分享，同量天地宽，共度日月长。🌸🌿",
        "愿你有好运气，如果没有，愿你在不幸中学会慈悲；愿你被很多人爱，如果没有，愿你在寂寞中学会宽容。🌈🍀",
        "愿你如阳光，明媚不忧伤；愿你如月光，明亮不清冷。愿你此生尽兴，赤诚善良。🌞🌙",
        "愿你所有的努力都不白费，所想的都能如愿，所做的都能实现，愿你往后路途，深情不再枉付。💪🎯",
        "愿你走出半生，归来仍是少年；愿你经历山河，觉得人生值得。🌍🚶",
        "愿你贪吃不胖，美梦不空，深情不负，此生尽兴。🍔💤",
        "愿你有梦为马，随处可栖；愿你执迷不悟时，少受点伤；愿你幡然醒悟时，物是人是。🐴🏠",
        "愿你余生所有的珍惜，都不必靠失去来懂得。愿你的快乐不缺观众，你的故事都有人懂。📖👥",
        "愿你惦念的人能和你道晚安，愿你独闯的日子里不觉得孤单。🛌💤",
        "愿你的世界永远充满阳光，不会有多余的悲伤。愿你在人生道路上，到达心之所向。☀️🛤️",
        "愿你如向日葵，永远面朝阳光，努力生长，保持本色，不偏不倚。🌻",
        "愿你所有快乐，无需假装；愿你此生尽兴，赤诚善良；愿时光能缓，愿故人不散。😊",
        "愿你往后余生，眼里是阳光，笑里是坦荡。愿你天黑有灯，下雨有伞，愿你路上有良人相伴。👫",
        "愿你的生活常温暖，日子总是温柔又闪光。愿你历经风雨，终见彩虹。🌈",
        "愿你这一生，既有随处可栖的江湖，也有追风逐梦的骁勇。🌊",
        "愿你被这个世界温柔以待，躲不过的惊吓都只是一场虚惊，收到的欢喜从无空欢喜。😌",
        "愿你如天上的云，自由自在；愿你如林间的风，潇洒自如。愿你活成自己最喜欢的模样。☁️🍃",
        "愿你所有快乐，无需假装；愿你赤子之心，永远滚烫。❤️🔥"
    ],
    '励志金句': [
        "乾坤未定，你我皆是黑马；乾坤已定，那就扭转乾坤。🐎💫",
        "愿你以渺小启程，以伟大结尾。熬过无人问津的日子，才有诗和远方。🚀🌟",
        "半山腰总是最挤的，你得去山顶看看。星光不问赶路人，时光不负有心人。⛰️✨",
        "愿你眼中有光，活成自己想要的模样；愿你心中有梦，不负韶华。💡",
        "将来的你，一定会感谢现在拼命的自己。每一个优秀的人，都有一段沉默的时光。📈",
        "愿你熬过万丈孤独，藏下星辰大海。愿你跨过星河迈过月亮，去迎接更好的自己。🌌",
        "生活原本沉闷，但跑起来就有风。愿你跑起来，追上那个被寄予厚望的自己。💨",
        "愿你付出甘之如饴，所得归于欢喜。愿你走出半生，归来仍是少年。🍬",
        "愿你成为自己的太阳，无需凭借谁的光。愿你永远年轻，永远热泪盈眶。☀️",
        "愿你像种子一样，一生向阳，在这片土壤里，随万物生长。🌱",
        "愿你每一次流泪，都是喜极而泣；愿你每一次精疲力尽，都有树可倚。😭🌳",
        "愿你学会释怀后一身轻，愿你无悔亦无惧。愿你此生尽兴，赤诚善良。🍃",
        "愿你在被打击时，记起你的珍贵，抵抗恶意；愿你在迷茫时，坚信你的珍贵，爱你所爱，行你所行，听从你心，无问西东。💪",
        "愿你所有的努力都不被辜负，愿你成为自己的太阳，无需凭借谁的光。🌞",
        "愿你以梦为马，不负韶华；愿你拼尽全力，无畏前行。🐴",
        "愿你全力以赴，又满载而归。愿你在这个必须拼得你死我活的世界里，拥有一份不怕变质的爱情。🏆",
        "愿你所有的幸运，都能不期而遇；愿你所有的美好，都能如期而至。🍀",
        "愿你出走半生，归来仍是少年；愿你历经山河，觉得人生值得。🏔️",
        "愿你被世界温柔以待，愿你目之所及，心之所向满满都是爱。🌍❤️",
        "愿你鲜衣怒马，一生荣光；愿你往后余生，平安喜乐。🎉"
    ],
    '幽默风趣': [
        "愿你像高智商一样活着，像低能儿一样快乐。🧠😂",
        "愿你贪吃不胖，美梦不空，深情不负，钱包鼓鼓。🍔💰",
        "愿你以后有酒有肉，能贫能笑，能干能架，此生纵情豁达。🍺🥩",
        "愿你做一个快乐的人，让风吹走你的忧愁，让雨洗掉你的烦恼，让阳光带给你温暖，让月亮带给你浪漫。🌪️🌧️☀️🌙",
        "愿你心情像天气一样晴朗，像吃了蜜糖一样甜，像中了彩票一样嗨。☀️🍯🎰",
        "愿你天天都有好心情，夜夜都有美梦，吃嘛嘛香，干嘛嘛顺。😊💤",
        "愿你像猪一样能吃能睡，像牛一样勤勤恳恳，像猴一样机灵，像狗一样忠诚，然后像人一样快乐。🐷🐮🐵🐶",
        "愿你余额永远充足，愿你卡路里永远不足。💰🔥",
        "愿你发财像发际线一样不留余地，愿你减肥像记忆一样说忘就忘。💇‍♂️💭",
        "愿你以后的生活，不仅有诗和远方，还有眼前的火锅和烧烤。🍲🍢",
        "愿你在这个看脸的世界里，不仅颜值在线，余额也在线。💅💸",
        "愿你发际线永远坚挺，愿你发量永远浓密，愿你熬夜不长痘，愿你吃多不长肉。💇‍♂️🌙🍔",
        "愿你钱包鼓得像气球，烦恼轻得像鸿毛，快乐多得像星星。🎈🪶✨",
        "愿你天天发财，月月中奖，年年有余，生生不息。💵🎁🐟",
        "愿你做一个快乐的小吃货，吃遍天下美食，喝遍天下美酒，玩遍天下美景。🍜🍷🌍",
        "愿你像打游戏一样，一路升级打怪，最后成为人生赢家。🎮🏆",
        "愿你所有的bug都被修复，愿你所有的需求都被满足，愿你永远没有蓝屏。🐞✅",
        "愿你在这个快节奏的时代，慢下来享受生活，做一个快乐的小神仙。🧘‍♂️☁️",
        "愿你像向日葵一样，每天都向着阳光，努力生长，然后结出好多好多的瓜子。🌻🌰",
        "愿你在这个冬天，不仅有棉袄，还有冰淇淋；不仅有暖气，还有冰啤酒。🧥🍦🍺"
    ],
    '唯美诗意': [
        "愿你三冬暖，愿你春不寒；愿你天黑有灯，下雨有伞；愿你一路上，有良人相伴。❄️🌸🌧️☂️",
        "愿时光能缓，愿故人不散；愿你惦念的人能和你道晚安，愿你独闯的日子里不觉得孤单。⏳👥🌙",
        "愿你往后余生，冷暖有相知，喜乐有分享，同量天地宽，共度日月长。🌞🌛",
        "愿你有好运气，如果没有，愿你在不幸中学会慈悲；愿你被很多人爱，如果没有，愿你在寂寞中学会宽容。🍀🤝",
        "愿你如阳光，明媚不忧伤；愿你如月光，明亮不清冷。愿你此生尽兴，赤诚善良。☀️🌙",
        "愿你所有的努力都不白费，所想的都能如愿，所做的都能实现，愿你往后路途，深情不再枉付。💪✨",
        "愿你走出半生，归来仍是少年；愿你经历山河，觉得人生值得。🏞️👦",
        "愿你贪吃不胖，美梦不空，深情不负，此生尽兴。🍜💭",
        "愿你有梦为马，随处可栖；愿你执迷不悟时，少受点伤；愿你幡然醒悟时，物是人是。🐴🏡",
        "愿你余生所有的珍惜，都不必靠失去来懂得。愿你的快乐不缺观众，你的故事都有人懂。📖👂",
        "愿你惦念的人能和你道晚安，愿你独闯的日子里不觉得孤单。🛌",
        "愿你的世界永远充满阳光，不会有多余的悲伤。愿你在人生道路上，到达心之所向。☀️🛤️",
        "愿你如向日葵，永远面朝阳光，努力生长，保持本色，不偏不倚。🌻",
        "愿你所有快乐，无需假装；愿你此生尽兴，赤诚善良；愿时光能缓，愿故人不散。😊",
        "愿你往后余生，眼里是阳光，笑里是坦荡。愿你天黑有灯，下雨有伞，愿你路上有良人相伴。👫",
        "愿你的生活常温暖，日子总是温柔又闪光。愿你历经风雨，终见彩虹。🌈",
        "愿你这一生，既有随处可栖的江湖，也有追风逐梦的骁勇。🌊",
        "愿你被这个世界温柔以待，躲不过的惊吓都只是一场虚惊，收到的欢喜从无空欢喜。😌",
        "愿你如天上的云，自由自在；愿你如林间的风，潇洒自如。愿你活成自己最喜欢的模样。☁️🍃",
        "愿你所有快乐，无需假装；愿你赤子之心，永远滚烫。❤️🔥"
    ],
    '简短精炼': [
        "愿你快乐，愿你幸福，愿你平安。😊❤️🙏",
        "祝你心想事成，万事如意。✨🎯",
        "愿你眼里有光，心中有爱。👀❤️",
        "愿你一生温暖，不舍爱与自由。🔥❤️",
        "愿你无忧无疾，百岁安生不离笑。😊🎂",
        "愿你天黑有灯，下雨有伞，愿你路上有良人相伴。🌙☔👫",
        "愿你所有快乐，无需假装。😄",
        "愿你此生尽兴，赤诚善良。🌟",
        "愿你历尽千帆，归来仍是少年。⛵👦",
        "愿你如阳光，明媚不忧伤。☀️",
        "愿你被世界温柔以待。🌍❤️",
        "愿你贪吃不胖，美梦不空。🍔💤",
        "愿你深情不负，钱包鼓鼓。❤️💰",
        "愿你以后有酒有肉，能贫能笑。🍷🥩",
        "愿你岁月波澜有人陪，余生悲欢有人听。📅👂",
        "愿你往后路途，深情不再枉付。🛤️❤️",
        "愿你眼中总有光芒，活成你想要的模样。✨",
        "愿你付出甘之如饴，所得归于欢喜。🍬",
        "愿你出走半生，归来仍是少年。🚶👦",
        "愿你此生尽兴，赤诚善良。🌟"
    ]
}

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
                font_name='ChineseEmoji'
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
            font_name='ChineseEmoji'
        )
        # 跳过按钮
        skip_btn = Button(
            text='跳过',
            size_hint=(None, None),
            size=(dp(80), dp(40)),
            background_color=get_color_from_hex('#80000000'),
            color=(1,1,1,1),
            bold=True,
            font_name='ChineseEmoji'
        )
        skip_btn.bind(on_press=self.skip_to_main)
        top_right.add_widget(self.countdown_label)
        top_right.add_widget(skip_btn)
        layout.add_widget(top_right)

        self.add_widget(layout)

        # 定时器管理
        self._auto_slide_trigger = None   # 自动轮播定时器（每秒切换）
        self._enter_timer = None           # 进入主屏倒计时定时器
        self._idle_timer = None            # 无操作5秒后恢复的定时器

        # 初始状态：启动自动轮播和6秒倒计时
        self.countdown = 9
        self._start_auto_slide()
        self._start_enter_countdown()

    def _start_auto_slide(self):
        """启动自动轮播，每秒切换一张"""
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
            font_name='ChineseEmoji'
        )
        self.spring_btn.bind(on_press=lambda x: self.switch_festival('春节祝福'))
        self.lantern_btn = Button(
            text='元宵节祝福',
            background_color=get_color_from_hex('#8B4513'),
            color=(1,1,1,1),
            bold=True,
            font_name='ChineseEmoji'
        )
        self.lantern_btn.bind(on_press=lambda x: self.switch_festival('元宵节祝福'))
        self.random_btn = Button(
            text='随机祝福',
            background_color=get_color_from_hex('#8B4513'),
            color=(1,1,1,1),
            bold=True,
            font_name='ChineseEmoji'
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
        share_btn = Button(
            text='发给微信好友',
            background_color=get_color_from_hex('#4CAF50'),
            color=(1,1,1,1),
            font_name='ChineseEmoji'
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
            font_name='ChineseEmoji'
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
                color=(1,1,1,1),
                font_name='ChineseEmoji'
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
                font_name='ChineseEmoji'
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

        title_label = Label(text='关于', font_name='ChineseEmoji', color=(1,1,1,1),
                            halign='left', valign='middle', size_hint_x=0.8)
        title_bar.add_widget(title_label)

        close_btn = Button(text='X', size_hint=(None, None), size=(dp(30), dp(30)),
                           pos_hint={'right':1, 'center_y':0.5},
                           background_color=(0,0,0,0), color=(1,1,1,1),
                           font_name='ChineseEmoji', bold=True)
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
            lbl = Label(text=line, font_name='ChineseEmoji', color=(0,0,0,1),
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







