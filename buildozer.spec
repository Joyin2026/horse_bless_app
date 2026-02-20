name: Build Android APK

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]
  workflow_dispatch:
  
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      # 显示 buildozer.spec 内容，用于验证
      - name: Show buildozer.spec content
        run: cat buildozer.spec

      # 设置 JDK 11（兼容性更好）
      - name: Set up JDK 11
        uses: actions/setup-java@v3
        with:
          distribution: 'temurin'
          java-version: '11'

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'

      - name: Install system dependencies
        run: |
          sudo apt update
          sudo apt install -y \
            git zip unzip openjdk-17-jdk python3-pip \
            autoconf libtool pkg-config zlib1g-dev \
            libncurses5-dev libncursesw5-dev libtinfo5 \
            cmake libffi-dev libssl-dev

      - name: Install buildozer
        run: |
          pip install --upgrade pip
          pip install buildozer cython
          buildozer --version

      # 解码 keystore 文件（从 GitHub Secrets 获取 base64 并生成 .jks 文件）
      - name: Decode keystore
        run: |
          echo "${{ secrets.KEYSTORE_BASE64 }}" | base64 --decode > keystore.jks
          echo "KEYSTORE_FILE=$(pwd)/keystore.jks" >> $GITHUB_ENV

      # 设置签名环境变量（映射 secrets 到 buildozer 需要的变量名）
      - name: Set signature environment variables
        run: |
          echo "KEYSTORE_ALIAS=${{ secrets.KEY_ALIAS }}" >> $GITHUB_ENV
          echo "KEYSTORE_PASS=${{ secrets.KEY_PASSWORD }}" >> $GITHUB_ENV
          echo "KEYALIAS_PASS=${{ secrets.KEY_PASSWORD }}" >> $GITHUB_ENV

      # 验证 keystore 文件是否存在以及环境变量是否设置（可选）
      - name: Verify keystore
        run: |
          ls -l keystore.jks
          echo "KEYSTORE_FILE: $KEYSTORE_FILE"
          echo "KEYSTORE_ALIAS: $KEYSTORE_ALIAS"
          if [ -z "$KEYSTORE_ALIAS" ]; then echo "KEYSTORE_ALIAS is empty"; exit 1; fi
          if [ -z "$KEYSTORE_PASS" ]; then echo "KEYSTORE_PASS is empty"; exit 1; fi

      # 清理构建缓存（可选，确保全新构建）
      - name: Clean buildozer cache
        run: rm -rf ~/.buildozer

      # 主构建命令（使用 release 模式，避免调试提示）
      - name: Build with buildozer
        env:
          GRADLE_OPTS: "-Dorg.gradle.daemon=false -Dorg.gradle.logging.level=debug"
        run: yes | buildozer android release --verbose --log_level=2

      # 上传生成的 APK 作为 artifact
      - name: Upload APK
        uses: actions/upload-artifact@v4
        with:
          name: signed-apk
          path: bin/*.apk
