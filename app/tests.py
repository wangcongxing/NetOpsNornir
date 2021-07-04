from django.test import TestCase
import ast
print(ast.literal_eval('[]'))

# Create your tests here.

# -*- coding: utf-8 -*-
__Author__ = "jenrey"
__Date__ = '2020/05/21 16:46'

"""
gitlab 经常使用到的api
DOC_URL: http://python-gitlab.readthedocs.io/en/stable/
LOCAL_PATH: C:\Python36\Lib\site-packages\gitlab
"""

a = [['GigabitEthernet0/0', '5cdd-70e7-e851', 'GigabitEthernet0/0', 'GigabitEthernet0/0 Interface', 'SZ-ZHIHANF-CT', '10.32.2.2', ''], ['GigabitEthernet0/1', '600b-031c-1aa1', 'GigabitEthernet0/0', 'GigabitEthernet0/0 Interface', 'SZ-ZhiHang-CMCC', '10.32.2.6', '']]
b = [['GigabitEthernet0/49', '5cdd-70e7-e851', 'GigabitEthernet0/3', 'GigabitEthernet0/3 Interface', 'SZ-ZHIHANF-CT', '10.32.4.252', '1'], ['GigabitEthernet0/50', '600b-031c-1aa1', 'GigabitEthernet0/3', 'GigabitEthernet0/3 Interface', 'SZ-ZhiHang-CMCC', '10.32.4.253', '1']]

'''
        # Excel 写入行
        # 创建工作簿
        wb = xlwt.Workbook()
        # 新建sheet
        for key, value in downloadResult.items():
            print("key={},value={}", key, value)
            for item in value:
                print("item=", item["cmds"])
                # 根据指令创建sheet
                try:
                    sheet = wb.add_sheet(item["cmds"])
                except Exception as e:
                    sheet = wb.get_sheet(item["cmds"])

                print("jsonResult=", item["jsonResult"])
                if item["jsonResult"]:
                    for inx, r in enumerate(ast.literal_eval(item["jsonResult"])):
                        for i, v in enumerate(r):
                            sheet.write(inx + 1, i, v)
                            # sheet.write(0, 0, v)

                print("oldResult=", item["oldResult"])
        # 保存Excel
        buffer = BytesIO()
        wb.save(buffer)
        # 将二进制数据写入响应的消息体中并设置MIME类型
        resp = HttpResponse(buffer.getvalue(), content_type='application/vnd.ms-excel')
        # 中文文件名需要处理成百分号编码
        filename = quote('老师.xls')
        # 通过响应头告知浏览器下载该文件以及对应的文件名
        resp['content-disposition'] = f'attachment; filename*=utf-8\'\'{filename}'
        return resp
'''



print(a+b)

import gitlab

url = 'https://gitlab.com/'
token = 'iAe-iqiQBiXaVLU3LsnR'

# 登录
gl = gitlab.Gitlab(url, token)

# ---------------------------------------------------------------- #
# 获取第一页project
projects = gl.projects.list()
print(projects)
# 获取所有的project
# projects = gl.projects.list(all=True)
# ---------------------------------------------------------------- #


# ---------------------------------------------------------------- #
# 获取所有project的name,id
# for p in gl.projects.list(all=True, as_list=False):
#    print(p.name, p.id)
# ---------------------------------------------------------------- #


# ---------------------------------------------------------------- #
# 获取第一页project的name,id
# for p in gl.projects.list(page=1):
#    print(p.name, p.id)
# ---------------------------------------------------------------- #


# ---------------------------------------------------------------- #
# 通过指定id 获取 project 对象
project = gl.projects.get(27551653)


# ---------------------------------------------------------------- #


# ---------------------------------------------------------------- #
# 查找项目
# projects = gl.projects.list(search='keyword')
# ---------------------------------------------------------------- #

# ---------------------------------------------------------------- #
# 创建一个项目
# project = gl.projects.create({'name': 'project1'})


# ---------------------------------------------------------------- #
# 创建一个commit
def judgeType(projects, file_path):
    try:
        projects.files.get(file_path=file_path, ref="main")
        return True
    except Exception as e:
        return False


import os


def commitFile(filePath, gitlabPath):
    gl = gitlab.Gitlab(url, token)
    projects = gl.projects.get(27551653)
    jsonList = []
    jMap = {}
    jMap["branch"] = "main"
    jMap["commit_message"] = "xxxxx"
    for file in os.listdir("/Users/congxingwang/pythoncode/NetOpsNornir/inventory"):
        file_dir = os.path.join(filePath, file)
        gitlab_dir = '%s%s' % (gitlabPath, file)
        aMap = {}
        if judgeType(projects, gitlab_dir):
            aMap["action"] = "update"
        else:
            aMap["action"] = "create"
        aMap["file_path"] = gitlab_dir
        aMap["content"] = 'blah'#open(file_dir, 'r', encoding='ISO-8859-1').read()
        jsonList.append(aMap)
    jMap["actions"] = jsonList
    projects.commits.create(jMap)


filePath = "/Users/congxingwang/pythoncode/NetOpsNornir/inventory"
gitlabPath = "/NetOpsNornir/inventory"
commitFile(filePath,gitlabPath)
'''
data = {
    'branch_name': 'master',  # v3
    'commit_message': 'blah blah blah',
    'actions': [
        {
            'action': 'create',
            'file_path': '/Users/congxingwang/pythoncode/NetOpsNornir/utils/demo2.py',
            'content': 'blah'
        }
    ]
}
commit = project.commits.create(data)
'''

# ---------------------------------------------------------------- #


# ---------------------------------------------------------------- #
# Compare two branches, tags or commits:
result = project.repository_compare('develop', 'feature-20180104')
print(result)
# get the commits

for commit in result['commits']:
    print(commit)
#
# get the diffs
for file_diff in result['diffs']:
    print(file_diff)
# ---------------------------------------------------------------- #


# ---------------------------------------------------------------- #
# get the commits
for commit in result['commits']:
    print(commit)
#
# get the diffs
for file_diff in result['diffs']:
    print(file_diff)
# ---------------------------------------------------------------- #
