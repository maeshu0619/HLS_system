import os
import subprocess

def compress_video_to_h264(input_video, window_width, window_height):
    """
    入力動画をH.264形式に圧縮し、指定された解像度で出力する関数。

    Args:
        input_video (str): 入力動画のパス。
        window_width (int): 出力動画の幅。
        window_height (int): 出力動画の高さ。

    Returns:
        str: 圧縮された動画のファイルパス。
    """
    # 出力ファイルパス
    res_output = "h264_outputs/res.mp4"

    # 出力ディレクトリを作成
    os.makedirs("h264_outputs", exist_ok=True)

    # FFmpegコマンドの作成
    command = [
        "ffmpeg", "-y", "-i", input_video,
        "-vf", f"scale={window_width}:{window_height}",
        "-b:v", "3000k", "-maxrate", "3000k",
        "-bufsize", "2M", "-c:v", "libx264", "-preset", "medium",
        "-tune", "film", res_output
    ]

    # FFmpegを実行
    try:
        print(f"Running FFmpeg for {res_output}...")
        subprocess.run(command, capture_output=True, text=True, check=True)
        print(f"Created {res_output}")
    except subprocess.CalledProcessError as e:
        print(f"Error during FFmpeg execution: {e.stderr}")
        raise

    return res_output
