package com.xiwen.business.音频压缩算法.g711a;

public class G711Java {
    private static final int SIGN_BIT = 0x80;      /* Sign bit for a A-law byte. */  
    private static final int QUANT_MASK = 0xf;     /* Quantization field mask.   */  
    private static final int NSEGS = 8;            /* Number of A-law segments.  */  
    private static final int SEG_SHIFT = 4;        /* Left shift for segment number. */  
    private static final int SEG_MASK = 0x70;      /* Segment field mask. */  
    
    private static final short[] segEnd = {0xFF, 0x1FF, 0x3FF, 0x7FF,  
                                           0xFFF, 0x1FFF, 0x3FFF, 0x7FFF};

    // 修改 u2a 数组类型为 int[]，支持 128
    private static final int[] u2a = { /* u- to A-law conversions */
            1,  1,  2,  2,  3,  3,  4,  4,
            5,  5,  6,  6,  7,  7,  8,  8,
            9,  10, 11, 12, 13, 14, 15, 16,
            17, 18, 19, 20, 21, 22, 23, 24,
            25, 27, 29, 31, 33, 34, 35, 36,
            37, 38, 39, 40, 41, 42, 43, 44,
            46, 48, 49, 50, 51, 52, 53, 54,
            55, 56, 57, 58, 59, 60, 61, 62,
            64, 65, 66, 67, 68, 69, 70, 71,
            72, 73, 74, 75, 76, 77, 78, 79,
            81, 82, 83, 84, 85, 86, 87, 88,
            89, 90, 91, 92, 93, 94, 95, 96,
            97, 98, 99, 100,101,102,103,104,
            105,106,107,108,109,110,111,112,
            113,114,115,116,117,118,119,120,
            121,122,123,124,125,126,127,128  // 128 正常存储
    };

    private static final byte[] a2u = { /* A- to u-law conversions */  
        1,  3,  5,  7,  9,  11, 13, 15,  
        16, 17, 18, 19, 20, 21, 22, 23,  
        24, 25, 26, 27, 28, 29, 30, 31,  
        32, 32, 33, 33, 34, 34, 35, 35,  
        36, 37, 38, 39, 40, 41, 42, 43,  
        44, 45, 46, 47, 48, 48, 49, 49,  
        50, 51, 52, 53, 54, 55, 56, 57,  
        58, 59, 60, 61, 62, 63, 64, 64,  
        65, 66, 67, 68, 69, 70, 71, 72,  
        73, 74, 75, 76, 77, 78, 79, 79,  
        80, 81, 82, 83, 84, 85, 86, 87,  
        88, 89, 90, 91, 92, 93, 94, 95,  
        96, 97, 98, 99, 100,101,102,103,  
        104,105,106,107,108,109,110,111,  
        112,113,114,115,116,117,118,119,  
        120,121,122,123,124,125,126,127  
    };  
    
    private static int search(int val, short[] table, int size) {  
        for (int i = 0; i < size; i++) {  
            if (val <= table[i])  
                return i;  
        }  
        return size;  
    }  
    
    /**
     * 将16位线性PCM值转换为8位A-law编码
     * @param pcmVal 输入值，范围：-32768~32767
     * @return 8位A-law编码值
     */
    public static int linear2alaw(int pcmVal) {  
        int mask;  
        int seg;  
        int aval;  

        if (pcmVal >= 0) {  
            mask = 0xD5;        /* 符号位(第7位) = 1 */  
        } else {  
            mask = 0x55;        /* 符号位 = 0 */  
            pcmVal = -pcmVal - 1;  
        }  

        seg = search(pcmVal, segEnd, 8);  

        if (seg >= 8) {  
            return 0x7F ^ mask;  
        } else {  
            aval = seg << SEG_SHIFT;  
            if (seg < 2) {  
                aval |= (pcmVal >> 4) & QUANT_MASK;  
            } else {  
                aval |= (pcmVal >> (seg + 3)) & QUANT_MASK;  
            }  
            return aval ^ mask;  
        }  
    }  
    
    /**
     * 将A-law编码值转换为16位线性PCM
     * @param aVal 8位A-law编码值
     * @return 16位线性PCM值
     */
    public static int alaw2linear(int aVal) {  
        int t;  
        int seg;  

        aVal ^= 0x55;  

        t = (aVal & QUANT_MASK) << 4;  
        seg = (aVal & SEG_MASK) >> SEG_SHIFT;  
        
        switch (seg) {  
            case 0:  
                t += 8;  
                break;  
            case 1:  
                t += 0x108;  
                break;  
            default:  
                t += 0x108;  
                t <<= seg - 1;  
        }  
        
        return ((aVal & SIGN_BIT) != 0) ? t : -t;  
    }  
    
    // 测试方法
    public static void main(String[] args) {
        // 测试值范围覆盖各种情况
        int[] testValues = {0, 1, -1, 10, -10, 100, -100, 
                           1000, -1000, 8191, -8191, 
                           32767, -32768};
        
        System.out.println("测试G.711 A-law编解码:");
        System.out.println("原始值\t编码后\t解码后\t误差");
        System.out.println("---------------------------");
        
        for (int val : testValues) {
            int encoded = linear2alaw(val);
            int decoded = alaw2linear(encoded);
            int error = val - decoded;
            
            System.out.printf("%d\t%d\t%d\t%d%n", val, encoded, decoded, error);
        }
    }
}
