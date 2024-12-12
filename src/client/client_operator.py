from src.client.hls_client import serve_hls


class VidepPlayback:
    def __init__(self, hls_dir):
        # Directory containing the HLS files (e.g., playlist.m3u8 and .ts files)
        self.output_dir = "segments/hls_file"
        # Path to save the HTML file
        self.html_file = "segments/hls_file/live-stream.html"
        # URL to the HLS playlist
        self.m3u8_playlist_url = "http://localhost:8080/master.m3u8"

    def run(self):
        running = True

        while running:
            serve_hls(
                output_directory="segments/hls_file",
                html_template_path="src/client/playback/hls_template.html",
                html_file_path="segments/hls_file/live-stream.html",
                m3u8_url="http://localhost:8080/master.m3u8"
            )

def start_video_playback(hls_dir):
    """
    VideoPlayback の実行
    """
    client_operator = VidepPlayback(hls_dir)
    client_operator.run()