from django.test import TestCase
import ast, os, uuid
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
a = [{'Name': 'SZ-IRA-MAN-RT', 'Chassis_ID': '', 'Slot_ID': '',
      'Current_software_images': 'flash:/msr3600x1-cmw710-boot-r0809p33.bin', 'Main_startup_software_images': '',
      'Backup_startup_software_images': ''}, {'Name': 'SZ-IRA-MAN-RT', 'Chassis_ID': '', 'Slot_ID': '',
                                              'Current_software_images': 'flash:/msr3600x1-cmw710-system-r0809p33.bin',
                                              'Main_startup_software_images': '', 'Backup_startup_software_images': ''},
     {'Name': 'SZ-IRA-MAN-RT', 'Chassis_ID': '', 'Slot_ID': '',
      'Current_software_images': 'flash:/msr3600x1-cmw710-escan-r0809p33.bin', 'Main_startup_software_images': '',
      'Backup_startup_software_images': ''}, {'Name': 'SZ-IRA-MAN-RT', 'Chassis_ID': '', 'Slot_ID': '',
                                              'Current_software_images': 'flash:/msr3600x1-cmw710-security-r0809p33.bin',
                                              'Main_startup_software_images': '', 'Backup_startup_software_images': ''},
     {'Name': 'SZ-IRA-MAN-RT', 'Chassis_ID': '', 'Slot_ID': '',
      'Current_software_images': 'flash:/msr3600x1-cmw710-voice-r0809p33.bin', 'Main_startup_software_images': '',
      'Backup_startup_software_images': ''}, {'Name': 'SZ-IRA-MAN-RT', 'Chassis_ID': '', 'Slot_ID': '',
                                              'Current_software_images': 'flash:/msr3600x1-cmw710-data-r0809p33.bin',
                                              'Main_startup_software_images': '', 'Backup_startup_software_images': ''},
     {'Name': 'SZ-IRA-MAN-RT', 'Chassis_ID': '', 'Slot_ID': '',
      'Current_software_images': 'flash:/msr3600x1-cmw710-boot-r0809p33.bin', 'Main_startup_software_images': '',
      'Backup_startup_software_images': ''}, {'Name': 'SZ-IRA-MAN-RT', 'Chassis_ID': '', 'Slot_ID': '',
                                              'Current_software_images': 'flash:/msr3600x1-cmw710-system-r0809p33.bin',
                                              'Main_startup_software_images': '', 'Backup_startup_software_images': ''},
     {'Name': 'SZ-IRA-MAN-RT', 'Chassis_ID': '', 'Slot_ID': '',
      'Current_software_images': 'flash:/msr3600x1-cmw710-escan-r0809p33.bin', 'Main_startup_software_images': '',
      'Backup_startup_software_images': ''}, {'Name': 'SZ-IRA-MAN-RT', 'Chassis_ID': '', 'Slot_ID': '',
                                              'Current_software_images': 'flash:/msr3600x1-cmw710-security-r0809p33.bin',
                                              'Main_startup_software_images': '', 'Backup_startup_software_images': ''},
     {'Name': 'SZ-IRA-MAN-RT', 'Chassis_ID': '', 'Slot_ID': '',
      'Current_software_images': 'flash:/msr3600x1-cmw710-voice-r0809p33.bin', 'Main_startup_software_images': '',
      'Backup_startup_software_images': ''}, {'Name': 'SZ-IRA-MAN-RT', 'Chassis_ID': '', 'Slot_ID': '',
                                              'Current_software_images': 'flash:/msr3600x1-cmw710-data-r0809p33.bin',
                                              'Main_startup_software_images': '', 'Backup_startup_software_images': ''},
     {'Name': 'SZ-IRA-MAN-RT', 'Chassis_ID': '', 'Slot_ID': '', 'Current_software_images': 'None',
      'Main_startup_software_images': '', 'Backup_startup_software_images': ''}]

oldResult = a[-1]["result"]
cmd = a[-1]["cmd"]
print("oldResult=", oldResult)
g = 0
print(isinstance(g, int))

a = [{'id': '57735f8f-3ce3-ae7d-bc7a-782066120ae3', 'ip': '127.0.0.1', 'key': '', 'value': ''},
     {'id': '3e7d9924-70a5-f1dc-8101-c2b86385fbe0', 'ip': '', 'key': '', 'value': ''},
     {'id': 'ccb97f2e-dcb7-9641-a52b-8cc689ac8894', 'ip': '', 'key': '{{vlanNum}}', 'value': ''},
     {'id': '3a302a6e-4086-82af-84e9-6f8ef6063ba2', 'ip': '', 'key': '{{description}}', 'value': ''}]

r = list(x for x in a if x["ip"] != '')
print(r)

# Create your tests here.

a = [{'time': '2021-07-12 10:15:09', 'cmd': 'sys', 'result': 'System View: return to User View with Ctrl+Z.'},
     {'time': '2021-07-12 10:15:15', 'cmd': 'vlan 11', 'result': ''},
     {'time': '2021-07-12 10:15:27', 'cmd': 'description  10.10.10.10 32', 'result': ''},
     {'time': '2021-07-12 10:15:32', 'cmd': 'quit', 'result': ''},
     {'time': '2021-07-12 10:15:36', 'cmd': 'quit', 'result': ''}, {'time': '2021-07-12 10:15:41', 'cmd': 'save',
                                                                    'result': 'The current configuration will be written to the device. Are you sure? [Y/N]:'},
     {'time': '2021-07-12 10:15:45', 'cmd': 'y',
      'result': 'Please input the file name(*.cfg)[flash:/startup.cfg]\n(To leave the existing filename unchanged, press the enter key):'},
     {'time': '2021-07-12 10:15:50', 'cmd': '', 'result': 'flash:/startup.cfg exists, overwrite? [Y/N]:'},
     {'time': '2021-07-12 10:15:57', 'cmd': 'y',
      'result': 'Validating file. Please wait...\nConfiguration is saved to device successfully.'}]

from concurrent.futures import ThreadPoolExecutor

# submit(fn, *args, **kwargs)
# return Future object
with ThreadPoolExecutor(max_workers=1) as executor:
    future = executor.submit(pow, 323, 1235)
    print(future.result())

# -*- coding: utf-8 -*-
__Author__ = "jenrey"
__Date__ = '2020/05/21 16:46'

"""
gitlab ??????????????????api
DOC_URL: http://python-gitlab.readthedocs.io/en/stable/
LOCAL_PATH: C:\Python36\Lib\site-packages\gitlab
"""

a = [['GigabitEthernet0/0', '5cdd-70e7-e851', 'GigabitEthernet0/0', 'GigabitEthernet0/0 Interface', 'SZ-ZHIHANF-CT',
      '10.32.2.2', ''],
     ['GigabitEthernet0/1', '600b-031c-1aa1', 'GigabitEthernet0/0', 'GigabitEthernet0/0 Interface', 'SZ-ZhiHang-CMCC',
      '10.32.2.6', '']]
b = [['GigabitEthernet0/49', '5cdd-70e7-e851', 'GigabitEthernet0/3', 'GigabitEthernet0/3 Interface', 'SZ-ZHIHANF-CT',
      '10.32.4.252', '1'],
     ['GigabitEthernet0/50', '600b-031c-1aa1', 'GigabitEthernet0/3', 'GigabitEthernet0/3 Interface', 'SZ-ZhiHang-CMCC',
      '10.32.4.253', '1']]

'''
        # Excel ?????????
        # ???????????????
        wb = xlwt.Workbook()
        # ??????sheet
        for key, value in downloadResult.items():
            print("key={},value={}", key, value)
            for item in value:
                print("item=", item["cmds"])
                # ??????????????????sheet
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
        # ??????Excel
        buffer = BytesIO()
        wb.save(buffer)
        # ??????????????????????????????????????????????????????MIME??????
        resp = HttpResponse(buffer.getvalue(), content_type='application/vnd.ms-excel')
        # ?????????????????????????????????????????????
        filename = quote('??????.xls')
        # ?????????????????????????????????????????????????????????????????????
        resp['content-disposition'] = f'attachment; filename*=utf-8\'\'{filename}'
        return resp
'''

'''


        ids = []
        for item in tasklistdetailsid:
            ids.append(item["id"])
        taskListresultdetails = models.taskListResultDetails.objects.filter(taskListDetails__id__in=ids)
        listResult = []
        for item in taskListresultdetails:
            jsonResult = item.jsonResult
            if jsonResult:
                cliValueResult = {}
                rowDict = ast.literal_eval(jsonResult)
                cliValueResult.update({"ip": item.taskListDetails.ip, "cmds": item.cmds, })
                for listItem in rowDict:
                    for k, v in listItem.items():
                        cliValueResult.update({k: v})
                cliValueResult.update({"tftid": item.taskListDetails.textfsmtemplates.id, "jsonResult": item.jsonResult,
                                       "oldResult": item.oldResult})
                listResult.append(cliValueResult)
        cmdsSheet = taskListresultdetails.values('cmds').distinct()
        print("cmdsSheet=", cmdsSheet)
        # ???????????????????????????

        # ???????????????
        wb = xlwt.Workbook()
        # ??????????????????sheet
        for c in cmdsSheet:
            sheet = wb.add_sheet('????????????????????????')
        # ??????list cmd ????????????????????????
        # ??????excel
        # ??????
        return APIResponseResult.APIResponse(0, 'ok', listResult)


        # ???????????????
        sheet = wb.add_sheet('????????????????????????')
        if listResult:
            colnames = listResult[0].keys()
            # ???Excel?????????????????????
            for index, name in enumerate(colnames):
                sheet.write(0, index, name)
        for index, rItem in enumerate(listResult):
            col = 0
            for k, v in rItem.items():
                sheet.write(index + 1, col, v)
                col = col + 1
        # ??????Excel
        buffer = BytesIO()
        wb.save(buffer)
        # ??????????????????????????????????????????????????????MIME??????
        resp = HttpResponse(buffer.getvalue(),
                            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        # ????????????????????????????????????????????? ???????????????????????????????????????
        filename = quote('{}.xls'.format(task.taskName))
        # ?????????????????????????????????????????????????????????????????????
        resp['content-disposition'] = f'attachment; filename*=utf-8\'\'{filename}'
        return resp

'''

print(a + b)

import gitlab

url = 'https://gitlab.com/'
token = 'iAe-iqiQBiXaVLU3LsnR'

# ??????
gl = gitlab.Gitlab(url, token)

# ---------------------------------------------------------------- #
# ???????????????project
projects = gl.projects.list()
print(projects)
# ???????????????project
# projects = gl.projects.list(all=True)
# ---------------------------------------------------------------- #


# ---------------------------------------------------------------- #
# ????????????project???name,id
# for p in gl.projects.list(all=True, as_list=False):
#    print(p.name, p.id)
# ---------------------------------------------------------------- #


# ---------------------------------------------------------------- #
# ???????????????project???name,id
# for p in gl.projects.list(page=1):
#    print(p.name, p.id)
# ---------------------------------------------------------------- #


# ---------------------------------------------------------------- #
# ????????????id ?????? project ??????
project = gl.projects.get(27551653)


# ---------------------------------------------------------------- #


# ---------------------------------------------------------------- #
# ????????????
# projects = gl.projects.list(search='keyword')
# ---------------------------------------------------------------- #

# ---------------------------------------------------------------- #
# ??????????????????
# project = gl.projects.create({'name': 'project1'})


# ---------------------------------------------------------------- #
# ????????????commit
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
        aMap["content"] = 'blah'  # open(file_dir, 'r', encoding='ISO-8859-1').read()
        jsonList.append(aMap)
    jMap["actions"] = jsonList
    projects.commits.create(jMap)


filePath = "/Users/congxingwang/pythoncode/NetOpsNornir/inventory"
gitlabPath = "/NetOpsNornir/inventory"
commitFile(filePath, gitlabPath)
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
