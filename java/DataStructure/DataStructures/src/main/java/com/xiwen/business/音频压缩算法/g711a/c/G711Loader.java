package com.xiwen.business.音频压缩算法.g711a.c;

import java.io.*;

public class G711Loader {
    // 动态库名称（Windows为g711.dll，Linux为libg711.so）
    private static final String LIBRARY_NAME = "g711";
    private static final String DLL_FILE_NAME = LIBRARY_NAME + ".dll";
    private static final String C_SOURCE_FILE = "G711.c";
    private static boolean isLoaded = false;

    // 静态块：自动加载库
    static {
        try {
            loadLibrary();
        } catch (Exception e) {
            System.err.println("加载G711库失败: " + e.getMessage());
            e.printStackTrace();
        }
    }

    /**
     * 加载G711库，如果不存在则尝试编译
     */
    public static synchronized void loadLibrary() throws Exception {
        if (isLoaded) return;

        // 检查是否已存在DLL
        File dllFile = new File(DLL_FILE_NAME);
        if (!dllFile.exists() || !dllFile.isFile()) {
            System.out.println("未找到" + DLL_FILE_NAME + "，尝试编译...");
            
            // 检查C源文件是否存在
            File cFile = new File(C_SOURCE_FILE);
            if (!cFile.exists() || !cFile.isFile()) {
                throw new FileNotFoundException("找不到C源文件: " + C_SOURCE_FILE);
            }

            // 编译C代码生成DLL
            compileCSource();
            
            // 再次检查编译是否成功
            if (!dllFile.exists()) {
                throw new IOException("编译失败，未生成" + DLL_FILE_NAME);
            }
        }

        // 加载动态库
        System.load(new File(DLL_FILE_NAME).getAbsolutePath());
        isLoaded = true;
        System.out.println(DLL_FILE_NAME + "加载成功");
    }

    /**
     * 调用系统命令编译C源文件为DLL
     */
    private static void compileCSource() throws Exception {
        // 检查操作系统是否为Windows（仅支持Windows编译）
        String os = System.getProperty("os.name").toLowerCase();
        if (!os.contains("win")) {
            throw new UnsupportedOperationException("仅支持Windows系统自动编译，其他系统请手动编译");
        }

        // 检查是否安装了MinGW（gcc编译器）
        if (!hasGccCompiler()) {
            throw new RuntimeException("未找到gcc编译器，请安装MinGW并配置到PATH环境变量");
        }

        // 获取JDK安装路径（用于找到jni.h头文件）
        String javaHome = System.getenv("JAVA_HOME");
        if (javaHome == null || javaHome.isEmpty()) {
            throw new RuntimeException("未设置JAVA_HOME环境变量");
        }

        // 编译命令：使用gcc编译G711.c为g711.dll
        String includePath1 = javaHome + File.separator + "include";
        String includePath2 = includePath1 + File.separator + "win32";
        
        // 构建编译命令
        String[] cmd = {
            "gcc",
            "-shared",
            "-o", DLL_FILE_NAME,
            C_SOURCE_FILE,
            "-I" + includePath1,
            "-I" + includePath2,
            "-Wl,--add-stdcall-alias"
        };

        // 执行编译命令
        System.out.println("执行编译命令: " + String.join(" ", cmd));
        Process process = Runtime.getRuntime().exec(cmd);
        
        // 捕获编译输出
        String output = readStream(process.getInputStream());
        String error = readStream(process.getErrorStream());
        
        // 等待编译完成
        int exitCode = process.waitFor();
        
        // 输出编译结果
        System.out.println("编译输出: " + output);
        if (exitCode != 0) {
            throw new RuntimeException("编译失败，错误信息: " + error);
        }
        System.out.println("编译成功，生成" + DLL_FILE_NAME);
    }

    /**
     * 检查系统是否安装了gcc编译器
     */
    private static boolean hasGccCompiler() {
        try {
            // 执行gcc --version检查是否存在
            Process process = Runtime.getRuntime().exec("gcc --version");
            process.waitFor();
            return process.exitValue() == 0;
        } catch (Exception e) {
            return false;
        }
    }

    /**
     * 读取输入流内容
     */
    private static String readStream(InputStream is) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(is));
        StringBuilder sb = new StringBuilder();
        String line;
        while ((line = br.readLine()) != null) {
            sb.append(line).append("\n");
        }
        return sb.toString();
    }

    // JNI方法声明
    public native static int alaw2linear(int aVal);
    public native static int linear2alaw(int pcmVal);

    // 测试方法
    public static void main(String[] args) {
        try {
            // 测试值
            int[] testValues = {0, 100, -100, 1000, -1000, 32767, -32768};
            
            for (int val : testValues) {
                int encoded = linear2alaw(val);
                int decoded = alaw2linear(encoded);
                System.out.printf("原始值: %d, 编码后: %d, 解码后: %d, 误差: %d%n",
                        val, encoded, decoded, val - decoded);
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
