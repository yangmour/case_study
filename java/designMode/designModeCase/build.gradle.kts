plugins {
    id("java")
    id("org.springframework.boot") version "3.0.2"
    id("io.spring.dependency-management") version "1.1.0"
    kotlin("jvm") version "1.9.0"  // 你当前使用的 Kotlin 版本
    kotlin("plugin.spring") version "1.9.0"

}

group = "com.work"
version = "1.0-SNAPSHOT"

//springBoot{
//    mainClass.set("com.work.Application")
//}
repositories {
    mavenLocal()
    maven {
        setUrl("https://maven.aliyun.com/repository/public/")
    }
    mavenCentral()
}

dependencies {
    testImplementation(platform("org.junit:junit-bom:5.10.0"))
    testImplementation("org.junit.jupiter:junit-jupiter")
    implementation("org.springframework.boot:spring-boot-starter-web")
    implementation("org.springframework.boot:spring-boot-starter-test")
    implementation("com.alibaba.fastjson2:fastjson2:2.0.52")
    compileOnly("org.projectlombok:lombok:1.18.34")
    implementation("cn.hutool:hutool-all:5.8.32")

}

tasks.test {
    useJUnitPlatform()
}