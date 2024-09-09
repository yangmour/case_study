import org.springframework.boot.gradle.tasks.bundling.BootJar

group = "com.work"
version = "0.0.1-SNAPSHOT"

tasks.named<BootJar>("bootJar") {
    enabled = false
}

dependencies {
//    implementation("org.springframework.boot:spring-boot-starter-web")

}

