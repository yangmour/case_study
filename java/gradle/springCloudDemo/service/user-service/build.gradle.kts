
group = "com.work"
version = "0.0.1-SNAPSHOT"

springBoot{
    mainClass.set("com.work.UserApplication")
}
dependencies {
    api(project(":common:bean"))
    implementation("org.springframework.boot:spring-boot-starter-web")
}

//kotlin {
//    jvmToolchain(17)
//}