from django.test import TestCase

# Create your tests here.

# -*- coding: utf-8 -*-
__Author__ = "jenrey"
__Date__ = '2020/05/21 16:46'

"""
gitlab 经常使用到的api
DOC_URL: http://python-gitlab.readthedocs.io/en/stable/
LOCAL_PATH: C:\Python36\Lib\site-packages\gitlab
"""

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
