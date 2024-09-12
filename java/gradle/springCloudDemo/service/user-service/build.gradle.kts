import org.jetbrains.kotlin.gradle.utils.RUNTIME

val springCloudVersion by extra("2022.0.4")
group = "com.work"
version = "0.0.1-SNAPSHOT"

springBoot{
    mainClass.set("com.work.UserApplication")
}
dependencies {
    api(project(":common:bean"))
    implementation("org.springframework.boot:spring-boot-starter-web")
    implementation("org.springframework.cloud:spring-cloud-starter-openfeign")
    implementation("com.alibaba.cloud:spring-cloud-starter-alibaba-nacos-discovery")
}

//kotlin {
//    jvmToolchain(17)
//}