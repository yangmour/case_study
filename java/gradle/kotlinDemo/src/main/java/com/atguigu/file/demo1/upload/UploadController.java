package com.atguigu.file.demo1.upload;

import com.j256.simplemagic.ContentInfo;
import com.j256.simplemagic.ContentInfoUtil;
import io.minio.*;
import org.apache.commons.compress.utils.IOUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Controller;
import org.springframework.util.DigestUtils;

import java.io.*;
import java.util.List;
import java.util.stream.Collectors;
import java.util.stream.Stream;

@Controller
public class UploadController {

    @Autowired
    MinioClient minioClient;

    @Value("${minio.bucket}")
    private String bucket;

    /**
     * 检查分块是否已经上传

     */
    public boolean checkChunks(String fileMd5, int chunkIndex) {

        String chunkFileFolderPath = getChunkFileFolderPath(fileMd5);
         // 得到每一块文件在minio的路径
        String chunkPath = chunkFileFolderPath + chunkIndex;
        StatObjectArgs statObjectArgs = StatObjectArgs.builder()
                .bucket(bucket)
                .object(chunkPath)
                .build();
        try {
            // 查看文件在minio桶中的指定目录是否存在
            minioClient.statObject(statObjectArgs);
        } catch (Exception e) {
            return false;
        }
        return true;
    }

    /**
     * 上传分块
     *
     */
    public boolean uploadChunks(String fileMd5, int chunkIndex, String localChunkFilePath) {

        // 得到分块上传目录--minio(服务端)
        String chunkPath = getChunkFileFolderPath(fileMd5) + chunkIndex;

        String mimeType = getMimeType(".temp");

        try {
            UploadObjectArgs uploadObjectArgs = UploadObjectArgs.builder()
                    .bucket(bucket) // 存储桶
                    .filename(localChunkFilePath) // 分块文件本地路径---客户端
                    .object(chunkPath) // 对象名（分块路径）
                    .contentType(mimeType) // 设置媒体文件类型
                    .build();

            minioClient.uploadObject(uploadObjectArgs);
        } catch (Exception e) {
            return false;
        }
        return true;
    }

    /**
     * 合并分块
     *
     */
    public boolean mergeChunks(String fileMd5, int chunkTotal, String sourceFileName) {

        String chunkFileFolderPath = getChunkFileFolderPath(fileMd5);

        List<ComposeSource> sources = Stream.iterate(0, i -> ++i)
                .limit(chunkTotal)
                .map(i -> ComposeSource.builder().bucket(bucket).object(chunkFileFolderPath + i).build())
                .collect(Collectors.toList());

        String extension = sourceFileName.substring(sourceFileName.lastIndexOf("."));

        String objectName = getFilePathByMd5(fileMd5, extension);

        ComposeObjectArgs composeObjectArgs = ComposeObjectArgs.builder()
                .bucket(bucket)
                .object(objectName) // 合并后文件的路径（对象名）
                .sources(sources) // 所有分块
                .build();
        try {
            minioClient.composeObject(composeObjectArgs);
        } catch (Exception e) {
            return false;
        }
        // 下载合并后的文件
        File file = downloadFileFromMinIO(objectName);
        try (FileInputStream fileInputStream = new FileInputStream(file)) {
            // 计算合并后文件的md5
//            String mergeFileMd5 = DigestUtils.md5DigestAsHex(fileInputStream);
            // 比较原始md5和合并后文件的md5
//            if (!fileMd5.equals(mergeFileMd5)) {
//                // 合并失败
//                return false;
//            }
            return true;
        } catch (Exception e) {
            // 合并失败
            return false;
        }
    }

    /**
     * 从minio下载文件
     *
     */
    public File downloadFileFromMinIO(String objectName) {
        // 临时文件
        File minioFile = null;
        FileOutputStream outputStream = null;
        try {
            InputStream stream = minioClient.getObject(GetObjectArgs.builder()
                    .bucket(bucket)
                    .object(objectName)
                    .build());
            // 创建临时文件
            minioFile = File.createTempFile("minio", ".merge");
            outputStream = new FileOutputStream(minioFile);
            IOUtils.copy(stream, outputStream);
            return minioFile;
        } catch (Exception e) {
            e.printStackTrace();
        } finally {
            if (outputStream != null) {
                try {
                    outputStream.close();
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
        }
        return null;
    }

    /**
     * 得到分块文件的目录
     *
     */
    private String getChunkFileFolderPath(String fileMd5) {
        return fileMd5.charAt(0) + "/" + fileMd5.charAt(1) + "/" + "chunk" + "/";
    }

    /**
     * 根据扩展名获取mimeType

     */
    private String getMimeType(String extension) {
        if (extension == null) {
            extension = "";
        }
        // 根据扩展名取出mimeType
        ContentInfo extensionMatch = ContentInfoUtil.findExtensionMatch(extension);
        // 通用mimeType，字节流
        String mimeType = MediaType.APPLICATION_OCTET_STREAM_VALUE;
        if (extensionMatch != null) {
            mimeType = extensionMatch.getMimeType();
        }
        return mimeType;
    }

    /**
     * 得到合并后的文件路径

     */
    private String getFilePathByMd5(String fileMd5, String fileExt) {
        return fileMd5.charAt(0) + "/" + fileMd5.charAt(1) + "/" + "file" + "/" + fileMd5 + fileExt;
    }
}
