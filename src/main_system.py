import os
import json
import time
import ctypes
import sys
import multiprocessing
from src.network_controller import NetworkController
from src.utils import get_network_interfaces
from src.server.mp4_creater import mp4_create
from src.client.cleanup_segments import clear_hls_segments
from src.server.hls_server import create_hls_with_dynamic_bitrate
from src.server.h264_compression import compress_video_to_h264
from src.server.server_operator import start_video_streaming
from src.client.client_operator import start_video_playback
from src.monitor_videostreaming import start_monitor_network

def network_interface():
    print("Available network interfaces:")
    interfaces = get_network_interfaces()  # ネットワークインターフェースを取得
    for idx, iface in enumerate(interfaces):
        print(f"{idx}: {iface}")

    if not interfaces:
        print("No network interfaces detected. Please check your system settings.")
        print("Debug: Ensure you are running the script with administrative privileges.")
        exit(1)


    # 入力の検証を追加
    while True:
        try:
            selected_idx = input("Select the interface to configure: ")
            if selected_idx.strip() == "":
                print("Input cannot be empty. Please enter a valid number.")
                continue
            selected_idx = int(selected_idx)
            if selected_idx < 0 or selected_idx >= len(interfaces):
                print("Invalid selection. Please choose a number from the list.")
                continue
            break
        except ValueError:
            print("Invalid input. Please enter a number.")

    interface = interfaces[selected_idx]
    print(f"Selected interface: {interface}")

    # 設定値を読み込む
    with open("src/config.json", "r") as config_file:
        config = json.load(config_file)

    # ネットワーク設定を適用
    controller = NetworkController(interface)
    controller.apply_settings(rate=config.get("rate"), delay=config.get("delay"), loss=config.get("loss"))

    return interface

def mp4_file_create_selection(input_video, input_frame, res_path, window_width, window_height):
    while True:
        user_input = input("\nDo you want to create or recreate MP4 segments? (y/n): ").strip().lower()
        if user_input == 'y':
            try:
                mp4_create(input_video, input_frame, res_path, window_width, window_height)
                print('MP4 Segments Creating done')
                break
            except Exception as e:
                print(f'MP4 Segments Creating failed: {e}')
                break
        elif user_input == 'n':
            print("Execution skipped.")
            break
        else:
            print("Invalid input. Please enter 'y' or 'n'.")

def hls_file_delete_and_create_slection(hls_dir, segment_dir, video_bitrate):
    if os.path.exists(hls_dir):
        while True:
            user_input = input("\nThe HLS File already exists. Do you want to delete it? (y/n): ").strip().lower()
            if user_input == 'y':
                try:
                    clear_hls_segments(hls_dir)
                    print('clear_hls_segments done')

                    while True:
                        user_input = input("\nThe HLS File was deleted. Do you want to create it now? (y/n): ").strip().lower()
                        if user_input == 'y':
                            # セグメントディレクトリ内の動画ファイルを取得
                            segment_files = [
                                f for f in os.listdir(segment_dir)
                                if f.endswith(".mp4")
                            ]
                            segment_count = len(segment_files)
                            if segment_count == 0:
                                print("No segment files found in the segment directory.")
                                break

                            print(f"Found {segment_count} segment files. Starting HLS generation...")
                            for segment_index, segment_file in enumerate(sorted(segment_files)):
                                try:
                                    segment_path = os.path.join(segment_dir, segment_file)
                                    hls_output_dir = "segments/hls_file"
                                    resolutions = [(640, 360), (1280, 720), (1920, 1080)]  # 解像度リスト
                                    
                                    # HLS生成
                                    create_hls_with_dynamic_bitrate(segment_path, hls_output_dir, resolutions, video_bitrate)
                                    print(f"HLSファイルを生成しました: {hls_output_dir} for segment {segment_index + 1}/{segment_count}")

                                except Exception as e:
                                    print(f'Video Encoding for HLS failed for {segment_file}: {e}')
                            break

                        elif user_input == 'n':
                            print("HLS generation skipped.")
                            break
                        else:
                            print("Invalid input. Please enter 'y' or 'n'.")
                    break

                except Exception as e:
                    print(f'clear_hls_segments failed: {e}')
            elif user_input == 'n':
                print("Execution skipped.")
                break
            else:
                print("Invalid input. Please enter 'y' or 'n'.")
    else:
        while True:
            user_input = input("\nThe HLS File was not exist. Do you want to create it now? (y/n): ").strip().lower()
            if user_input == 'y':
                # セグメントディレクトリ内の動画ファイルを取得
                segment_files = [
                    f for f in os.listdir(segment_dir)
                    if f.endswith(".mp4")
                ]
                segment_count = len(segment_files)
                if segment_count == 0:
                    print("No segment files found in the segment directory.")
                    break

                print(f"Found {segment_count} segment files. Starting HLS generation...")
                for segment_index, segment_file in enumerate(sorted(segment_files)):
                    try:
                        segment_path = os.path.join(segment_dir, segment_file)
                        hls_output_dir = "segments/hls_file"
                        resolutions = [(640, 360), (1280, 720), (1920, 1080)]  # 解像度リスト
                        
                        # HLS生成
                        create_hls_with_dynamic_bitrate(segment_path, hls_output_dir, resolutions, video_bitrate)
                        print(f"HLSファイルを生成しました: {hls_output_dir} for segment {segment_index + 1}/{segment_count}")

                    except Exception as e:
                        print(f'Video Encoding for HLS failed for {segment_file}: {e}')
                break

            elif user_input == 'n':
                print("HLS generation skipped.")
                break
            else:
                print("Invalid input. Please enter 'y' or 'n'.")

def h264_compressing_selection(res_path, input_video, window_width, window_height):
    if os.path.exists(res_path):
        while True:
            user_input = input("\nThe H.264 Compression already done. Do you want to execute H.264 Compression? (y/n): ").strip().lower()
            if user_input == 'y':
                try:
                    # フォビエイテッド圧縮を実行
                    res_path = compress_video_to_h264(input_video, window_width, window_height)
                except Exception as e:
                    print(f"Error during H.264 Compression: {e}")
                    break
                break  # 正常終了
            elif user_input == 'n':
                #print("Execution skipped.")
                break
            else:
                print("Invalid input. Please enter 'y' or 'n'.")
    else:
        try:
            res_path = compress_video_to_h264(input_video, window_width, window_height)
            print("H.264 Compression done")
        except Exception as e:
            print(f"H.264 Compressioon failed: {e}")

def videostreaming_selection(input_video, input_frame, res_path, 
                             window_width, window_height, hls_dir, 
                             interface, monitor_queue, m3u8_playlist_url
                             ):
    try:
        video_streaming_process = multiprocessing.Process(
            target=start_video_streaming,
            args=(input_video, input_frame, res_path, window_width, window_height)
        )
        video_playback_process = multiprocessing.Process(
            target=start_video_playback,
            args=(hls_dir,)
        )
        monitor_process = multiprocessing.Process(
            target=start_monitor_network,
            args=("http://localhost:8080/master.m3u8", interface, monitor_queue)
        )

        # プロセス開始
        # ファイルが存在するかをチェック
        if os.path.exists(m3u8_playlist_url):  # m3u8_playlist_urlが存在する場合
            while True:
                user_input = input("\nDo you want to execute Realtime Streaming function? (y/n): ").strip().lower()
                if user_input == 'y':
                    try:
                        print('Executing VideoStreaming and VideoPlayback simultaneously...')
                        # 並行してプロセスを開始
                        video_streaming_process.start()
                        video_playback_process.start()
                        monitor_process.start()

                        # プロセスの終了を待機
                        video_streaming_process.join()
                        video_playback_process.join()
                        monitor_process.join()
                    except Exception as e:
                        print(f"Error during VideoStreaming or VideoPlayback process: {e}")
                    break  # 正常終了
                elif user_input == 'n':
                    try:
                        print('Executing VideoPlayback only...')
                        video_playback_process.start()
                        monitor_process.start() 
                        
                        video_playback_process.join()
                        monitor_process.join()
                    except Exception as e:
                        print(f"Error during VideoPlayback process: {e}")
                    break
                else:
                    print("Invalid input. Please enter 'y' or 'n'.")
        else:
            print(f"{m3u8_playlist_url} does not exist. Starting VideoStreaming and VideoPlayback simultaneously.")
            try:
                # 並行してプロセスを開始
                video_streaming_process.start()
                video_playback_process.start()
                monitor_process.start() 

                # プロセスの終了を待機
                video_streaming_process.join()
                video_playback_process.join()
                monitor_process.join()
            except Exception as e:
                print(f"Error during VideoStreaming or VideoPlayback process: {e}")

        # メインループで待機
        print("Press Ctrl+C to exit.")
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("Exiting program...")
        video_streaming_process.terminate()
        video_playback_process.terminate()
        monitor_process.terminate()
    
    except Exception as e:
        print(f"Error during process execution: {e}")

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def admin_judge():
    if not is_admin():
        print("Restarting script as administrator...")
        try:
            # 管理者権限でスクリプトを再実行
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        except Exception as e:
            print(f"Failed to restart script as administrator: {e}")
        print("Press Enter to exit...")
        input()  # ターミナルが閉じないよう待機
        sys.exit(0)