import multiprocessing
import atexit
import signal
import cv2
import matplotlib
matplotlib.use('Agg')  # 非GUIバックエンドを使用
from src.server.server_function import get_video_frame_count
from src.client.browser_launcher import close_chrome, handle_exit
from src.server.hls_server import get_video_bitrate
from main_system import admin_judge, mp4_file_create_selection, network_interface, hls_file_delete_and_create_slection, h264_compressing_selection, videostreaming_selection

# 管理者権限でスクリプトを再実行
admin_judge()

# プログラム終了時に呼び出される関数を登録
atexit.register(close_chrome)
signal.signal(signal.SIGINT, handle_exit)
signal.signal(signal.SIGTERM, handle_exit)

if __name__ == "__main__":
    input_video = "Assets/input_video-1.mp4"
    segment_dir="segments/segmented_video"
    hls_dir = "segments/hls_file"
    res_path = "h264_outputs/res.mp4"
    m3u8_playlist_url = "segments/hls_file/master.m3u8"
    monitor_queue = multiprocessing.Queue()
    input_frame = int(get_video_frame_count(input_video))
    video_bitrate = get_video_bitrate(res_path)
    cap = cv2.VideoCapture(input_video) # cv2.VideoCaptureで動画のプロパティを取得
    if not cap.isOpened():
        print(f"Error: Unable to open video file {input_video}")
        exit(1)
    # 動画の幅と高さを取得
    window_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) 
    window_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap.release()  # リソースを解放

    # Step1: ネットワークインターフェイスを取得し、ネットワーク環境を動的に制限する
    interface = network_interface()
    
    # Step2: H.264ファイルが存在するかをチェック
    h264_compressing_selection(res_path, input_video, window_width, window_height)

    # Step3: MP4セグメントが生成されいるか確認し、再生成するか否か確認する
    mp4_file_create_selection(input_video, input_frame, res_path, window_width, window_height)

    # Step4: HLSファイルを削除するか否か選択
    hls_file_delete_and_create_slection(hls_dir, segment_dir, video_bitrate)

    # Step5: ビデオストリーミング方法を選択
    videostreaming_selection(input_video, input_frame, res_path, 
                                window_width, window_height, hls_dir, 
                                interface, monitor_queue, m3u8_playlist_url
                                )