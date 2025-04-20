FROM ubuntu:22.04

# 必要なパッケージだけをインストール
RUN apt-get update && apt-get install -y \
    python3.10 python3.10-venv python3.10-distutils python3-pip \
    ffmpeg libsndfile1 git curl \
    && ln -sf /usr/bin/python3.10 /usr/bin/python \
    && ln -sf /usr/bin/pip3 /usr/bin/pip \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# 作業ディレクトリと依存インストール
WORKDIR /app
COPY requirements.txt .
RUN python -m pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# アプリコードをコピー（任意）
COPY . .

CMD ["python", "app.py"]
