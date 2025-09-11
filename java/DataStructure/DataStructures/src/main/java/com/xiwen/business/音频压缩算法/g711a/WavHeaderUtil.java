package com.xiwen.business.音频压缩算法.g711a;

import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.nio.charset.StandardCharsets;
import java.util.Arrays;

/**
 * 生成标准WAV头（确保fmt子块符合RIFF规范，带严格校验）
 */
public class WavHeaderUtil {
    // 核心标识（必须严格匹配，fmt后有空格！）
    public static final byte[] RIFF_ID = "RIFF".getBytes(StandardCharsets.US_ASCII);
    public static final byte[] WAVE_ID = "WAVE".getBytes(StandardCharsets.US_ASCII);
    public static final byte[] FMT_ID = "fmt ".getBytes(StandardCharsets.US_ASCII); // 末尾空格不可省略
    public static final byte[] DATA_ID = "data".getBytes(StandardCharsets.US_ASCII);

    // PCM固定参数（与解析逻辑对齐）
    private static final short AUDIO_FORMAT = 1;     // 1=PCM未压缩
    private static final short CHANNELS = 1;         // 单声道
    private static final int SAMPLE_RATE = 8000;     // 8000Hz采样率
    private static final short BITS_PER_SAMPLE = 16; // 16位采样
    private static final int BYTE_RATE = SAMPLE_RATE * CHANNELS * (BITS_PER_SAMPLE / 8); // 16000
    private static final short BLOCK_ALIGN = (short) (CHANNELS * (BITS_PER_SAMPLE / 8)); // 2
    private static final int FMT_CHUNK_SIZE = 16;    // PCM的fmt子块大小固定16字节

    /**
     * 为PCM数据添加标准WAV头（生成后自动校验fmt子块）
     * @param pcmData 原始PCM数据（16位、单声道、8000Hz）
     * @return 带完整WAV头的音频数据
     */
    public static byte[] addWavHeader(byte[] pcmData) throws IOException {
        // 校验PCM数据合法性
        if (pcmData == null || pcmData.length == 0) {
            throw new IllegalArgumentException("PCM数据不能为空！");
        }

        // 1. 计算WAV各部分大小（严格遵循RIFF格式公式）
        int dataChunkSize = pcmData.length;                  // data子块数据长度
        int riffChunkSize = 4 + (8 + FMT_CHUNK_SIZE) + (8 + dataChunkSize); // RIFF块大小=WAVE(4) + fmt子块(24) + data子块(8+dataSize)
        int totalWavSize = 4 + riffChunkSize;               // 总大小=RIFF标识(4) + RIFF块大小

        // 2. 按顺序写入WAV头（顺序不可乱！）
        ByteArrayOutputStream out = new ByteArrayOutputStream(totalWavSize);
        // ① RIFF块（0-11字节）
        out.write(RIFF_ID);                                  // 0-3：RIFF标识
        out.write(intToLittleEndian(riffChunkSize));          // 4-7：RIFF块大小（小端序）
        out.write(WAVE_ID);                                  // 8-11：WAVE标识
        // ② fmt子块（12-35字节，标准24字节）
        out.write(FMT_ID);                                   // 12-15：fmt 标识（带空格）
        out.write(intToLittleEndian(FMT_CHUNK_SIZE));         // 16-19：fmt子块大小（16）
        out.write(shortToLittleEndian(AUDIO_FORMAT));         // 20-21：PCM格式（1）
        out.write(shortToLittleEndian(CHANNELS));             // 22-23：单声道（1）
        out.write(intToLittleEndian(SAMPLE_RATE));            // 24-27：8000Hz采样率
        out.write(intToLittleEndian(BYTE_RATE));              // 28-31：字节率（16000）
        out.write(shortToLittleEndian(BLOCK_ALIGN));          // 32-33：块对齐（2）
        out.write(shortToLittleEndian(BITS_PER_SAMPLE));      // 34-35：16位采样
        // ③ data子块（36字节后）
        out.write(DATA_ID);                                   // 36-39：data标识
        out.write(intToLittleEndian(dataChunkSize));          // 40-43：data数据长度
        out.write(pcmData);                                   // 44+：PCM原始数据

        // 3. 生成后校验（提前发现fmt子块问题）
        byte[] wavData = out.toByteArray();
        validateFmtSubchunk(wavData);
        return wavData;
    }

    /**
     * 校验WAV数据中的fmt子块是否合规
     */
    public static void validateFmtSubchunk(byte[] wavData) throws IOException {
        // 校验1：至少包含完整fmt子块（36字节）
        if (wavData.length < 36) {
            throw new IOException("WAV数据过短（需≥36字节，实际：" + wavData.length + "字节），无完整fmt子块！");
        }

        // 校验2：提取12-15字节的fmt标识（标准位置）
        byte[] actualFmtId = new byte[4];
        System.arraycopy(wavData, 12, actualFmtId, 0, 4);

        // 校验3：对比标准fmt标识（含空格）
        if (!Arrays.equals(actualFmtId, FMT_ID)) {
            throw new IOException(
                    "fmt子块标识错误！\n" +
                            "预期：'" + new String(FMT_ID, StandardCharsets.US_ASCII) + "'（十六进制：" + bytesToHex(FMT_ID) + "）\n" +
                            "实际：'" + new String(actualFmtId, StandardCharsets.US_ASCII) + "'（十六进制：" + bytesToHex(actualFmtId) + "）\n" +
                            "原因：生成时可能漏写fmt末尾的空格！"
            );
        }

//        System.out.println("✅ fmt子块标识校验通过！");
    }

    // 工具方法：int转小端字节数组
    public static byte[] intToLittleEndian(int value) {
        return ByteBuffer.allocate(4).order(ByteOrder.LITTLE_ENDIAN).putInt(value).array();
    }

    // 工具方法：short转小端字节数组
    public static byte[] shortToLittleEndian(short value) {
        return ByteBuffer.allocate(2).order(ByteOrder.LITTLE_ENDIAN).putShort(value).array();
    }

    // 工具方法：字节数组转十六进制（调试用）
    public static String bytesToHex(byte[] bytes) {
        StringBuilder sb = new StringBuilder();
        for (byte b : bytes) {
            sb.append(String.format("%02X ", b));
        }
        return sb.toString().trim();
    }
}