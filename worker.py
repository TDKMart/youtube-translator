from celery import Celery
import subprocess, os

app = Celery("worker", broker="redis://redis:6379/0", backend="redis://redis:6379/0")

@app.task
def process_video(url, target_lang, job_id):
    try:
        output_dir = f"/tmp/{job_id}"
        os.makedirs(output_dir, exist_ok=True)

        audio = f"{output_dir}/audio.mp3"
        subprocess.run(["yt-dlp", "-x", "--audio-format", "mp3", "-o", audio, url])

        transcript = f"{output_dir}/transcript.txt"
        subprocess.run(["whisper", audio, "--model", "base", "--output_format", "txt", "--output_dir", output_dir])

        with open(transcript) as f:
            text = f.read()

        translated = f"{output_dir}/translated.txt"
        subprocess.run(["argos-translate", "--from-lang", "en", "--to-lang", target_lang, "--text", text], stdout=open(translated, "w"))

        with open(translated) as f:
            translated_text = f.read()

        tts_path = f"{output_dir}/tts.wav"
        subprocess.run(["tts", "--text", translated_text, "--out_path", tts_path])

        final_video = f"{output_dir}/output.mp4"
        subprocess.run(["ffmpeg", "-i", audio, "-i", tts_path, "-c:v", "copy", "-map", "0:v:0", "-map", "1:a:0", "-shortest", final_video])

        return "done"

    except Exception as e:
        print(f"[ERROR] {e}")
        return "error"