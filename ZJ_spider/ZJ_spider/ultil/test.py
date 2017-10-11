# -*-coding:utf8-*-
import os
import sys
a = ['同步测试', '单元试卷', '月考试卷', '期中考试', '期末考试', '中考模拟', '中考真卷', '专题试卷', '开学考试']

b = ['/paper/index?chid=7&xd=2&tree_type=knowledge&papertype=14', '/paper/index?chid=7&xd=2&tree_type=knowledge&papertype=1', '/paper/index?chid=7&xd=2&tree_type=knowledge&papertype=3', '/paper/index?chid=7&xd=2&tree_type=knowledge&papertype=5', '/paper/index?chid=7&xd=2&tree_type=knowledge&papertype=6', '/paper/index?chid=7&xd=2&tree_type=knowledge&papertype=7', '/paper/index?chid=7&xd=2&tree_type=knowledge&papertype=8', '/paper/index?chid=7&xd=2&tree_type=knowledge&papertype=2', '/paper/index?chid=7&xd=2&tree_type=knowledge&papertype=4']
c = zip(a,b)
for i in c:
    print(i)



