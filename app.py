import os
import tempfile
from flask import Flask, request, render_template, jsonify
from werkzeug.utils import secure_filename
import whisper
from pydub import AudioSegment
from pyannote.audio import Pipeline
from openai import OpenAI
import ffmpeg
from dotenv import load_dotenv

# 環境変数読み込み
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN")

client = OpenAI(api_key=OPENAI_API_KEY)

app = Flask(__name__)

# Whisperモデルのキャッシュ辞書
global_whisper_model_cache = {}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/process", methods=["POST"])
def process():
    try:
        title = request.form.get("title", "無題の会議")
        datetime = request.form.get("datetime", "不明な日時")
        participants = request.form.get("participants", "未入力")
        whisper_model_name = request.form.get("whisper_model", "base")
        gpt_model_name = request.form.get("gpt_model", "gpt-4")

        audio_file = request.files["audio"]
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as temp_input:
            audio_file.save(temp_input.name)
            wav_path = temp_input.name.replace(".webm", ".wav")
            ffmpeg.input(temp_input.name).output(
                wav_path, format='wav', acodec='pcm_s16le', ac=1, ar='16000'
            ).run(overwrite_output=True)

        # Whisperモデルをキャッシュから取得またはロード
        global global_whisper_model_cache
        if whisper_model_name not in global_whisper_model_cache:
            global_whisper_model_cache[whisper_model_name] = whisper.load_model(whisper_model_name)
        whisper_model = global_whisper_model_cache[whisper_model_name]

        speaker_pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization@2.1",
            use_auth_token=HUGGINGFACE_TOKEN
        )
        diarization = speaker_pipeline(wav_path)
        audio = AudioSegment.from_file(wav_path)
        transcript_parts = []

        for turn, _, speaker in diarization.itertracks(yield_label=True):
            duration = turn.end - turn.start
            if duration < 0.5:
                continue

            segment = audio[turn.start * 1000: turn.end * 1000]
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as seg_file:
                segment.export(seg_file.name, format="wav")
                result = whisper_model.transcribe(seg_file.name)
                transcript_parts.append(f"[{speaker}] {result['text'].strip()}")
                os.unlink(seg_file.name)

        os.unlink(temp_input.name)
        os.unlink(wav_path)

        full_transcript = "\n".join(transcript_parts)

        prompt = f"""
以下は、ある会議の内容を話者別に書き起こしたものです。これを読みやすい日本語の議事録形式にまとめてください。

会議名: {title}
日時: {datetime}
参加者: {participants}

発言記録:
{full_transcript}

--- 出力形式の例 ---
・議題ごとの要約（あれば）
・各発言内容を要点で箇条書き
・アクションアイテム（ToDo）があれば明示
-------------------
"""

        response = client.chat.completions.create(
            model=gpt_model_name,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )

        summary = response.choices[0].message.content

        return jsonify({
            "transcription": full_transcript,
            "summary": summary
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
