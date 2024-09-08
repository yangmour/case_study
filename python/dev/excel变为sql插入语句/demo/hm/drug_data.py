from decimal import Decimal, ROUND_HALF_UP

import xlrd

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import binascii


class DrugData:
    def __init__(self, path, insert_table_name,key=None):
        self.workbook = xlrd.open_workbook(path)
        arr = self.parse()
        self.createSql(arr, insert_table_name, key)

    # 解析数据
    def parse(self):
        sh0 = self.workbook.sheet_by_index(0)
        print("{0} {1} {2}".format(sh0.name, sh0.nrows, sh0.ncols))
        print("Cell D30 is {0}".format(sh0.cell_value(rowx=2, colx=3)))
        arr = []
        for rx in range(sh0.nrows - 1):
            # print("行下表：" + str(rx))
            # 货品id	货品品名	规格	生产厂商	全局零售价	处方标识
            rows = sh0.row_values(rx + 1)
            # print(rows)
            arr.append(rows)

        return arr

    # 创建sql
    def createSql(self, arr, insert_table_name, key):
        with open("./drug_data.sql", "a+") as icd10File:
            baseSql = "insert into {0}(product_number, name, sku, manufacturer,price,type) values('{1}','{2}','{3}','{4}','{5}','{6}');\n"
            sm4 = Sm4(key)

            for cols in arr:
                d = Decimal(cols[4] * 100)
                rounded_d = d.to_integral(rounding=ROUND_HALF_UP)
                print(rounded_d)
                sql = baseSql.format(insert_table_name,
                                     sm4.sm4_encrypt_ecb(str(cols[0]).replace(".0", "")),
                                     sm4.sm4_encrypt_ecb(cols[1]),
                                     sm4.sm4_encrypt_ecb(cols[2]),
                                     sm4.sm4_encrypt_ecb(cols[3]),
                                     sm4.sm4_encrypt_ecb(str(rounded_d)),
                                     sm4.sm4_encrypt_ecb(cols[5]))
                icd10File.write(sql)


class Sm4:
    def __init__(self,key):
        self.key = key
    def sm4_encrypt_ecb(self, data):
        # cipher = Cipher(algorithms.SM4(binascii.unhexlify(self.key)), modes.ECB(), backend=default_backend())
        cipher = Cipher(algorithms.SM4(bytes(self.key, 'utf-8')), modes.ECB(), backend=default_backend())
        encryptor = cipher.encryptor()

        # Use PKCS7 padding
        data_bytes = data.encode('utf-8')
        padded_data = data_bytes + bytes([16 - len(data_bytes) % 16] * (16 - len(data_bytes) % 16))

        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        return binascii.hexlify(ciphertext).decode('utf-8')

    def sm4_decrypt_ecb(self, ciphertext):
        cipher = Cipher(algorithms.SM4(binascii.unhexlify(self.key)), modes.ECB(), backend=default_backend())
        decryptor = cipher.decryptor()

        decrypted_data = decryptor.update(binascii.unhexlify(ciphertext)) + decryptor.finalize()

        # Remove PKCS7 padding
        return decrypted_data.rstrip(b'\x00').decode('utf-8')


if __name__ == '__main__':
    DrugData("/Users/awen/Desktop/dev/重药/重药数据/目录 20240630.xlsx", "hm_drug_data","a02fea5344df88d7")
