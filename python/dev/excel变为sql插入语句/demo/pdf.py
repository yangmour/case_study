#!/usr/bin/env python
# -*- coding:utf-8 -*-

import pdfkit
import pdfplumber
import json
#pdfkit.from_file('cs.html','out.pdf')   


pdf = pdfplumber.open("/Users/xiwen/Desktop/dev/文档/预核保文档/复联联合乳果爱医疗保险（2021版）费率表.pdf")
#print(pdf.metadata)
for page in pdf.pages:
	tables = page.extract_tables()
	print(json.dumps(tables, ensure_ascii=False))
	print("==================")
	# for table in tables:
	# 	print(table)
	# 	print("$$$$$$$$$$$$$$$$$$$$$")
	# 	for row in table:
	# 		print("###################")
	# 		print(row)
