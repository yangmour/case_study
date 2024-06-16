import xlrd


class Icd10:
    def __init__(self, path, insert_table_name):
        self.workbook = xlrd.open_workbook(path)
        # [['国临版编码', '国临版名称', '医保版2.0编码', '医保版2.0名称']
        # ,['国临版编码', '国临版名称', '医保版2.0编码', '医保版2.0名称']]
        arr = self.parse()
        self.createSql(arr, insert_table_name)

    # 解析数据
    def parse(self):
        sh0 = self.workbook.sheet_by_index(0)
        print("{0} {1} {2}".format(sh0.name, sh0.nrows, sh0.ncols))
        print("Cell D30 is {0}".format(sh0.cell_value(rowx=2, colx=3)))
        arr = []
        for rx in range(sh0.nrows - 1):
            # print("行下表：" + str(rx))
            # ['国临版编码', '国临版名称', '医保版2.0编码', '医保版2.0名称']
            rows = sh0.row_values(rx + 1)
            # print(rows)
            arr.append(rows)

        return arr

    # 创建sql
    def createSql(self, arr, insert_table_name):
        with open("./icd10.sql", "a+") as icd10File:
            baseSql = "insert into {0}(national_name, national_code, medicare_name, medicare_code,code) values('{1}','{2}','{3}','{4}','{5}')\n"
            eq_count = 0
            for cols in arr:
                code = "no-eq"
                if cols[0] == cols[2] and cols[1] == cols[3]:
                    eq_count += 1
                    code = "eq"
                sql = baseSql.format(insert_table_name, cols[0], cols[1], cols[2], cols[3], code)
                icd10File.write(sql)
            print("总数：{0};相等的数量{1}".format(len(arr), eq_count))


if __name__ == '__main__':
    Icd10("/Users/awen/Desktop/ICD10国临版2.0与医保版2.0对照库.xlsx", "icd10")
