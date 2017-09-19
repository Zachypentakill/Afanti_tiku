#!/usr/bin/env python
# encoding: utf-8
from __future__ import unicode_literals, absolute_import
import re

'''
用于提取并删除题目前的（2015-安徽-15分-选择题）的信息
>>>html = '<p>(2015-安徽-15分-选择题)这是一道题目'
>>>new_html, meta_info = get_question_meta_info(html)
>>>new_html
<p>这是一道题目
>>>meta_info
{'year': 2015, 'province': '安徽'}
'''


def del_nouse_text_with_brackets(html):
    #替换掉（本题满分30分）， (共30分) 等的字样
    html = re.sub('(\(|（)本?小?题?((满分)|(共))?\d+分?(\)|）)', '', html, flags=re.U)
    #替换掉'(★★★)'　这样的字样
    html = re.sub('((\(|（)[★☆]+(）|\)))', '', html, flags=re.U)
    return html


def del_nouse_text(html):
    html = del_nouse_text_with_brackets(html)
    #替换掉（2015-安徽-15分）中的15分
    brackets_item = get_content_with_brackers(html)
    if brackets_item:
        if test_meta_valid(brackets_item):
            tmp = re.sub('\d+分', '', brackets_item, flags=re.U)
            html = html.replace(brackets_item, tmp)
    return html


def test_meta_valid(text):
    '''
    测试文本是否合法
    '''
    if del_nouse_text_with_brackets(text) == '':  # 如果文本是（本题满分30分）等字样，认为其合法
        return True
    text = get_content_inside_brackets(text)
    interval_pattern = re.compile(r'((\d+)|(-?∞))\s?,\s?((\d+)|(\+?∞))')
    if interval_pattern.match(text): #　避免匹配到[1,2]、(1, 2]等数学区间
        return False

    city_status, city = get_city_from_text(text)
    year_status, year = get_year_from_text(text)

    if city_status and year_status:
        return True
    else:
        return False

def get_city_from_text(text):
    '''
    根据已有列表中的城市信息获取text中的城市信息 粗略，不准确
    '''
    for city in city_lst:
        if city in text:
            return True, city
    return False, ''

def get_year_from_text(text):
    pattern_year = re.compile('(?P<year>((19\d{2})|(20[0-1][0-9]))年?)', flags=re.U)
    if pattern_year.match(text):
        return True, pattern_year.match(text).group('year')
    pattern_year = re.compile('(?P<year>([0189][0-9])[(年)|(届)(级)])', flags=re.U)
    if pattern_year.match(text):
        year = pattern_year.match(text).group('year')
        if int(year) < 50:
            return True, str(2000+int(year))
        else:
            return True, str(1900+int(year))
    return False, ''


def get_content_inside_brackets(text):
    text = text.replace('[', '').replace(']', '')
    text = text.replace('(', '').replace(')', '')
    text = text.replace('（', '').replace('）', '')
    return text


def del_special_character(text):
    text = text.replace('[', '').replace(']', '')
    text = text.replace('(', '').replace(')', '')
    text = text.replace('（', '').replace('）', '')
    text = text.replace('☆', '').replace('★', '')
    text = text.replace('-', '').replace('—', '').replace('•', '')
    text = text.replace(',', '').replace('，', '')
    text = text.replace(';', '').replace('；', '')
    text = text.replace('&lt;', '').replace('&gt;', '')
    return text


def get_content_with_brackers(text):
    '''
    找到（）、()、[]中包裹的内容，这些内容很有可能是考试的年份信息
    '''
    pattern = re.compile('(\(.*?\))')
    if pattern.findall(text):
        return pattern.findall(text)[0]
    pattern = re.compile('(（.*?）)')
    if pattern.findall(text):
        return pattern.findall(text)[0]
    pattern = re.compile('(\[.*?\])')
    if pattern.findall(text):
        return pattern.findall(text)[0]
    return None


def get_and_replace_meta_info(html):
    html = del_special_character(html)
    _, year = get_year_from_text(html)
    html = re.sub('\d+(年|届|级|)(\d+月)?', '', html, flags=re.U)  #删除年份信息
    html = re.sub('\d+月', '', html, flags=re.U)  # 删除月份信息
    html = html.replace(year, '')
    html = re.sub('\d+(分|$|,| ,)', '', html, flags=re.U)
    html = html.replace('多项', '').replace('不定项', '').replace('单项', '').replace('选择', '')
    html = html.replace('多选', '').replace('单选', '')
    html = re.sub('[a-zA-Z0-9]', '', html, flags=re.U)  #删除多余的数字及英文字符
    html = html.replace(' ', '')
    return {'province': html, 'year': year}


def get_question_meta_info(html):
    all_html = html
    all_html = del_nouse_text(all_html)
    html = all_html[:30]

    meta_info = {'province': None, 'year': None}
    content_with_brackets = get_content_with_brackers(html)
    if not content_with_brackets:
        pass
    else:
        if not test_meta_valid(content_with_brackets):
            pass
        else:
            meta_info = get_and_replace_meta_info(content_with_brackets)
            all_html = all_html.replace(content_with_brackets, '')
    return all_html, meta_info


keyword_lst = [
    "课标",
    "全国",
    "中学",
    "联考",
    "课纲",
    "课改",
    "大纲",
    "月考",
    "检测",
    "期末",
    "期中",
    "练习",
    "模拟",
    "质检",
    "一模",
    "二模",
    "三模",
    "调研",
    "摸底",
    "单科",
    "理综",
    "文综",
    "统考",
    "测评",
    "诊断",
    "测试"
]


city_lst = [
    "北京",
    "上海",
    "天津",
    "重庆",
    "山西",
    "河北",
    "内蒙古",
    "辽宁",
    "吉林",
    "黑龙江",
    "江苏",
    "浙江",
    "安徽",
    "福建",
    "江西",
    "山东",
    "河南",
    "湖北",
    "湖南",
    "广东",
    "广西",
    "海南",
    "四川",
    "贵州",
    "云南",
    "西藏",
    "陕西",
    "甘肃",
    "青海",
    "宁夏",
    "新疆",
    "台湾",
    "香港",
    "澳门",
    "东城区",
    "西城区",
    "崇文区",
    "宣武区",
    "朝阳区",
    "丰台区",
    "石景山区",
    "海淀区",
    "门头沟区",
    "房山区",
    "通州区",
    "顺义区",
    "昌平区",
    "大兴区",
    "怀柔区",
    "平谷区",
    "密云",
    "延庆",
    "黄浦区",
    "卢湾区",
    "徐汇区",
    "长宁区",
    "静安区",
    "普陀区",
    "闸北区",
    "虹口区",
    "杨浦区",
    "闵行区",
    "宝山区",
    "嘉定区",
    "浦东新区",
    "金山区",
    "松江区",
    "青浦区",
    "南汇区",
    "奉贤区",
    "崇明",
    "和平区",
    "河东区",
    "河西区",
    "南开区",
    "河北区",
    "红桥区",
    "塘沽区",
    "汉沽区",
    "大港区",
    "东丽区",
    "西青区",
    "津南区",
    "北辰区",
    "武清区",
    "宝坻区",
    "宁河",
    "静海",
    "蓟",
    "万州区",
    "涪陵区",
    "渝中区",
    "大渡口区",
    "江北区",
    "沙坪坝区",
    "九龙坡区",
    "南岸区",
    "北碚区",
    "万盛区",
    "双桥区",
    "渝北区",
    "巴南区",
    "黔江区",
    "长寿区",
    "綦江",
    "潼南",
    "铜梁",
    "大足",
    "荣昌",
    "璧山",
    "梁平",
    "城口",
    "丰都",
    "垫江",
    "武隆",
    "忠",
    "开",
    "云阳",
    "奉节",
    "巫山",
    "巫溪",
    "石柱土家族自治",
    "秀山土家族苗族自治",
    "酉阳土家族苗族自治",
    "彭水苗族土家族自治",
    "江津",
    "合川",
    "永川",
    "南川",
    "石家庄",
    "唐山",
    "秦皇岛",
    "邯郸",
    "邢台",
    "保定",
    "张家口",
    "承德",
    "沧州",
    "廊坊",
    "衡水",
    "太原",
    "大同",
    "阳泉",
    "长治",
    "晋城",
    "朔州",
    "晋中",
    "运城",
    "忻州",
    "临汾",
    "吕梁",
    "呼和浩特",
    "包头",
    "乌海",
    "赤峰",
    "通辽",
    "鄂尔多斯",
    "呼伦贝尔",
    "巴彦淖尔",
    "乌兰察布",
    "兴安盟",
    "锡林郭勒盟",
    "阿拉善盟",
    "沈阳",
    "大连",
    "鞍山",
    "抚顺",
    "本溪",
    "丹东",
    "锦州",
    "营口",
    "阜新",
    "辽阳",
    "盘锦",
    "铁岭",
    "朝阳",
    "葫芦岛",
    "长春",
    "吉林",
    "四平",
    "辽源",
    "通化",
    "白山",
    "松原",
    "白城",
    "延边朝鲜族自治州",
    "哈尔滨",
    "齐齐哈尔",
    "鸡西",
    "鹤岗",
    "双鸭山",
    "大庆",
    "伊春",
    "佳木斯",
    "七台河",
    "牡丹江",
    "黑河",
    "绥化",
    "大兴安岭地区",
    "南京",
    "无锡",
    "徐州",
    "常州",
    "苏州",
    "南通",
    "连云港",
    "淮安",
    "盐城",
    "扬州",
    "镇江",
    "泰州",
    "宿迁",
    "杭州",
    "宁波",
    "温州",
    "嘉兴",
    "湖州",
    "绍兴",
    "金华",
    "衢州",
    "舟山",
    "台州",
    "丽水",
    "合肥",
    "芜湖",
    "蚌埠",
    "淮南",
    "马鞍山",
    "淮北",
    "铜陵",
    "安庆",
    "黄山",
    "滁州",
    "阜阳",
    "宿州",
    "巢湖",
    "六安",
    "亳州",
    "池州",
    "宣城",
    "福州",
    "厦门",
    "莆田",
    "三明",
    "泉州",
    "漳州",
    "南平",
    "龙岩",
    "宁德",
    "南昌",
    "景德镇",
    "萍乡",
    "九江",
    "新余",
    "鹰潭",
    "赣州",
    "吉安",
    "宜春",
    "抚州",
    "上饶",
    "济南",
    "青岛",
    "淄博",
    "枣庄",
    "东营",
    "烟台",
    "潍坊",
    "济宁",
    "泰安",
    "威海",
    "日照",
    "莱芜",
    "临沂",
    "德州",
    "聊城",
    "滨州",
    "荷泽",
    "郑州",
    "开封",
    "洛阳",
    "平顶山",
    "安阳",
    "鹤壁",
    "新乡",
    "焦作",
    "濮阳",
    "许昌",
    "漯河",
    "三门峡",
    "南阳",
    "商丘",
    "信阳",
    "周口",
    "驻马店",
    "武汉",
    "黄石",
    "十堰",
    "宜昌",
    "襄樊",
    "鄂州",
    "荆门",
    "孝感",
    "荆州",
    "黄冈",
    "咸宁",
    "随州",
    "恩施土家族苗族自治州",
    "仙桃",
    "潜江",
    "天门",
    "神农架林区",
    "长沙",
    "株洲",
    "湘潭",
    "衡阳",
    "邵阳",
    "岳阳",
    "常德",
    "张家界",
    "益阳",
    "郴州",
    "永州",
    "怀化",
    "娄底",
    "湘西土家族苗族自治州",
    "广州",
    "韶关",
    "深圳",
    "珠海",
    "汕头",
    "佛山",
    "江门",
    "湛江",
    "茂名",
    "肇庆",
    "惠州",
    "梅州",
    "汕尾",
    "河源",
    "阳江",
    "清远",
    "东莞",
    "中山",
    "潮州",
    "揭阳",
    "云浮",
    "南宁",
    "柳州",
    "桂林",
    "梧州",
    "北海",
    "防城港",
    "钦州",
    "贵港",
    "玉林",
    "百色",
    "贺州",
    "河池",
    "来宾",
    "崇左",
    "海口",
    "三亚",
    "五指山",
    "琼海",
    "儋州",
    "文昌",
    "万宁",
    "东方",
    "定安",
    "屯昌",
    "澄迈",
    "临高",
    "白沙黎族自治",
    "昌江黎族自治",
    "乐东黎族自治",
    "陵水黎族自治",
    "保亭黎族苗族自治",
    "琼中黎族苗族自治",
    "西沙群岛",
    "南沙群岛",
    "中沙群岛的岛礁及其海域",
    "成都",
    "自贡",
    "攀枝花",
    "泸州",
    "德阳",
    "绵阳",
    "广元",
    "遂宁",
    "内江",
    "乐山",
    "南充",
    "眉山",
    "宜宾",
    "广安",
    "达州",
    "雅安",
    "巴中",
    "资阳",
    "阿坝藏族羌族自治州",
    "甘孜藏族自治州",
    "凉山彝族自治州",
    "贵阳",
    "六盘水",
    "遵义",
    "安顺",
    "铜仁地区",
    "黔西南布依族苗族自治州",
    "毕节地区",
    "黔东南苗族侗族自治州",
    "黔南布依族苗族自治州",
    "昆明",
    "曲靖",
    "玉溪",
    "保山",
    "昭通",
    "丽江",
    "思茅",
    "临沧",
    "楚雄彝族自治州",
    "红河哈尼族彝族自治州",
    "文山壮族苗族自治州",
    "西双版纳傣族自治州",
    "大理白族自治州",
    "德宏傣族景颇族自治州",
    "怒江傈僳族自治州",
    "迪庆藏族自治州",
    "拉萨",
    "昌都地区",
    "山南地区",
    "日喀则地区",
    "那曲地区",
    "阿里地区",
    "林芝地区",
    "西安",
    "铜川",
    "宝鸡",
    "咸阳",
    "渭南",
    "延安",
    "汉中",
    "榆林",
    "安康",
    "商洛",
    "兰州",
    "嘉峪关",
    "金昌",
    "白银",
    "天水",
    "武威",
    "张掖",
    "平凉",
    "酒泉",
    "庆阳",
    "定西",
    "陇南",
    "临夏回族自治州",
    "甘南藏族自治州",
    "西宁",
    "海东地区",
    "海北藏族自治州",
    "黄南藏族自治州",
    "海南藏族自治州",
    "果洛藏族自治州",
    "玉树藏族自治州",
    "海西蒙古族藏族自治州",
    "银川",
    "石嘴山",
    "吴忠",
    "固原",
    "中卫",
    "乌鲁木齐",
    "克拉玛依",
    "吐鲁番地区",
    "哈密地区",
    "昌吉回族自治州",
    "博尔塔拉蒙古自治州",
    "巴音郭楞蒙古自治州",
    "阿克苏地区",
    "克孜勒苏柯尔克孜自治州",
    "喀什地区",
    "和田地区",
    "伊犁哈萨克自治州",
    "塔城地区",
    "阿勒泰地区",
    "石河子",
    "阿拉尔",
    "图木舒克",
    "五家渠",
    "台北",
    "高雄",
    "基隆",
    "新竹",
    "台中",
    "嘉义",
    "台南",
    "台北",
    "桃园",
    "新竹",
    "苗栗",
    "台中",
    "彰化",
    "南投",
    "云林",
    "嘉义",
    "台南",
    "高雄",
    "屏东",
    "宜兰",
    "花莲",
    "台东",
    "澎湖",
    "金门",
    "连江",
    "中西区",
    "东区",
    "南区",
    "湾仔区",
    "九龙城区",
    "观塘区",
    "深水埗区",
    "黄大仙区",
    "油尖旺区",
    "离岛区",
    "葵青区",
    "北区",
    "西贡区",
    "沙田区",
    "大埔区",
    "荃湾区",
    "屯门区",
    "元朗区",
    "澳门花地玛堂区",
    "澳门圣安多尼堂区",
    "澳门大堂区",
    "澳门望德堂区",
    "澳门风顺堂区",
    "海岛嘉模堂区",
    "海岛圣方济各堂区"
]


