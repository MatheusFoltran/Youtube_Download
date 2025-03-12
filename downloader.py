import yt_dlp
import os

def download(url, out_path, audio_only=True):
    ydl_opts = {
        'outtmpl': os.path.join(out_path, '%(title)s.%(ext)s'),
        'quiet': False,
    }
    
    if audio_only:
        ydl_opts.update({
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        })
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        return info_dict.get('title', 'Título desconhecido')

# Exemplo de uso:
# download("URL_DO_VIDEO", "D:/USUARIO/Matheus/Music", audio_only=True)