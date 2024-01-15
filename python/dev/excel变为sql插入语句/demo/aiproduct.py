#!/usr/bin/env python
# -*- coding:utf-8 -*-
import copy

import requests
import csv, os
import sys, os
import json
import re
import random
from time import sleep
import pymysql
import conndb
import base64
import json
import re
import xlrd


class case():
    def __init__(self):
        self.work_dir = os.getcwd() + "/"
        self.get()

    def get(self):
        w = open(os.getcwd() + "/sql.sql", "w+")
        for parent, dirnames, filenames in os.walk(self.work_dir):
            for filename in filenames:
                if (filename.endswith(".json")):
                    r = open(self.work_dir + filename, "r")
                    j = json.loads(r.read())
                    imageId = {}
                    if ("imageList" in j):
                        for p in j:
                            if (p == "imageList"):
                                for d in j[p]:
                                    conn, cur = conndb.conn_db()
                                    imageId[d["id"]] = d["md5"]
                                    sql = "update fy_case_structuring_summary s set s.summary = '%s' where s.image_id in (select i.id from fy_health_record_image i where  i.uniq_file_id = '%s');" % (
                                    json.dumps(d, ensure_ascii=False), d["md5"])
                                    sql2 = "delete from fy_case_structuring_summary_info where image_id in (select i.id from fy_health_record_image i where  i.uniq_file_id = '%s'); " % (
                                    d["md5"])
                                    w.write(sql + "\n")
                                    w.write(sql2 + "\n")
                                    sta = conndb.exe_update(cur, sql)
                                    sta = conndb.exe_update(cur, sql2)
                                    conndb.exe_commit(cur)
                                    conndb.conn_close(conn, cur)
                            elif (p == "mergeInfo"):
                                info = j[p]
                                conn, cur = conndb.conn_db()
                                user_id = 0
                                num = 0
                                for d in info["fileList"]:
                                    if ("imageId" in d):
                                        num += 1
                                        sql = "SELECT id,user_id FROM fy_health_record_image where uniq_file_id = '%s' order by id desc limit 1" % (
                                        imageId[d["imageId"]])
                                        sta = conndb.exe_query(cur, sql)
                                        for image_id in cur.fetchall():
                                            d["uniqFileId"] = image_id[0]
                                            user_id = image_id[1]
                                sql = "update fy_case_structuring_summary set summary = '%s' where user_id = %s and  is_complete = 'Y'" % (
                                json.dumps(info, ensure_ascii=False), user_id)
                                sta = conndb.exe_update(cur, sql)
                                conndb.exe_commit(cur)
                                conndb.conn_close(conn, cur)
                                w.write(sql + "\n")


# 费率数据导入
class rate_insert:
    def __init__(self,fielName):
        self.work_dir = os.getcwd() + "/"
        self.conn, self.cur = conndb.conn_db()
        self.batch_insert(fielName)

    # 批量插入
    def batch_insert(self, fielName):
        with open(self.work_dir + fielName) as file:
            print("打开文件！")
            # sql_all = ""
            # count = 0
            self.cur.execute('START TRANSACTION;')

            for line_sql in file:

                stat = conndb.exe_update(self.cur, line_sql)
                print(stat)
            # 提交
            conndb.exe_commit(self.cur)
            conndb.conn_close(self.conn, self.cur)

            print("批量插入提交完成!")



# 复联联合乳果爱
class Data():
    def __init__(self):
        self.insuranceRate(
            "/Users/xiwen/Desktop/dev/文档/预核保文档/复联联合乳果爱医疗保险（2021版）费率表.json", "Y")
        self.insuranceRate(
            "/Users/xiwen/Desktop/dev/文档/预核保文档/复联联合乳果爱医疗保险（2021版）费率表2.json", "N")

    def insuranceRate(self, path, ispe):
        r = open(path, "r")
        data = json.loads(r.read())
        rate = ["复星联合乳果爱", "", "", "", "", "", "", "", "", "", "", "", ""]
        data_list = []
        age = ""
        for d in data:
            for dd in d:
                typing = dd[0].replace("\n", "").replace("her", "HER").replace("pr", "PR")
                if (len(typing) > 0):
                    rate[3] = ""
                    rate[4] = ""
                    rate[5] = ""
                if (1 < len(typing) < 5):
                    rate[1] = self.datastrip(dd[0])
                else:
                    if (typing.find("Luminal A") > -1):
                        rate[1] = "Luminal A"
                    elif (typing.find("Luminal B") > -1):
                        rate[1] = "Luminal B"
                    elif (typing.find("HER2 过表达") > -1 or typing.find("HER2过表达") > -1):
                        rate[1] = "Her2过表达型"
                    elif (typing.find("三阴性") > -1):
                        rate[1] = "三阴性"

                    if (typing.find("PR阳") > -1):
                        rate[4] = "阳性"

                    if (typing.find("Ki67&lt;14%") > -1):
                        rate[5] = "<14%"
                    elif (typing.find("Ki67&gt;14%") > -1):
                        rate[5] = "≥14%"

                    if (typing.find("HER2阳") > -1):
                        rate[3] = "阳性"
                    elif (typing.find("HER2阴") > -1):
                        rate[3] = "阴性"

                if (self.datastrip(dd[1]) == "术前未接受新辅助治疗"):
                    rate[6] = "N"
                elif (self.datastrip(dd[1]) == "术前接受新辅助治疗"):
                    rate[6] = "Y"
                if (len(dd[2]) > 3):
                    age = dd[2].replace("，", ",").replace("＞", "").replace("＜", "").replace("≥", "").replace("≤",
                                                                                                             "").replace(
                        " ", "").replace("\n", "").replace("岁", "").split(",")
                if (age[0] > age[1]):
                    rate[7] = age[1]
                    rate[8] = age[0]
                if (age[1] > age[0]):
                    rate[7] = age[0]
                    rate[8] = age[1]
                if (len(dd[3]) > 0):
                    rate[2] = dd[3]
                # 社保
                rate[9] = ispe
                # 报销型10万保额（计划一）：1602元报销型40万保额（计划二）：4110元报销型150万保额（计划三）：14075元
                rate[10] = "报销型10万保额（计划一）：" + dd[4] + "元"
                rate[11] = "报销型40万保额（计划二）：" + dd[5] + "元"
                rate[12] = "报销型150万保额（计划三）：" + dd[6] + "元"
                rate2 = rate.copy()
                data_list.append(rate2)
        self.addInsuranceRate(data_list)

    def datastrip(self, data):
        return data.replace("\n", "").strip()

    def addInsuranceRate(self, data):
        sql = ""
        for d in data:
            sql += "insert into fy_insurance_rate(insurance_name,typing,staging,her,hr,ki,newcomp,min_age,max_age,ispe,plana,planb,planc) values ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s');" % (
                d[0], d[1], d[2], d[3], d[4], d[5], d[6], d[7], d[8], d[9], d[10], d[11], d[12])
        a = open("insert.sql", "a+")
        for d in sql.split(";"):
            if (len(d) > 2):
                a.write(d + ";\n")
        a.close()

    def charItemIsNullHandel(self):
        conn, cur = conndb.conn_db()
        sql = "select c.user_id,c.category,c.check_type,p.why,c.ref_lower_bound,c.ref_upper_bound,c.y_axis_unit from fy_case_structuring_chart_point p left join fy_case_structuring_chart c on p.chart_id = c.id where (c.check_item is null or c.check_item = '') and (p.why is not null and p.why != '') group by c.user_id,p.why;"
        sta = conndb.exe_query(cur, sql)
        sql2 = "insert into fy_case_structuring_chart(user_id,category,check_type,check_item,ref_lower_bound,ref_upper_bound,y_axis_unit) values "
        for d in cur.fetchall():
            sql2 += "('%s','%s','%s','%s','%s','%s','%s')," % (d[0], d[1], d[2], d[3], d[4], d[5], d[6])
        sql2 = sql2[:-1] + ";"
        sta = conndb.exe_update(cur, sql2)
        conndb.exe_commit(cur)
        sql3 = "select p.id,c.id from fy_case_structuring_chart_point p left join fy_case_structuring_chart c1 on c1.id = p.chart_id left join fy_case_structuring_chart c on c.user_id = c1.user_id  and p.why = c.check_item  where p.why is not null and p.why != '' and c1.check_item = '';"
        sta = conndb.exe_query(cur, sql3)
        for d in cur.fetchall():
            sql4 = "update fy_case_structuring_chart_point set chart_id = %s where id = %s;" % (d[1], d[0])
            sta = conndb.exe_update(cur, sql4)
            conndb.exe_commit(cur)
        sql5 = "update  fy_followup_alert set check_item = content where check_item is null or check_item = '';"
        sta = conndb.exe_update(cur, sql5)
        conndb.exe_commit(cur)

        sql6 = "delete from fy_case_structuring_chart_point where alert_def_name = '';"
        sta = conndb.exe_update(cur, sql6)
        conndb.exe_commit(cur)

        sql7 = "delete from fy_case_structuring_chart where  id in (select cid from (select c.id cid from fy_case_structuring_chart c left outer join fy_case_structuring_chart_point cp on c.id = cp.chart_id where cp.id is null) as tmp)"
        sta = conndb.exe_update(cur, sql7)
        conndb.exe_commit(cur)

        conndb.conn_close(conn, cur)


# 国泰如意宝费率
class Insurance():
    def __init__(self):
        self.sql = ""
        self.insuranceRate()
        self.writeSql()

    def insuranceRate(self):

        rate_list = []
        workbook = xlrd.open_workbook("/Users/xiwen/Desktop/dev/文档/预核保文档/国泰如意保产品费率.xlsx")

        reates = {}
        for d in [0, 1, 3]:
            Data_sheet = workbook.sheets()[d]  # 通过索引获取
            rowNum = Data_sheet.nrows  # sheet行数
            colNum = Data_sheet.ncols  # sheet列数
            # 行数
            for i in range(rowNum):
                # 拿标题数据
                text = Data_sheet.cell_value(i, 0)
                if (text.find("乳腺恶性肿瘤") > -1):
                    age = text.split("）")[1].split("-")
                    if (text.find("未经新辅助治疗") > -1):
                        isnew = 'N'
                    else:
                        isnew = 'Y'

                    # 表格内部行数据
                    for j in range(4, 8):
                        # 表格内部列数据
                        for m in range(1, colNum):
                            # 是否社保
                            if (m < 5):
                                # 设置费率
                                self.set_rate(Data_sheet, age, i, isnew, j, m, "Y", reates)
                            else:
                                # 设置费率
                                self.set_rate(Data_sheet, age, i, isnew, j, m, "N", reates)

                        # 只有前五行的情况下设置无社保给付型费率
                        if (colNum == 5):
                            for m in range(1, colNum):
                                self.set_rate(Data_sheet, age, i, isnew, j, m, "N", reates)

        print(reates)
        for d in reates.keys():
            r = d.split("-")
            for dd in reates[d]:
                r.append(dd)
            if (len(r) == 10):
                r.append("")
            rate_list.append(r)
        # ["国泰如意保-Luminal A-0期-18-30-Y-N-N", '报销型100万保额:1198', '给付型每10万保额:1283', '附加特药50万保额:504']
        self.addInsuranceRate(rate_list)

        rate_list2 = []
        for d in [2]:
            Data_sheet = workbook.sheets()[d]  # 通过索引获取
            rowNum = Data_sheet.nrows  # sheet行数
            colNum = Data_sheet.ncols  # sheet列数
            for i in range(2, rowNum):
                if (len(str(Data_sheet.cell_value(i, 1))) > 1):
                    rate = ["国泰如意保", None, None, None]
                    rate[1] = Data_sheet.cell_value(i, 0).split("-")[0]
                    rate[2] = Data_sheet.cell_value(i, 0).split("-")[1]
                    rate[3] = Data_sheet.name + ":" + str(Data_sheet.cell_value(i, 1)) + "元"
                    rate_list2.append(rate)
        for dd in rate_list2:
            self.sql += "insert into fy_insurance_rate(insurance_name,min_age,max_age,plana) values ('%s','%s','%s','%s');" % (
                dd[0], dd[1], dd[2], dd[3])

    # 设置费率
    def set_rate(self, Data_sheet, age, i, isnew, j, m, ispe, reates):
        # 名称，分型，分期，min_age,max_age,isPE,iscom,isnew
        rate = ["国泰如意保", None, None, age[0], age[1], 'N', 'N', isnew]
        rate[1] = Data_sheet.cell_value(i + j, 0)
        rate[2] = (str(Data_sheet.cell_value(i + 3, m))
                   .replace(".0", "")
                   .replace("1", "I期")
                   .replace("2", "II期")
                   .replace("3", "III期")
                   .replace("pCR", "pCR")
                   .replace("0", "0期"))

        # 社保
        rate[5] = ispe
        if (Data_sheet.cell_value(i + 3, m) == "pCR"):
            rate[6] = 'Y'
        # sheet名字:
        money = Data_sheet.name + ":" + str(Data_sheet.cell_value(i + j, m)).split(".")[0] + "元"
        # ["国泰如意保", None, None, age[0], age[1], 'N', 'N', isnew] 拼串-> 国泰如意保-Luminal A-0期-18-30-Y-N-N
        key = "-".join(rate)
        # 如果在字典里就拼接到数组里
        if (key in reates):
            reates[key].append(money)
        else:
            reates[key] = [money]

    def addInsuranceRate(self, data):
        for d in data:
            self.sql += "insert into fy_insurance_rate(insurance_name,typing,staging,min_age,max_age,ispe,pcr,newcomp,plana,planb,planc) values ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s');" % (
                d[0], d[1], d[2], d[3], d[4], d[5], d[6], d[7], d[8], d[9], d[10])

    def writeSql(self):
        a = open("insert.sql", "a+")
        for d in self.sql.split(";"):
            if (len(d) > 2):
                a.write(d + ";\n")
        a.close()


# 泰康费率
class InsuranceTK():
    def __init__(self):
        self.workbook = xlrd.open_workbook(
            "/Users/xiwen/Desktop/dev/文档/预核保文档/泰康报销型3.0plus费率表.xlsx")
        self.sql = ""
        self.insuranceRate1()
        self.insuranceRate2()
        self.insuranceRate3()
        self.insuranceRate4()
        self.insuranceRate5()
        self.insuranceRate6()
        self.insuranceRate7()
        self.insuranceRate8()
        self.writeSql()

    def insuranceRate1(self):
        rate_list = []
        reates = {}
        for d in [0]:
            Data_sheet = self.workbook.sheets()[d]  # 通过索引获取
            rowNum = Data_sheet.nrows  # sheet行数
            colNum = Data_sheet.ncols  # sheet列数
            isnew = 'N'
            for i in range(rowNum):
                if (Data_sheet.cell_value(i, 0) == "无新辅助"):
                    isnew = 'N'
                elif (Data_sheet.cell_value(i, 0) == "有新辅助"):
                    isnew = 'Y'
                if (Data_sheet.cell_value(i, 0) == "销售价格" or Data_sheet.cell_value(i, 0) == "销售费率"):
                    age = Data_sheet.cell_value(i, 1).split("-")
                    for j in range(4, 8):
                        for m in range(1, 4):
                            # 名称，分型，分期，min_age,max_age,isPE,iscom,isnew
                            rate = ["泰康好效保", None, None, age[0], age[1], 'N', 'N', isnew]
                            rate[1] = Data_sheet.cell_value(i + j, 0)
                            rate[2] = str(Data_sheet.cell_value(i + 3, m)).replace(".0", "").replace("1",
                                                                                                     "I期").replace("2",
                                                                                                                    "II期").replace(
                                "3", "III期").replace("pCR", "pCR").replace("0", "0期")
                            # 无社保
                            money = Data_sheet.name + ":" + str(Data_sheet.cell_value(i + j, m)).split(".")[0] + "元"

                            rate2 = copy.deepcopy(rate)
                            rate2.append(money)
                            rate_list.append(rate2)
                            if (m < 5):
                                rate[5] = 'Y'
                            if (Data_sheet.cell_value(i + 3, m) == "pCR"):
                                rate[6] = 'Y'
                            # 有社保
                            rate.append(money)
                            rate_list.append(rate)
        for d in rate_list:
            self.sql += "insert into fy_insurance_rate(insurance_name,typing,staging,min_age,max_age,ispe,pcr,newcomp,plana) values ('%s','%s','%s','%s','%s','%s','%s','%s','%s');" % (
                d[0], d[1], d[2], d[3], d[4], d[5], d[6], d[7], d[8])

    def insuranceRate2(self):
        rate_list = []
        reates = {}
        for d in [1]:
            Data_sheet = self.workbook.sheets()[d]  # 通过索引获取
            rowNum = Data_sheet.nrows  # sheet行数
            colNum = Data_sheet.ncols  # sheet列数
            isnew = 'N'
            for i in range(rowNum):
                if (Data_sheet.cell_value(i, 0) == "销售价格" or Data_sheet.cell_value(i, 0) == "销售费率"):
                    age = Data_sheet.cell_value(i, 1).split("-")
                    for j in range(2, 6):
                        for m in range(1, 2):
                            # 名称，分型，min_age,max_age
                            rate = ["泰康好效保", None, age[0], age[1]]
                            rate[1] = Data_sheet.cell_value(i + j, 0)
                            money = Data_sheet.name + ":" + str(Data_sheet.cell_value(i + j, m)).split(".")[0] + "元"
                            rate.append(money)
                            rate_list.append(rate)
        for d in rate_list:
            self.sql += "insert into fy_insurance_rate(insurance_name,typing,min_age,max_age,plana) values ('%s','%s','%s','%s','%s');" % (
                d[0], d[1], d[2], d[3], d[4])

    def insuranceRate3(self):
        rate_list = []
        reates = {}
        for d in [2]:
            Data_sheet = self.workbook.sheets()[d]  # 通过索引获取
            rowNum = Data_sheet.nrows  # sheet行数
            colNum = Data_sheet.ncols  # sheet列数
            isnew = 'N'
            for i in range(rowNum):
                if (Data_sheet.cell_value(i, 0) == "无新辅助"):
                    isnew = 'N'
                elif (Data_sheet.cell_value(i, 0) == "有新辅助"):
                    isnew = 'Y'
                if (Data_sheet.cell_value(i, 0) == "销售价格" or Data_sheet.cell_value(i, 0) == "销售费率"):
                    age = Data_sheet.cell_value(i, 1).split("-")
                    for j in range(4, 8):
                        for m in range(1, 9):
                            if (len(str(Data_sheet.cell_value(i + 3, m))) < 1):
                                break
                            # 名称，分型，分期，min_age,max_age,isPE,iscom,isnew
                            rate = ["泰康好效保", None, None, age[0], age[1], 'N', 'N', isnew]
                            rate[1] = Data_sheet.cell_value(i + j, 0)
                            rate[2] = str(Data_sheet.cell_value(i + 3, m)).replace(".0", "").replace("1",
                                                                                                     "I期").replace("2",
                                                                                                                    "II期").replace(
                                "3", "III期").replace("pCR", "pCR").replace("0", "0期")
                            if (isnew == 'N' and m < 5):
                                rate[5] = 'Y'
                            elif (isnew == 'Y' and m < 4):
                                rate[5] = 'Y'
                            if (Data_sheet.cell_value(i + 3, m) == "pCR"):
                                rate[6] = 'Y'
                            money = Data_sheet.name + ":" + str(Data_sheet.cell_value(i + j, m)).split(".")[0] + "元"
                            rate.append(money)
                            rate_list.append(rate)
        for d in rate_list:
            self.sql += "insert into fy_insurance_rate(insurance_name,typing,staging,min_age,max_age,ispe,pcr,newcomp,plana) values ('%s','%s','%s','%s','%s','%s','%s','%s','%s');" % (
                d[0], d[1], d[2], d[3], d[4], d[5], d[6], d[7], d[8])

    def insuranceRate4(self):
        rate_list = []
        reates = {}
        for d in [3]:
            Data_sheet = self.workbook.sheets()[d]  # 通过索引获取
            rowNum = Data_sheet.nrows  # sheet行数
            colNum = Data_sheet.ncols  # sheet列数
            isnew = 'N'
            for i in range(rowNum):
                if (Data_sheet.cell_value(i, 0) == "销售价格" or Data_sheet.cell_value(i, 0) == "销售费率"):
                    age = Data_sheet.cell_value(i, 1).split("-")
                    for j in range(3, 7):
                        for m in range(1, 3):
                            # 名称，分型，min_age,max_age,isPE
                            rate = ["泰康好效保", None, age[0], age[1], 'N']
                            if (m == 1):
                                rate[4] = 'Y'
                            rate[1] = Data_sheet.cell_value(i + j, 0)
                            money = Data_sheet.name + ":" + str(Data_sheet.cell_value(i + j, m)).split(".")[0] + "元"
                            rate.append(money)
                            rate_list.append(rate)
        for d in rate_list:
            self.sql += "insert into fy_insurance_rate(insurance_name,typing,min_age,max_age,ispe,plana) values ('%s','%s','%s','%s','%s','%s');" % (
                d[0], d[1], d[2], d[3], d[4], d[5])

    def insuranceRate5(self):
        rate_list = []
        reates = {}
        for d in [4]:
            Data_sheet = self.workbook.sheets()[d]  # 通过索引获取
            rowNum = Data_sheet.nrows  # sheet行数
            colNum = Data_sheet.ncols  # sheet列数
            for i in range(4, rowNum):
                if (len(str(Data_sheet.cell_value(i, 1))) > 1):
                    rate = ["泰康好效保", None, None, None]
                    rate[1] = Data_sheet.cell_value(i, 0).split("-")[0]
                    rate[2] = Data_sheet.cell_value(i, 0).split("-")[1]
                    rate[3] = Data_sheet.name + ":" + str(Data_sheet.cell_value(i, 1)) + "元"
                    rate_list.append(rate)
        for d in rate_list:
            self.sql += "insert into fy_insurance_rate(insurance_name,min_age,max_age,plana) values ('%s','%s','%s','%s');" % (
                d[0], d[1], d[2], d[3])

    def insuranceRate6(self):
        rate_list = []
        reates = {}
        for d in [5]:
            Data_sheet = self.workbook.sheets()[d]  # 通过索引获取
            rowNum = Data_sheet.nrows  # sheet行数
            colNum = Data_sheet.ncols  # sheet列数
            isnew = 'N'
            for i in range(rowNum):
                if (Data_sheet.cell_value(i, 0) == "无新辅助"):
                    isnew = 'N'
                elif (Data_sheet.cell_value(i, 0) == "有新辅助"):
                    isnew = 'Y'
                if (Data_sheet.cell_value(i, 0) == "销售价格" or Data_sheet.cell_value(i, 0) == "销售费率"):
                    age = Data_sheet.cell_value(i, 1).split("-")
                    name = Data_sheet.cell_value(i, 2).replace("w", "万保额")
                    for j in range(4, 8):
                        for m in range(1, 9):
                            if (len(str(Data_sheet.cell_value(i + 3, m))) < 1):
                                break
                            # 名称，分型，分期，min_age,max_age,isPE,iscom,isnew
                            rate = ["泰康好效保", None, None, age[0], age[1], 'N', 'N', isnew]
                            rate[1] = Data_sheet.cell_value(i + j, 0)
                            rate[2] = str(Data_sheet.cell_value(i + 3, m)).replace(".0", "").replace("1",
                                                                                                     "I期").replace("2",
                                                                                                                    "II期").replace(
                                "3", "III期").replace("pCR", "pCR").replace("0", "0期")
                            if (isnew == 'N' and m < 5):
                                rate[5] = 'Y'
                            elif (isnew == 'Y' and m < 4):
                                rate[5] = 'Y'
                            if (Data_sheet.cell_value(i + 3, m) == "pCR"):
                                rate[6] = 'Y'
                            money = Data_sheet.name + name + ":" + str(Data_sheet.cell_value(i + j, m)).split(".")[
                                0] + "元"
                            if ("-".join(rate) in reates):
                                reates["-".join(rate)].append(money)
                            else:
                                reates["-".join(rate)] = [money]
        for d in reates.keys():
            r = d.split("-")
            for dd in reates[d]:
                r.append(dd)
            if (len(r) == 9):
                r.append("")
            rate_list.append(r)
        for d in rate_list:
            self.sql += "insert into fy_insurance_rate(insurance_name,typing,staging,min_age,max_age,ispe,pcr,newcomp,plana,planb) values ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s');" % (
                d[0], d[1], d[2], d[3], d[4], d[5], d[6], d[7], d[8], d[9])

    def insuranceRate7(self):
        rate_list = []
        reates = {}
        for d in [6]:
            Data_sheet = self.workbook.sheets()[d]  # 通过索引获取
            rowNum = Data_sheet.nrows  # sheet行数
            colNum = Data_sheet.ncols  # sheet列数
            isnew = 'N'
            for i in range(rowNum):
                if (Data_sheet.cell_value(i, 0) == "无新辅助"):
                    isnew = 'N'
                elif (Data_sheet.cell_value(i, 0) == "有新辅助"):
                    isnew = 'Y'
                if (Data_sheet.cell_value(i, 0) == "销售价格" or Data_sheet.cell_value(i, 0) == "销售费率"):
                    age = Data_sheet.cell_value(i, 1).split("-")
                    name = Data_sheet.cell_value(i, 2).replace("w", "万保额")
                    for j in range(3, 7):
                        for m in range(1, 5):
                            if (len(str(Data_sheet.cell_value(i + 3, m))) < 1):
                                break
                            # 名称，分型，分期，min_age,max_age,iscom,isnew
                            rate = ["泰康好效保", None, None, age[0], age[1], 'N', isnew]
                            rate[1] = Data_sheet.cell_value(i + j, 0)
                            rate[2] = str(Data_sheet.cell_value(i + 2, m)).replace(".0", "").replace("1",
                                                                                                     "I期").replace("2",
                                                                                                                    "II期").replace(
                                "3", "III期").replace("pCR", "pCR").replace("0", "0期")
                            if (Data_sheet.cell_value(i + 3, m) == "pCR"):
                                rate[5] = 'Y'
                            money = Data_sheet.name + name + ":" + str(Data_sheet.cell_value(i + j, m)).split(".")[
                                0] + "元"
                            if ("-".join(rate) in reates):
                                reates["-".join(rate)].append(money)
                            else:
                                reates["-".join(rate)] = [money]
        for d in reates.keys():
            r = d.split("-")
            for dd in reates[d]:
                r.append(dd)
            if (len(r) == 9):
                r.append("")
            rate_list.append(r)
        for d in rate_list:
            self.sql += "insert into fy_insurance_rate(insurance_name,typing,staging,min_age,max_age,pcr,newcomp,plana,planb) values ('%s','%s','%s','%s','%s','%s','%s','%s','%s');" % (
                d[0], d[1], d[2], d[3], d[4], d[5], d[6], d[7], d[8])

    def insuranceRate8(self):
        rate_list = []
        reates = {}
        for d in [7]:
            Data_sheet = self.workbook.sheets()[d]  # 通过索引获取
            rowNum = Data_sheet.nrows  # sheet行数
            colNum = Data_sheet.ncols  # sheet列数
            for i in range(2, rowNum):
                if (len(str(Data_sheet.cell_value(i, 1))) > 1):
                    rate = ["泰康好效保", None, None, None]
                    rate[1] = Data_sheet.cell_value(i, 0).split("-")[0]
                    rate[2] = Data_sheet.cell_value(i, 0).split("-")[1]
                    rate[3] = Data_sheet.name + ":" + str(Data_sheet.cell_value(i, 1)) + "元"
                    rate_list.append(rate)
        for d in rate_list:
            self.sql += "insert into fy_insurance_rate(insurance_name,min_age,max_age,plana) values ('%s','%s','%s','%s');" % (
                d[0], d[1], d[2], d[3])

    def writeSql(self):
        a = open("insert.sql", "a+")
        for d in self.sql.split(";"):
            if (len(d) > 2):
                a.write(d + ";\n")
        a.close()


if __name__ == '__main__':
    Data()
    Insurance()
    InsuranceTK()

    rate_insert("insert.sql")