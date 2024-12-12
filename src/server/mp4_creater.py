import cv2
import os
import subprocess
import traceback
from src.server.hls_server import get_video_bitrate
from src.client.playback.logger import VideoLogger
from src.bar_making import ProgressBar
    
frame_buffer = []
segment_index = 0

def mp4_create(input_video, input_frame, res_path, window_width, window_height):
    cap = cv2.VideoCapture(res_path)
    gaze_log = VideoLogger(log_dir="logs/gaze_prediction")
    progress_bar = ProgressBar(input_frame=input_frame)

    window_width = window_width
    window_height = window_height

    segment_dir = os.path.abspath("segments/segmented_video")
    os.makedirs(segment_dir, exist_ok=True)

    fps = 30
    frame_counter = 0

    video_bitrate = get_video_bitrate(res_path)
    while frame_counter < input_frame:
        ret, frame = cap.read()

        if not (ret):
            break

        mp4_create_frame_segmented(frame, input_frame, video_bitrate, fps, segment_dir)

        frame_counter += 1
        progress_bar.update(frame_counter)

    cap.release()

def mp4_create_frame_segmented(combined_frame, input_frame, video_bitrate, fps, segment_dir="segments/segmented_video", segment_duration=6):
    """
    合成フレームをセグメント化します。

    Args:
        combined_frame (np.ndarray): 合成されたフレーム。
        input_frame (int): 1セグメントあたりのフレーム数。
        video_bitrate (str): ビットレート（例: "3000k"）。
        fps (int): 動画のフレームレート。
        segment_dir (str): セグメントファイルを保存するディレクトリ。
        segment_duration (int): セグメントの長さ（秒単位）。
    """
    global frame_buffer, segment_index

    # セグメントディレクトリを作成
    segment_dir = os.path.abspath(segment_dir)
    os.makedirs(segment_dir, exist_ok=True)

    thirty_sec = fps * 30

    frame_buffer.append(combined_frame)

    # フレームが規定数に達したらセグメントを保存
    if len(frame_buffer) >= thirty_sec:
        segment_path = os.path.join(segment_dir, f"segment_{segment_index:04d}.mp4")
        temp_raw_file = os.path.join(segment_dir, f"segment_{segment_index:04d}_raw.mp4")

        try:
            # OpenCVを使用して一時ファイルを作成
            height, width, _ = frame_buffer[0].shape
            out = cv2.VideoWriter(temp_raw_file, cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height))
            for frame in frame_buffer:
                out.write(frame)
            out.release()

            print(f"未エンコードセグメントを保存しました: {temp_raw_file}")

            # FFmpegを使用してエンコード
            video_bitrate_str = f"{video_bitrate}k" if isinstance(video_bitrate, int) else video_bitrate
            ffmpeg_command = [
                "ffmpeg", "-y", "-i", temp_raw_file,
                "-c:v", "libx264", "-preset", "fast",
                "-b:v", video_bitrate_str, "-maxrate", video_bitrate_str,
                "-bufsize", "3M", segment_path
            ]
            subprocess.run(ffmpeg_command, check=True)

            print(f"セグメントを保存しました: {segment_path}")

            # 一時ファイルを削除
            os.remove(temp_raw_file)

        except Exception as e:
            print(f"セグメント保存エラー: {segment_path}")
            print(traceback.format_exc())
            frame_buffer.clear()
            return False

        # フレームバッファをクリアし、次のセグメントの準備
        frame_buffer.clear()
        segment_index += 1
        return True

    return False
