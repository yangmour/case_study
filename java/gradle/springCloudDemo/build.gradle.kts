// springboot统一管理版本
plugins {
    id("org.springframework.boot") version "3.0.2"
    id("io.spring.dependency-management") version "1.1.0"
    id("java")
    kotlin("jvm") version "1.9.0"
    kotlin("plugin.spring") version "1.9.0"
}


val springCloudVersion: String by extra("2022.0.5")
val springCloudAliBabaVersion: String by extra("2022.0.0.0-RC2")
val groovyVersion: String by extra("4.0.22")

group = "com.work"
version = "0.0.1-SNAPSHOT"

// 所有项目通用配置
allprojects {

    apply(plugin = "java")
    apply(plugin = "java-library")

    // java版本
    java {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    // 设置maven路径
    repositories {
        mavenLocal()
        maven {
            setUrl("https://maven.aliyun.com/repository/public/")
        }
//        maven {
//            url ("https://maven.aliyun.com/repository/central")
//        }
        mavenCentral()
    }

    configurations {
        compileOnly {
//            extendsFrom annotationProcessor
            extendsFrom(configurations.annotationProcessor.get())
        }
    }
}
// 子项目配置
subprojects {

    apply(plugin = "org.springframework.boot")
    apply(plugin = "io.spring.dependency-management")
    apply(plugin = "groovy")
    apply(plugin = "org.jetbrains.kotlin.jvm")
    apply(plugin = "org.jetbrains.kotlin.plugin.spring")

    dependencyManagement {
        imports {
            mavenBom("org.springframework.cloud:spring-cloud-dependencies:${springCloudVersion}")
            mavenBom("com.alibaba.cloud:spring-cloud-alibaba-dependencies:${springCloudAliBabaVersion}")
        }
    }

    dependencies {
        implementation("org.apache.groovy:groovy:${groovyVersion}")
        implementation("com.alibaba.fastjson2:fastjson2:2.0.52")
        compileOnly(group = "org.projectlombok", name = "lombok", version = "1.18.30")
    }

    tasks.withType<GroovyCompile> {
        sourceCompatibility = "17"
        targetCompatibility = "17"
        // 指定 Groovy 文件的位置
        source = fileTree("src/main/java").matching {
            include("**/*.groovy") // 只包含 .groovy 文件
        }
        groovyOptions.forkOptions.jvmArgs = listOf("-Dgroovy.parameters=true")
    }
}


