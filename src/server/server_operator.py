"""
セグメントが独立してデコードできるため、用意する動画のフレームはIフレームのみにし、P,Bフレームは取り扱わないのが
最も好ましい。しかし、現在は全てのフレームを参照するようになっている。
"""

import cv2
import os
from src.server.server_function import get_video_bitrate
from src.server.server_function import frame_segmented
from src.client.playback.logger import VideoLogger
from src.bar_making import ProgressBar

class VideoStreaming:
    def __init__(self, input_video, input_frame, res_path, window_width, window_height):
        self.cap = cv2.VideoCapture(res_path)
        self.input_frame = input_frame
        self.gaze_log = VideoLogger(log_dir="logs/gaze_prediction")
        self.progress_bar = ProgressBar(input_frame=self.input_frame)

        self.window_width = window_width
        self.window_height = window_height

        self.segment_dir = os.path.abspath("segments/segmented_video")
        os.makedirs(self.segment_dir, exist_ok=True)

        self.fps = 30
        self.frame_counter = 0

        self.video_bitrate = get_video_bitrate(res_path)
    
    def run(self):
        while self.frame_counter < self.input_frame:
            ret, frame = self.cap.read()

            if not (ret):
                break

            frame_segmented(frame, self.input_frame, self.video_bitrate, self.fps, self.segment_dir)

            self.frame_counter += 1
            #self.progress_bar.update(self.frame_counter)

        self.cap.release()


def start_video_streaming(input_video, input_flame, res_path, window_width, window_height):
    """
    VideoStreaming の実行
    """
    video_streaming = VideoStreaming(input_video, input_flame, res_path, window_width, window_height)
    video_streaming.run()