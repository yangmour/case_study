package com.atguigu.file.demo1;

import com.atguigu.file.demo1.upload.UploadController;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.util.DigestUtils;

import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.RandomAccessFile;

/**
 * Author:huzhongkui
 * Date: 2024-04-26  12:59
 */
@SpringBootTest
public class ApiTest {

    @Autowired
    private UploadController uploadController;

    @Test
    public void uploadFile() throws IOException {
        // 原文件路径
        String sourcePath = "D:\\test\\test.mp4";
        // 本地分块文件存储路径
        String localChunkFilePath = "D:\\test\\data\\";
        String sourceMd5 = DigestUtils.md5DigestAsHex(new FileInputStream(sourcePath));
        // 进行上传文件的读&&写操作
        int chunkTotal = fileToChunk(sourcePath, localChunkFilePath);
        int i = 0;
        for (; i < chunkTotal; i++) {
            boolean isSuccess = uploadController.checkChunks(sourceMd5, i);
            if (isSuccess) {
                // 分块目录在存在 代表已上传过
                System.out.println(i + "号分块已经上传成功");
            } else {
                // 分块在本地指定目录上不存在，则进行上传
                isSuccess = uploadController.uploadChunks(sourceMd5, i, localChunkFilePath + i);
                if (isSuccess) {
                    System.out.println("执行上传" + i + "号分块成功");
                } else {// 如果当前上传的这一块出现了问题 后面所有的分块都不在上传  包括后续的合并 因为对于要合并后的源文件来说是没有一点意义。
                    System.out.println("执行上传" + i + "号分块失败");
                    break;
                }
            }
        }
        // 4.如果上传过程中没有任何问题，d代表分片都上传问完毕，可以合并分块
        if (i == chunkTotal) {
            System.out.println("所有分块均上传成功，开始合并分块");
            boolean isSuccess = uploadController.mergeChunks(sourceMd5, chunkTotal, sourcePath);
            if (isSuccess) {
                System.out.println("合并分块成功");
            } else {
                System.out.println("合并分块失败");
            }
        }
    }

    /**
     * 文件分块
     */
    public int fileToChunk(String sourcePath, String localChunkFilePath) throws IOException {
        File sourceFile = new File(sourcePath);
        int chunkSize = 1024 * 1024 * 5;// 分块大小
        int chunkNum = (int) Math.ceil(sourceFile.length() * 1.0 / chunkSize);// 分块数
        // 操作文件的底层对象&&读取指定的文件
        RandomAccessFile raf_r = new RandomAccessFile(sourceFile, "r");
        // 创建一个缓冲池
        byte[] bytes = new byte[1024];
        for (int i = 0; i < chunkNum; i++) {
            File chunkFile = new File(localChunkFilePath + i);
            // 将文件片写到指定的目录下
            RandomAccessFile rw = new RandomAccessFile(chunkFile, "rw");
            int len = -1;
            boolean isFull = false;
            // 缓冲区没有写满
            while ((len = raf_r.read(bytes)) != -1) {
                rw.write(bytes, 0, len);
                // 当上传的文件大小比缓冲区的大小大，则代表这一轮5mb写完了 退出循环 写下一轮
                if (chunkFile.length() >= chunkSize) {
                    System.out.println("第" + i + "个分块的大小：" + chunkFile.length() + "byte");
                    isFull = true;
                    break;
                }
            }
            // 最后不足5mb的写完 做个打印
            if (!isFull && chunkFile.length() != 0) {
                System.out.println("第" + i + "个分块的大小：" + chunkFile.length() + "byte");
            }
            rw.close();
        }
        raf_r.close();
        return chunkNum;
    }
}
