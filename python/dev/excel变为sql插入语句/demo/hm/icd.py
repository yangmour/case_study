import xlrd


# icd10诊断编码
class Icd10DiagnosticCoding:
    def __init__(self, path, insert_table_name):
        self.workbook = xlrd.open_workbook(path)
        arr = self.parse()
        self.createSql(arr, insert_table_name)

    # 解析数据
    def parse(self):
        sh0 = self.workbook.sheet_by_index(0)
        print("{0} {1}".format(sh0.name, sh0.nrows, sh0.ncols))
        arr = []
        for rx in range(sh0.nrows - 1):
            # print("行下表：" + str(rx))
            # ['国临版编码', '国临版名称', '医保版2.0编码', '医保版2.0名称']
            rows = sh0.row_values(rx)
            # print(rows)
            arr.append(rows)

        return arr

    # 创建sql
    def createSql(self, arr, insert_table_name):
        with open("./icd10_diagnostic_coding.sql", "a+") as icd10File:
            baseSql = "insert into {0}(diagnosis_code, diagnosis_name) values(\"{1}\",\"{2}\");\n"
            for cols in arr:
                sql = baseSql.format(insert_table_name, cols[0], cols[1])
                icd10File.write(sql)


# 3位代码类目表
class ThreeBitCodeCategory:
    def __init__(self, path, insert_table_name):
        self.workbook = xlrd.open_workbook(path)
        arr = self.parse()
        self.createSql(arr, insert_table_name)

    # 解析数据
    def parse(self):
        sh0 = self.workbook.sheet_by_index(0)
        print("{0} {1}".format(sh0.name, sh0.nrows, sh0.ncols))
        arr = []
        for rx in range(sh0.nrows - 2):
            # print("行下表：" + str(rx))
            # ['国临版编码', '国临版名称', '医保版2.0编码', '医保版2.0名称']
            rows = sh0.row_values(rx + 2)
            # print(rows)
            arr.append(rows)

        return arr

    # 创建sql
    def createSql(self, arr, insert_table_name):
        with open("./icd10_three_bit_code_category.sql", "a+") as icd10File:
            baseSql = "insert into {0}(code, name) values(\"{1}\",\"{2}\");\n"
            for cols in arr:
                sql = baseSql.format(insert_table_name, cols[0], cols[1])
                icd10File.write(sql)


# 4位代码类目表
class FourBitCodeCategory:
    def __init__(self, path, insert_table_name):
        self.workbook = xlrd.open_workbook(path)
        arr = self.parse()
        self.createSql(arr, insert_table_name)

    # 解析数据
    def parse(self):
        sh0 = self.workbook.sheet_by_index(0)
        arr = []
        for rx in range(sh0.nrows - 2):
            # print("行下表：" + str(rx))
            # ['国临版编码', '国临版名称', '医保版2.0编码', '医保版2.0名称']
            rows = sh0.row_values(rx + 2)
            # print(rows)
            arr.append(rows)

        return arr

    # 创建sql
    def createSql(self, arr, insert_table_name):
        with open("./icd10_four_bit_code_category.sql", "a+") as icd10File:
            baseSql = "insert into {0}(code, name) values(\"{1}\",\"{2}\");\n"
            for cols in arr:
                sql = baseSql.format(insert_table_name, cols[0], cols[1])
                icd10File.write(sql)


# 6位代码类目表
class SixBitCodeCategory:
    def __init__(self, path, insert_table_name):
        self.workbook = xlrd.open_workbook(path)
        arr = self.parse()
        self.createSql(arr, insert_table_name)

    # 解析数据
    def parse(self):
        sh0 = self.workbook.sheet_by_index(0)
        arr = []
        for rx in range(sh0.nrows - 2):
            # print("行下表：" + str(rx))
            # ['国临版编码', '国临版名称', '医保版2.0编码', '医保版2.0名称']
            rows = sh0.row_values(rx + 2)
            # print(rows)
            arr.append(rows)

        return arr

    # 创建sql
    def createSql(self, arr, insert_table_name):
        with open("./icd10_six_bit_code_category.sql", "a+") as icd10File:
            baseSql = "insert into {0}(code, attachment_code, name) values(\"{1}\",\"{2}\",\"{3}\");\n"
            for cols in arr:
                sql = baseSql.format(insert_table_name, cols[0], cols[1],cols[2])
                icd10File.write(sql)


if __name__ == '__main__':
    # icd10诊断编码
    Icd10DiagnosticCoding("/Users/awen/Desktop/dev/重药/重药数据/全国版RC020-ICD-10诊断编码.xls",
                          "icd10_diagnostic_coding")
    # 3为类目表
    ThreeBitCodeCategory("/Users/awen/Desktop/dev/重药/重药数据/ICD疾病分类/3位代码类目表（ICD-10）.xls",
                             "icd10_three_bit_code_category")
    # 4为类目表
    FourBitCodeCategory("/Users/awen/Desktop/dev/重药/重药数据/ICD疾病分类/4位代码亚目表（ICD-10）.xls",
                        "icd10_four_bit_code_category")
    # 6位类目表
    SixBitCodeCategory("/Users/awen/Desktop/dev/重药/重药数据/ICD疾病分类/6位扩展代码表.xls",
                           "icd10_six_bit_code_category")
