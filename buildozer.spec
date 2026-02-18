[app]

# (str) Title of your application
title = 马年祝福

# (str) Package name
package.name = horsebless

# (str) Package domain (needed for android/ios packaging)
package.domain = www.sjinyu.com

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas

# (str) Application versioning (method 1)
version = 1.0.2

# (list) Application requirements
requirements = python3,kivy,plyer

# (str) Custom source folders for requirements
#requirements.source.kivy = ../../kivy

# (str) Presplash of the application
#presplash.filename = %(source.dir)s/data/presplash.png

# (str) Icon of the application
icon.filename = images/bless.png

# (str) Supported orientation (one of landscape, portrait, or all)
orientation = portrait

# (bool) Indicate if the application should be fullscreen
fullscreen = 1

# (bool) Indicate if the application can be debugged
debug = 1

# (bool) Enable the use of the Android support library (androidx)
android.enable_androidx = True

# (list) Android permissions
android.permissions = INTERNET

# (int) Android API to use
android.api = 31

# (int) Minimum API required
android.minapi = 21

# (int) Android SDK version to use
#android.sdk = 31

# (str) Android NDK version to use
android.ndk = 25b

# (bool) Use --private data storage (True) or --dir public storage (False)
android.private_storage = True

# (str) Android NDK directory (if empty, it will be automatically downloaded)
#android.ndk_path =

# (str) Android SDK directory (if empty, it will be automatically downloaded)
#android.sdk_path =

# (str) ANT directory (if empty, it will be automatically downloaded)
#android.ant_path =

# (bool) If True, then skip trying to update the Android sdk
# This can be useful to avoid excess Internet downloads or save time
#android.accept_sdk_license = False

# (str) Android entry point, default is 'org.kivy.android.PythonActivity'
#android.entrypoint = org.kivy.android.PythonActivity

# (list) List of Java .jar files to add to the libs so that pyjnius can access
# their classes. Don't add jars that you do not need, since extra jars can slow
# down the build process. Allows wildcards matching, for example:
# java/libs = *.jar
#android.add_src =

# (str) Path to a custom AndroidManifest.xml file
#android.manifest =

# (str) Path to a custom source folder for your android project
#android.sources =

# (list) Python modules to compile to .pyc
#android.copy_python_sources =

# (list) List of Android gradle dependencies to compile
#android.gradle_dependencies = 'com.android.support:appcompat-v7:26.0.0'

# (bool) Enable AndroidX support. Enable when 'android.gradle_dependencies' includes an AndroidX library
#android.use_androidx = True

# (str) The Android arch to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
android.archs = arm64-v8a, armeabi-v7a

# (int) Override the default `android.sdk` API level (31) used to compile the
# native Python objects
#android.ndk_api = 21

# (bool) Add gstreamer support
#android.gstreamer = True

# (str) Path to a custom Android project template
#android.project_template =

# (str) Value to set for `android:debuggable` in AndroidManifest.xml
#android.debuggable = True

# (bool) Enable verbose build
#android.verbose = False

# -------------------- Android signing and release build --------------------
# (str) Path to the keystore file (must exist)
android.keystore = ./my-release-key.keystore

# (str) Keystore alias
android.keystore_alias = my-key-alias

# (str) Password for the keystore
android.keystore_password = 123456

# (str) Password for the key alias
android.keyalias_password = 123456

# (bool) If True, then the build will be a release build (not debug)
#android.release = True

# (str) Path to a custom private key to use when signing
#android.private_key =

# (str) Path to a custom certificate to use when signing
#android.certificate =

# (list) Android ABI splits to include
#android.abi_splits = armeabi-v7a, arm64-v8a

# (bool) If True, then the app will be built as a multi-APK (multiple APKs for
# different ABIs)
#android.multiapk = False

# -------------------- Android APK splits --------------------

# -------------------- iOS specific --------------------

# (str) Path to a custom kivy-ios folder
#ios.kivy_ios_dir = ../kivy-ios

# (str) Name of the certificate to use for signing the debug version
# Get a list of available identities: buildozer ios list_identities
#ios.codesign.debug = "iPhone Developer: <lastname> <firstname> (<hexstring>)"

# (str) Name of the certificate to use for signing the release version
#ios.codesign.release = %(ios.codesign.debug)s

# (list) Architecture to build for, for ios
#ios.archs = armv7, arm64

# (str) Path to a custom Xcode project template
#ios.xcode_template =

# -------------------- Windows specific --------------------

# (str) Path to a custom project template
#windows.project_template =

# (str) The major version of the current Python installation
#python3.version = 3.10

# -------------------- Requirements customization --------------------

# (str) Path to a custom pip requirements file
#requirements.source = requirements.txt

# (str) Path to a custom Python recipe folder
#recipes =

# -------------------- Buildozer global configuration --------------------

# (int) Log level (0 = error only, 1 = info, 2 = debug)
log_level = 2

# (bool) Prefer the use of the cache (default: True)
#use_cache = True

# (bool) Prefer the use of the ccache (default: False)
#use_ccache = False

# (str) Path to the build directory
#build_dir = ./.buildozer

# (str) Path to the bin directory (generated APKs)
#bin_dir = ./bin

# (str) Path to the Android SDK
#android.sdk_path =

# (str) Path to the Android NDK
#android.ndk_path =

# (str) Path to the Android ANT
#android.ant_path =

# (str) Path to the Java JDK
#java.jdk_path =

# -------------------- Command line options --------------------
