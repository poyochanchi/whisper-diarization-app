# whisper-diarization-app

## 開発中のコンテナ起動コマンド
docker run --gpus all -p 5000:5000 --env-file .env   -v ${PWD}/app_with_model_cache.py:/app/app_with_model_cache.py   -v ${PWD}/templates:/app/templates   -v ${PWD}/static:/app/static   -v ${HOME}/.cache:/root/.cache   whisper-diarization-gpu