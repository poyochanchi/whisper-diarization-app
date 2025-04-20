#!/bin/bash

# プロジェクト名の指定（カレントディレクトリ名を取得）
PROJECT_NAME=$(basename "$PWD")

# 1. Git 初期化
git init
echo "✅ Git リポジトリ初期化済み"

# 2. .gitignore を作成（Python/Docker向けの基本形）
cat <<EOF > .gitignore
__pycache__/
*.pyc
*.pyo
.env
*.env
*.log
venv/
.envrc
.DS_Store
*.sqlite3
*.db
*.egg-info/
docker-compose.override.yml
EOF
echo "✅ .gitignore 作成済み"

# 3. README.md を作成
echo "# $PROJECT_NAME" > README.md
echo "✅ README.md 作成済み"

# 4. 初回コミット
git add .
git commit -m "初期コミット"
echo "✅ 初回コミット完了"

# 5. GitHub CLIでログイン確認（未ログインなら実行される）
gh auth status || gh auth login

# 6. GitHub リポジトリ作成＆プッシュ
gh repo create "$PROJECT_NAME" --private --source=. --push
echo "✅ GitHub リポジトリ作成＆初回プッシュ完了"
