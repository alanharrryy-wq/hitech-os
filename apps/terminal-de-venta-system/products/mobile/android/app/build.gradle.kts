plugins {
    id("com.android.application") version "8.7.3"
}

android {
    namespace = "com.prisma.pos.mobile"
    compileSdk = 35

    defaultConfig {
        applicationId = "com.prisma.pos.mobile"
        minSdk = 23
        targetSdk = 35
        versionCode = 8
        versionName = "0.8.0"
    }
}

dependencies {
    implementation("com.google.androidbrowserhelper:androidbrowserhelper:2.5.0")
}
