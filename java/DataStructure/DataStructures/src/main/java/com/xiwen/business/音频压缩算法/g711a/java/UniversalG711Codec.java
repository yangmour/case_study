package com.xiwen.business.音频压缩算法.g711a.java;

import com.xiwen.business.音频压缩算法.g711a.java.G711Java;
import org.apache.commons.lang3.StringUtils;
import org.apache.commons.lang3.exception.ExceptionUtils;
import org.springframework.mock.web.MockMultipartFile;

import java.io.*;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.UUID;

/**
 * 通用G.711编解码工具，支持：
 * 输入：File / InputStream / byte[]（PCM或标准16位PCM WAV）
 * 输出：File / OutputStream / byte[]（G.711或PCM/WAV）
 * 注：A-law编解码算法已替换为调用G711Java类实现，μ-law保留原实现
 */
public class UniversalG711Codec {
    // 编码类型枚举（A-law/μ-law）
    public enum CodecType {
        ALAW, ULAW
    }

    // 默认缓冲区大小（4KB，2的幂数，适配系统IO效率）
    private static final int DEFAULT_BUFFER_SIZE = 4096;
    // WAV标准PCM头长度（44字节）
    private static final int WAV_PCM_HEADER_SIZE = 44;
    // μ-law编码偏置值（标准G.711定义）
    private static final int ULAW_BIAS = 33024;

    /**
     * 压缩：PCM数据（字节数组）→ G.711字节数组
     * @param pcmData 16位PCM字节数组（小端字节序）
     * @param codecType 编码类型（ALAW/ULAW）
     * @return 压缩后的G.711字节数组
     */
    public static byte[] compressPcm(byte[] pcmData, CodecType codecType) {
        if (pcmData == null || pcmData.length % 2 != 0) {
            throw new IllegalArgumentException("PCM字节数组不能为空且必须为偶数字节（16位样本）");
        }
        try (ByteArrayOutputStream out = new ByteArrayOutputStream()) {
            compressPcm(new ByteArrayInputStream(pcmData), out, codecType, DEFAULT_BUFFER_SIZE);
            return out.toByteArray();
        } catch (IOException e) {
            throw new RuntimeException("PCM压缩失败", e);
        }
    }

    /**
     * 压缩：PCM输入流 → G.711输出流
     * @param pcmIn 16位PCM输入流（小端字节序）
     * @param g711Out G.711输出流（自动关闭）
     * @param codecType 编码类型
     * @param bufferSize 缓冲区大小（需≥2）
     * @throws IOException 流操作异常
     */
    public static void compressPcm(InputStream pcmIn, OutputStream g711Out,
                                   CodecType codecType, int bufferSize) throws IOException {
        if (bufferSize < 2) throw new IllegalArgumentException("缓冲区大小不能小于2字节");

        try { // try-with-resources自动关闭输入输出流
            byte[] buffer = new byte[bufferSize];
            ByteBuffer pcmBuffer = ByteBuffer.wrap(buffer).order(ByteOrder.LITTLE_ENDIAN);
            int bytesRead;

            while ((bytesRead = pcmIn.read(buffer)) != -1) {
                if (bytesRead % 2 != 0) {
                    throw new IOException("PCM流读取到奇数字节（" + bytesRead + "），无法解析16位样本");
                }

                int sampleCount = bytesRead / 2;
                byte[] g711Buffer = new byte[sampleCount];

                for (int i = 0; i < sampleCount; i++) {
                    short pcmSample = pcmBuffer.getShort(i * 2);
                    // 核心改动1：A-law编码调用G711Java.linear2alaw，μ-law保留原实现
                    g711Buffer[i] = (byte) (codecType == CodecType.ALAW
                            ? G711Java.linear2alaw(pcmSample) // 替换为G711Java的A-law编码方法
                            : linear2ulaw(pcmSample));
                }
                g711Out.write(g711Buffer);
            }
            g711Out.flush();
        }finally {
            pcmIn.close();
            g711Out.close();
        }
    }

    /**
     * 压缩：PCM文件 → G.711文件
     * @param pcmFile 16位PCM文件（小端字节序）
     * @param g711File 输出G.711文件（自动创建）
     * @param codecType 编码类型
     * @throws IOException 文件操作异常
     */
    public static void compressPcm(File pcmFile, File g711File, CodecType codecType) throws IOException {
        if (!pcmFile.exists()) throw new FileNotFoundException("PCM输入文件不存在：" + pcmFile.getPath());
        try (
                InputStream in = new FileInputStream(pcmFile);
                OutputStream out = new FileOutputStream(g711File)
        ) {
            compressPcm(in, out, codecType, DEFAULT_BUFFER_SIZE);
        }
    }

    /**
     * 压缩：WAV文件 → G.711字节数组（仅支持标准16位PCM WAV）
     * @param wavFile 标准16位PCM WAV文件
     * @param codecType 编码类型
     * @return 压缩后的G.711字节数组
     * @throws IOException 解析或压缩异常
     */
    public static byte[] compressWav(File wavFile, CodecType codecType) throws IOException {
        if (!wavFile.exists()) throw new FileNotFoundException("WAV输入文件不存在：" + wavFile.getPath());
        try (
                InputStream wavIn = Files.newInputStream(wavFile.toPath());
                ByteArrayOutputStream g711Out = new ByteArrayOutputStream()
        ) {
            compressWav(wavIn, g711Out, codecType);
            return g711Out.toByteArray();
        }
    }

    /**
     * 压缩：WAV输入流 → G.711输出流（仅支持标准16位PCM WAV）
     * @param wavIn 标准16位PCM WAV输入流（自动关闭）
     * @param g711Out G.711输出流（自动关闭）
     * @param codecType 编码类型
     * @throws IOException 解析或压缩异常
     */
    public static void compressWav(InputStream wavIn, OutputStream g711Out, CodecType codecType) throws IOException {
        try {
            // 解析WAV头并校验格式
            WavParams wavParams = parseWavHeader(wavIn);
            // 压缩WAV中的PCM数据（流指针已定位到PCM数据区）
            compressPcm(wavIn, g711Out, codecType, DEFAULT_BUFFER_SIZE);
        } finally {
            wavIn.close();
            g711Out.close();
        }
    }

    /**
     * 解压：G.711字节数组 → PCM字节数组（16位，小端）
     * @param g711Data G.711字节数组（ALAW/ULAW）
     * @param codecType 编码类型
     * @return 解压后的16位PCM字节数组
     */
    public static byte[] decompressG711(byte[] g711Data, CodecType codecType) {
        if (g711Data == null || g711Data.length == 0) {
            throw new IllegalArgumentException("G711字节数组不能为空");
        }
        try (ByteArrayOutputStream out = new ByteArrayOutputStream()) {
            decompressG711(new ByteArrayInputStream(g711Data), out, codecType, DEFAULT_BUFFER_SIZE);
            return out.toByteArray();
        } catch (IOException e) {
            throw new RuntimeException("G711解压失败", e);
        }
    }

    /**
     * 解压：G.711输入流 → PCM输出流（16位，小端）
     * @param g711In G.711输入流（自动关闭）
     * @param pcmOut PCM输出流（自动关闭）
     * @param codecType 编码类型
     * @param bufferSize 缓冲区大小（≥1）
     * @throws IOException 流操作异常
     */
    public static void decompressG711(InputStream g711In, OutputStream pcmOut,
                                      CodecType codecType, int bufferSize) throws IOException {
        if (bufferSize < 1) throw new IllegalArgumentException("缓冲区大小不能小于1字节");

        try { // 自动关闭流
            byte[] g711Buffer = new byte[bufferSize];
            // PCM缓冲区：1个G711字节→2个PCM字节，预分配2倍大小
            ByteBuffer pcmBuffer = ByteBuffer.allocate(bufferSize * 2).order(ByteOrder.LITTLE_ENDIAN);
            int bytesRead;

            while ((bytesRead = g711In.read(g711Buffer)) != -1) {
                pcmBuffer.clear();
                for (int i = 0; i < bytesRead; i++) {
                    // 无符号解析G711字节（避免Java byte负数值问题）
                    int g711Sample = g711Buffer[i] & 0xFF;
                    // 核心改动2：A-law解码调用G711Java.alaw2linear，μ-law保留原实现
                    short pcmSample = (short) (codecType == CodecType.ALAW
                            ? G711Java.alaw2linear(g711Sample) // 替换为G711Java的A-law解码方法
                            : ulaw2linear(g711Sample));
                    pcmBuffer.putShort(pcmSample);
                }
                // 写入实际长度的PCM数据（bytesRead * 2字节）
                pcmOut.write(pcmBuffer.array(), 0, bytesRead * 2);
            }
            pcmOut.flush();
        } finally {
            g711In.close();
            pcmOut.close();
        }
    }

    /**
     * 解压：G.711字节数组 → PCM文件（16位，小端字节序，裸PCM格式）
     * @param g711Data 输入的G.711字节数组（ALAW/ULAW）
     * @param pcmFile 输出的PCM文件（自动创建，若已存在则覆盖）
     * @param codecType 编码类型（需与G.711数据匹配）
     * @throws IOException 文件写入异常或数据处理异常
     */
    public static void decompressG711(byte[] g711Data, File pcmFile, CodecType codecType) throws IOException {
        // 1. 前置校验：避免空数据或无效文件路径
        if (g711Data == null || g711Data.length == 0) {
            throw new IllegalArgumentException("G711字节数组不能为空或空数组");
        }
        if (pcmFile == null) {
            throw new IllegalArgumentException("PCM输出文件不能为空");
        }
        // 确保父目录存在（避免文件路径不存在导致写入失败）
        File parentDir = pcmFile.getParentFile();
        if (parentDir != null && !parentDir.exists()) {
            if (!parentDir.mkdirs()) {
                throw new IOException("无法创建PCM文件的父目录：" + parentDir.getPath());
            }
        }

        // 2. 核心逻辑：G711字节数组→PCM字节流→写入文件
        // 用try-with-resources自动关闭流，确保数据刷盘
        try (
                // 将G711字节数组转为输入流
                InputStream g711In = new ByteArrayInputStream(g711Data);
                // 打开PCM文件输出流（覆盖已有文件）
                OutputStream pcmOut = Files.newOutputStream(pcmFile.toPath())
        ) {
            // 调用底层解压方法：G711输入流→PCM输出流（确保小端字节序）
            decompressG711(g711In, pcmOut, codecType, DEFAULT_BUFFER_SIZE);

            // 额外确保数据全部写入磁盘（避免缓冲区滞留）
            pcmOut.flush();
        }

        // 3. 验证文件完整性（可选，增强可靠性）
        long expectedFileSize = g711Data.length * 2; // 1个G711字节→2个PCM字节
        long actualFileSize = pcmFile.length();
        if (actualFileSize != expectedFileSize) {
            throw new IOException("PCM文件写入不完整！预期大小：" + expectedFileSize
                    + "字节，实际大小：" + actualFileSize + "字节");
        }
        System.out.println("G711→PCM文件转换完成：" + pcmFile.getPath()
                + "（大小：" + actualFileSize + "字节）");
    }

    /**
     * 解压：G.711字节数组 → WAV文件（生成标准16位PCM WAV）
     * @param g711Data G.711原始字节数组
     * @param wavFile 输出WAV文件（自动创建）
     * @param codecType 编码类型
     * @param sampleRate 采样率（需与压缩前一致）
     * @param numChannels 声道数（需与压缩前一致，1/2）
     * @throws IOException 生成WAV异常
     */
    public static void decompressToWav(byte[] g711Data, File wavFile, CodecType codecType,
                                       int sampleRate, short numChannels) throws IOException {
        if (sampleRate <= 0) throw new IllegalArgumentException("采样率必须为正数：" + sampleRate);
        if (numChannels != 1 && numChannels != 2) {
            throw new IllegalArgumentException("仅支持单声道（1）或立体声（2），当前：" + numChannels);
        }
        // PCM数据大小 = G711长度 × 2（1个G711字节→2个PCM字节）
        int pcmDataSize = g711Data.length * 2;
        WavParams wavParams = new WavParams(numChannels, sampleRate, pcmDataSize);

        try (
                InputStream g711In = new ByteArrayInputStream(g711Data);
                FileOutputStream wavOut = new FileOutputStream(wavFile)
        ) {
            // 1. 写入WAV头
            wavOut.write(createWavHeader(wavParams));
            // 2. 解压G711并写入PCM数据
            decompressG711(g711In, wavOut, codecType, DEFAULT_BUFFER_SIZE);
        }
    }

    // ------------------------------
    // 内部工具方法：WAV解析与生成
    // ------------------------------

    // WAV文件标识的十六进制常量（大端序）
    private static final int RIFF_MARKER = 0x52494646; // "RIFF"
    private static final int WAVE_MARKER = 0x57415645; // "WAVE"
    private static final int FMT_MARKER = 0x666D7420;  // "fmt "（带空格）
    private static final int DATA_MARKER = 0x64617461; // "data"
    /**
     * 解析WAV文件头，提取关键参数并验证格式（修复data子块位置计算错误）
     */
    public static WavParams parseWavHeader(InputStream wavIn) throws IOException {
        // 1. 初始化缓冲区（足够容纳标准WAV头）
        byte[] header = new byte[2048];
        int totalRead = 0;
        int requiredMinLength = 44; // 基础头大小

        // 读取足够字节覆盖基础头
        while (totalRead < requiredMinLength) {
            int read = wavIn.read(header, totalRead, header.length - totalRead);
            if (read == -1) {
                throw new IOException("WAV文件头不完整！需至少" + requiredMinLength + "字节，实际读" + totalRead + "字节");
            }
            totalRead += read;
        }

        // 2. 分离标识和参数的字节序Buffer
        ByteBuffer markerBuffer = ByteBuffer.wrap(header).order(ByteOrder.BIG_ENDIAN); // 标识用大端序
        ByteBuffer paramBuffer = ByteBuffer.wrap(header).order(ByteOrder.LITTLE_ENDIAN); // 参数用小端序

        // 3. 验证RIFF和WAVE标识
        if (markerBuffer.getInt() != RIFF_MARKER) {
            throw new IOException("不是标准WAV文件（RIFF标识错误）");
        }
        if (markerBuffer.getInt(8) != WAVE_MARKER) {
            throw new IOException("不是标准WAV文件（WAVE标识错误）");
        }

        // 4. 解析fmt子块（正确计算data子块位置）
        int fmtPosition = 12; // fmt子块起始位置（固定）

        // 验证fmt标识
        if (markerBuffer.getInt(fmtPosition) != FMT_MARKER) {
            throw new IOException("WAV格式不支持（无fmt子块）");
        }

        // 提取fmt子块大小（subchunk1Size）
        int subchunk1Size = paramBuffer.getInt(fmtPosition + 4);

        // -------------------------- 关键修复：正确计算data子块位置 --------------------------
        // fmt子块总长度 = 4字节标识 + 4字节大小 + subchunk1Size字节内容 = 8 + subchunk1Size
        int dataPosition = fmtPosition + 8 + subchunk1Size; // 修正：+8而非+4
        // -----------------------------------------------------------------------------------

        // 确保缓冲区读取到data标识位置
        requiredMinLength = dataPosition + 4; // 至少覆盖data标识的4字节
        if (totalRead < requiredMinLength) {
            while (totalRead < requiredMinLength) {
                int read = wavIn.read(header, totalRead, header.length - totalRead);
                if (read == -1) {
                    throw new IOException("WAV文件头不完整！需" + requiredMinLength + "字节读取data标识");
                }
                totalRead += read;
            }
            // 重新包装Buffer以加载新数据
            markerBuffer = ByteBuffer.wrap(header).order(ByteOrder.BIG_ENDIAN);
            paramBuffer = ByteBuffer.wrap(header).order(ByteOrder.LITTLE_ENDIAN);
        }

        // 5. 验证data子块标识
        int actualDataMarker = markerBuffer.getInt(dataPosition);
        if (actualDataMarker != DATA_MARKER) {
            throw new IOException(
                    "WAV格式不支持（无data子块）！" +
                            "预期data标识（大端序）：0x" + Integer.toHexString(DATA_MARKER).toUpperCase() + "（即\"data\"），" +
                            "实际data位置（" + dataPosition + "字节）标识：0x" + Integer.toHexString(actualDataMarker).toUpperCase()
            );
        }

        // 6. 解析音频参数
        short audioFormat = paramBuffer.getShort(fmtPosition + 8);
        if (audioFormat != 1) {
            throw new IOException("仅支持PCM未压缩格式（AudioFormat=" + audioFormat + "）");
        }

        short numChannels = paramBuffer.getShort(fmtPosition + 10);
        if (numChannels != 1 && numChannels != 2) {
            throw new IOException("仅支持单声道（1）或立体声（2），当前：" + numChannels);
        }

        int sampleRate = paramBuffer.getInt(fmtPosition + 12);
        int dataSize = paramBuffer.getInt(dataPosition + 4);
        if (dataSize <= 0) {
            throw new IOException("WAV文件无有效PCM数据（大小：" + dataSize + "字节）");
        }

        System.out.println("调试：WAV头解析成功！声道数=" + numChannels + "，采样率=" + sampleRate + "Hz");
        return new WavParams(numChannels, sampleRate, dataSize);
    }


    /**
     * 创建标准16位PCM WAV头（44字节）
     * @param params WAV参数（声道数、采样率、数据大小）
     * @return 44字节WAV头字节数组
     */
    private static byte[] createWavHeader(WavParams params) {
        ByteBuffer header = ByteBuffer.allocate(WAV_PCM_HEADER_SIZE).order(ByteOrder.LITTLE_ENDIAN);
        int chunkSize = 36 + params.dataSize;          // ChunkSize = 36 + 数据大小
        int byteRate = params.sampleRate * params.numChannels * 2; // 字节率 = 采样率×声道数×2（16位）
        short blockAlign = (short) (params.numChannels * 2);       // 块对齐 = 声道数×2（16位）

        // 1. RIFF子块
        header.putInt(0x52494646); // ChunkID: "RIFF"
        header.putInt(chunkSize);   // ChunkSize
        header.putInt(0x57415645); // Format: "WAVE"

        // 2. fmt子块
        header.putInt(0x666D7420); // Subchunk1ID: "fmt "
        header.putInt(16);         // Subchunk1Size: 16（PCM标准）
        header.putShort((short) 1); // AudioFormat: 1（PCM）
        header.putShort(params.numChannels); // NumChannels
        header.putInt(params.sampleRate);    // SampleRate
        header.putInt(byteRate);             // ByteRate
        header.putShort(blockAlign);         // BlockAlign
        header.putShort((short) 16);         // BitsPerSample: 16

        // 3. data子块
        header.putInt(0x64617461); // Subchunk2ID: "data"
        header.putInt(params.dataSize);      // Subchunk2Size（PCM数据大小）

        return header.array();
    }

    // ------------------------------
    // G.711编解码实现：保留μ-law（A-law已替换为G711Java调用）
    // ------------------------------

    /**
     * 16位PCM → 8位μ-law编码（标准G.711 μ-law，保留原实现）
     * @param pcm 16位PCM样本（范围：-32768~32767）
     * @return 8位μ-law编码（0~255）
     */
    private static int linear2ulaw(int pcm) {
        final int MAX_PCM = 32767;
        final int MIN_PCM = -32768;

        // 1. 处理溢出
        if (pcm > MAX_PCM) pcm = MAX_PCM;
        if (pcm < MIN_PCM) pcm = MIN_PCM;

        // 2. 提取符号位+加偏置（μ-law特性）
        int sign = 0;
        int p = pcm;
        if (p < 0) {
            p = -p;
            sign = 0x80; // 符号位1为负
        }
        p += ULAW_BIAS; // 加μ-law偏置值

        // 3. 计算指数（找到最高置位）
        int exponent = 0;
        for (int i = 15; i >= 4; i--) { // 从bit15开始检测（跳过低4位量化位）
            if ((p & (1 << i)) != 0) {
                exponent = i - 7; // 指数范围0~7
                break;
            }
        }
        // 确保指数在合法范围
        exponent = Math.max(0, Math.min(7, exponent));

        // 4. 计算量化位（低4位）
        int quantization = (p >> (exponent + 3)) & 0x0F;

        // 5. 拼接μ-law字节：符号位(1) + (7-指数)(3) + 量化位(4)
        return sign | ((7 - exponent) << 4) | quantization;
    }

    /**
     * 8位μ-law → 16位PCM解码（标准G.711 μ-law，保留原实现）
     * @param uLaw 8位μ-law编码（0~255）
     * @return 16位PCM样本（-32768~32767）
     */
    private static int ulaw2linear(int uLaw) {
        uLaw &= 0xFF; // 无符号解析
        // 1. 提取符号位、指数、量化位
        int sign = (uLaw & 0x80) != 0 ? -1 : 1;
        int exponent = 7 - ((uLaw & 0x70) >> 4); // 指数=7 - 段号
        int quantization = uLaw & 0x0F;

        // 2. 标准μ-law解码公式（含偏置修正）
        int pcm = ( (1 << (exponent + 3)) * (quantization + 1) ) + (1 << exponent) - ULAW_BIAS;

        // 3. 溢出保护
        if (pcm > 32767) pcm = 32767;
        if (pcm < -32768) pcm = -32768;

        return sign * pcm;
    }

    // ------------------------------
    // 工具方法：输入流→字节数组
    // ------------------------------

    /**
     * 将输入流转换为字节数组（需调用者关闭输入流）
     * @param inputStream 输入流（未关闭）
     * @param bufferSize 缓冲区大小（≥1）
     * @return 转换后的字节数组
     * @throws IOException 流操作异常
     */
    public static byte[] inputStreamToByteArray(InputStream inputStream, int bufferSize) throws IOException {
        if (inputStream == null) throw new IllegalArgumentException("输入流不能为空");
        if (bufferSize < 1) throw new IllegalArgumentException("缓冲区大小不能小于1字节");

        try (ByteArrayOutputStream outputStream = new ByteArrayOutputStream()) {
            byte[] buffer = new byte[bufferSize];
            int bytesRead;
            while ((bytesRead = inputStream.read(buffer)) != -1) {
                outputStream.write(buffer, 0, bytesRead);
            }
            outputStream.flush();
            return outputStream.toByteArray();
        }
    }

    // ------------------------------
    // WAV参数封装类
    // ------------------------------
    private static class WavParams {
        final short numChannels; // 声道数（1/2）
        final int sampleRate;    // 采样率（Hz）
        final int dataSize;      // PCM数据大小（字节）

        WavParams(short numChannels, int sampleRate, int dataSize) {
            this.numChannels = numChannels;
            this.sampleRate = sampleRate;
            this.dataSize = dataSize;
        }
    }

    /**
     * 将 PCM 文件转换为字节数组（通用文件转字节数组逻辑，不依赖 PCM 格式细节）
     * @param pcmFile 输入的 PCM 文件（需存在且为可读文件）
     * @param bufferSize 缓冲区大小（建议 4096~8192 字节，平衡效率和内存）
     * @return PCM 文件对应的字节数组（二进制数据，保留原始格式如 16 位小端）
     * @throws IOException 文件不存在、权限不足或读取异常
     */
    public static byte[] pcmFileToArray(File pcmFile, int bufferSize) throws IOException {
        // 1. 前置校验：确保文件有效
        if (pcmFile == null) {
            throw new IllegalArgumentException("PCM文件不能为空");
        }
        if (!pcmFile.exists()) {
            throw new FileNotFoundException("PCM文件不存在：" + pcmFile.getAbsolutePath());
        }
        if (!pcmFile.isFile()) {
            throw new IOException("路径不是文件：" + pcmFile.getAbsolutePath());
        }
        if (!pcmFile.canRead()) {
            throw new IOException("无权限读取PCM文件：" + pcmFile.getAbsolutePath());
        }
        if (bufferSize < 1) {
            throw new IllegalArgumentException("缓冲区大小不能小于1字节");
        }

        // 2. 读取文件流并缓冲数据
        Path pcmPath = pcmFile.toPath();
        // try-with-resources 自动关闭流，避免资源泄漏
        try (
                InputStream inputStream = Files.newInputStream(pcmPath); // 高效读取文件流
                ByteArrayOutputStream outputStream = new ByteArrayOutputStream() // 缓冲数据
        ) {
            byte[] buffer = new byte[bufferSize]; // 临时缓冲区
            int bytesRead; // 每次读取的字节数

            // 循环读取文件内容到缓冲区，直到流结束
            while ((bytesRead = inputStream.read(buffer)) != -1) {
                outputStream.write(buffer, 0, bytesRead); // 写入缓冲流（仅写入实际读取的字节）
            }

            outputStream.flush(); // 确保所有数据写入缓冲流
            return outputStream.toByteArray(); // 转换为字节数组
        }
    }

    /**
     * 重载方法：使用默认缓冲区大小（4096字节），简化调用
     */
    public static byte[] pcmFileToArray(File pcmFile) throws IOException {
        return pcmFileToArray(pcmFile, 4096);
    }

    /**
     * 将字节数组转换为输入流（InputStream）
     * @param byteArray 输入字节数组（非空，可用于 G711 数据、PCM 数据等）
     * @return 包装后的输入流（ByteArrayInputStream）
     * @throws IllegalArgumentException 字节数组为空时抛出
     */
    public static InputStream convert(byte[] byteArray) {
        // 前置校验：避免空数组导致后续流读取异常
        if (byteArray == null || byteArray.length == 0) {
            throw new IllegalArgumentException("输入字节数组不能为空或空数组");
        }
        // 核心：通过 ByteArrayInputStream 包装字节数组
        return new ByteArrayInputStream(byteArray);
    }

    /**
     * 重载方法：指定读取起始位置和长度（适用于仅需读取数组部分数据的场景）
     * @param byteArray 输入字节数组
     * @param offset 起始读取索引（从 0 开始）
     * @param length 读取长度（不能超过数组剩余长度）
     * @return 部分数据的输入流
     */
    public static InputStream convert(byte[] byteArray, int offset, int length) {
        if (byteArray == null || byteArray.length == 0) {
            throw new IllegalArgumentException("输入字节数组不能为空或空数组");
        }
        if (offset < 0 || length < 0 || offset + length > byteArray.length) {
            throw new IndexOutOfBoundsException("起始位置或长度超出数组范围");
        }
        return new ByteArrayInputStream(byteArray, offset, length);
    }


    /**
     * 将WAV格式字节数组写入文件，生成可播放的WAV文件
     * @param wavByteArray 完整的WAV格式字节数组（含头信息+PCM数据）
     * @param targetFile 目标WAV文件（如 "output.wav"）
     * @throws IOException 写入失败（路径错误、权限不足等）
     */
    public static void writeWavFile(byte[] wavByteArray, File targetFile) throws IOException {
        // 1. 前置校验：避免空数据或无效文件
        if (wavByteArray == null || wavByteArray.length == 0) {
            throw new IllegalArgumentException("WAV字节数组不能为空或空数组");
        }
        if (targetFile == null) {
            throw new IllegalArgumentException("目标文件不能为空");
        }

        // 2. 确保父目录存在（避免因路径不存在导致写入失败）
        File parentDir = targetFile.getParentFile();
        if (parentDir != null && !parentDir.exists()) {
            boolean dirCreated = parentDir.mkdirs();
            if (!dirCreated) {
                throw new IOException("无法创建父目录：" + parentDir.getAbsolutePath());
            }
        }

        // 3. 将字节数组完整写入文件（核心操作）
        // 使用try-with-resources自动关闭流，确保数据刷盘
        try (OutputStream out = new FileOutputStream(targetFile)) {
            out.write(wavByteArray); // 一次性写入所有字节（WAV头+数据）
            out.flush(); // 强制刷盘，避免数据滞留缓冲区
        }

        // 4. 验证文件完整性（可选，增强可靠性）
        long fileSize = targetFile.length();
        if (fileSize != wavByteArray.length) {
            throw new IOException("WAV文件写入不完整！预期大小：" + wavByteArray.length
                    + "字节，实际大小：" + fileSize + "字节");
        }

        System.out.println("WAV文件生成成功：" + targetFile.getAbsolutePath()
                + "（大小：" + fileSize + "字节）");
    }


    // ------------------------------
    // 测试方法（覆盖核心场景）
    // ------------------------------
    public static void main(String[] args) {
        try {
            // 1. 准备测试文件（替换为你的WAV文件路径）
            File inputWav = new File("input.pcm");
            if (!inputWav.exists()) {
                System.err.println("测试失败：输入WAV文件不存在：" + inputWav.getPath());
                return;
            }

            byte[] pcmFileToArray = UniversalG711Codec.pcmFileToArray(inputWav);

            byte[] wavBytes = WavHeaderUtil.addWavHeader(pcmFileToArray);
            // 指定临时文件存储目录（如当前项目的 temp 文件夹）
            Path tempDir = Paths.get("./temp");
            // 确保目录存在（不存在则创建）
            Files.createDirectories(tempDir);
            Path tempWav = Files.createTempFile(tempDir, "audio_", ".wav");
            try {

                // 使用临时文件（写入内容）
                Files.write(tempWav, wavBytes);
                System.out.println("临时音频文件路径：" + tempWav);

                // 压缩并解压
                CharSequence zipType = "711A";
                if (StringUtils.isNotBlank(zipType) && "711A".equals(zipType)) {
                    // 压缩->解压后数据
                    byte[] pcmByteArray = UniversalG711Codec.wavFile711AConvertPcmByteArray(tempWav.toFile());
                    wavBytes = WavHeaderUtil.addWavHeader(pcmByteArray);

                    // 仅压缩
                } else if (StringUtils.isNotBlank(zipType) && "711Azip".equals(zipType)) {
                    wavBytes = UniversalG711Codec.compressWav(tempWav.toFile(), UniversalG711Codec.CodecType.ALAW);
                }
            } finally {
                // 关键：设置JVM退出时自动删除（防止忘记手动删除）
                tempWav.toFile().deleteOnExit();
                try {
                    Files.deleteIfExists(tempWav); // 立刻删除
                } catch (IOException e) {
                    System.out.println(ExceptionUtils.getStackTrace(e));
                }
            }
            String fileName = UUID.randomUUID().toString().replace("-", "");
            MockMultipartFile mockMultipartFile = new MockMultipartFile("file",
                    fileName,
                    "audio/wav",
                    wavBytes);


            System.out.println("=== 所有测试场景执行完成 ===");

        } catch (Exception e) {
            System.err.println("测试失败：" + e.getMessage());
            System.out.println(ExceptionUtils.getStackTrace(e));
        }
    }

    public static byte[] wavFile711AConvertPcmByteArray(File inputWav) {
        File outputPcm = new File("./temp/output.pcm");

        try {
            // 2. 解析原始WAV参数（采样率、声道数）
            int originalSampleRate;
            short originalChannels;
            try (InputStream tempWavIn = Files.newInputStream(inputWav.toPath())) {
                WavParams originalParams = parseWavHeader(tempWavIn);
                originalSampleRate = originalParams.sampleRate;
                originalChannels = originalParams.numChannels;
            }
            System.out.println("=== 原始WAV参数 ===");
            System.out.println("采样率：" + originalSampleRate + "Hz");
            System.out.println("声道数：" + originalChannels);
            System.out.println("------------------");

            // 3. 场景1：WAV文件 → A-law字节数组  压缩（使用G711Java编码）
            byte[] alawData = compressWav(inputWav, CodecType.ALAW);

            // 4. 场景2：A-law字节数组 → PCM文件 解压（使用G711Java解码）
            decompressG711(alawData, outputPcm, CodecType.ALAW);
            System.out.println("场景2：A-law→PCM文件 完成（路径：" + outputPcm.getPath() + "）");

            byte[] pcmFileToArray = pcmFileToArray(outputPcm);
            return pcmFileToArray;
        } catch (Exception e){
            e.printStackTrace();
            throw new RuntimeException(e);
        }finally {
            try {
                // 清理临时文件
                if (outputPcm.exists()) {
                    Files.delete(outputPcm.toPath());
                }
            } catch (IOException ex) {
                ex.printStackTrace();
            }
        }
    }
}