let mediaRecorder;
let audioChunks = [];
let recordedBlob = null;

const startBtn = document.getElementById('startBtn');
const stopBtn = document.getElementById('stopBtn');
const submitBtn = document.getElementById('submitBtn');
const fileInput = document.getElementById('fileInput');
const statusEl = document.getElementById('statusMessage');
const audioPlayback = document.getElementById('audioPlayback');
const transcriptSection = document.getElementById('transcriptionSection');
const transcriptText = document.getElementById('transcription');
const summaryText = document.getElementById('summary');

startBtn.onclick = async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);
    audioChunks = [];
    mediaRecorder.start();

    mediaRecorder.ondataavailable = e => {
        audioChunks.push(e.data);
    };

    mediaRecorder.onstop = () => {
        recordedBlob = new Blob(audioChunks, { type: 'audio/webm' });
        const url = URL.createObjectURL(recordedBlob);
        audioPlayback.src = url;
        submitBtn.disabled = false;
        statusEl.innerText = "🎤 録音完了！音声を確認できます。";
    };

    startBtn.disabled = true;
    stopBtn.disabled = false;
    statusEl.innerText = "🎙️ 録音中...";
};

stopBtn.onclick = () => {
    mediaRecorder.stop();
    startBtn.disabled = false;
    stopBtn.disabled = true;
};

fileInput.onchange = () => {
    const file = fileInput.files[0];
    if (file) {
        recordedBlob = file;
        const url = URL.createObjectURL(file);
        audioPlayback.src = url;
        submitBtn.disabled = false;
        statusEl.innerText = "📂 ファイルを読み込みました。音声を確認できます。";
    }
};

submitBtn.onclick = async () => {
    const form = document.getElementById('metaForm');
    const formData = new FormData(form);
    formData.append('audio', recordedBlob, 'input.webm');

    statusEl.innerText = "⏳ 処理中...（音声送信中）";
    submitBtn.disabled = true;

    try {
        const response = await fetch('/process', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        statusEl.innerText = "🤖 WhisperとGPTで解析中...";

        const result = await response.json();

        if (result.error) {
            statusEl.innerText = "❌ エラーが発生しました: " + result.error;
            transcriptText.innerText = "";
            summaryText.innerText = "";
        } else {
            statusEl.innerText = "🎉 議事録の生成が完了しました！";
            transcriptText.innerText = result.transcription;
            summaryText.innerText = result.summary;
            transcriptSection.open = false; // 折りたたみ状態で初期化
        }
    } catch (err) {
        console.error(err);
        statusEl.innerText = "❌ 通信エラーが発生しました。もう一度お試しください。";
    } finally {
        submitBtn.disabled = false;
    }
};