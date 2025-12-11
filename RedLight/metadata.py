import subprocess
import shutil
from pathlib import Path
from typing import Optional, Dict, List


class MetadataEditor:
    
    def __init__(self):
        self.ffmpeg_available = shutil.which("ffmpeg") is not None
        if not self.ffmpeg_available:
            raise RuntimeError("FFmpeg is required for metadata editing.")
            
    def SetMetadata(
        self,
        video_path: str,
        title: Optional[str] = None,
        artist: Optional[str] = None,
        album: Optional[str] = None,
        description: Optional[str] = None,
        genre: Optional[str] = None,
        date: Optional[str] = None,
        output_path: Optional[str] = None
    ) -> str:
        input_path = Path(video_path)
        if not input_path.exists():
            raise FileNotFoundError(f"Video not found: {video_path}")
            
        if not output_path:
            temp_output = input_path.with_suffix(f".meta{input_path.suffix}")
        else:
            temp_output = Path(output_path)
            
        cmd = [
            'ffmpeg', '-y', '-hide_banner', '-loglevel', 'error',
            '-i', str(input_path),
            '-c', 'copy',
            '-map_metadata', '0'
        ]
        
        metadata = {
            'title': title,
            'artist': artist,
            'album': album,
            'comment': description,
            'genre': genre,
            'date': date
        }
        
        for key, value in metadata.items():
            if value:
                cmd.extend(['-metadata', f'{key}={value}'])
        
        cmd.append(str(temp_output))
        
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            
            if not output_path:
                shutil.move(str(temp_output), str(input_path))
                return str(input_path)
            
            return str(temp_output)
            
        except subprocess.CalledProcessError as e:
            if temp_output.exists():
                temp_output.unlink()
            raise RuntimeError(f"FFmpeg metadata error: {e.stderr}")

    def SetThumbnail(self, video_path: str, thumbnail_path: str, output_path: Optional[str] = None) -> str:
        input_path = Path(video_path)
        thumb_path = Path(thumbnail_path)
        
        if not input_path.exists():
            raise FileNotFoundError(f"Video not found: {video_path}")
        if not thumb_path.exists():
            raise FileNotFoundError(f"Thumbnail not found: {thumbnail_path}")
            
        if not output_path:
            temp_output = input_path.with_suffix(f".thumb{input_path.suffix}")
        else:
            temp_output = Path(output_path)
            
        cmd = [
            'ffmpeg', '-y', '-hide_banner', '-loglevel', 'error',
            '-i', str(input_path),
            '-i', str(thumb_path),
            '-map', '0', '-map', '1',
            '-c', 'copy',
            '-disposition:v:1', 'attached_pic',
            str(temp_output)
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)
            
            if not output_path:
                shutil.move(str(temp_output), str(input_path))
                return str(input_path)
                
            return str(temp_output)
            
        except subprocess.CalledProcessError as e:
            if temp_output.exists():
                temp_output.unlink()
            raise RuntimeError(f"FFmpeg thumbnail error: {e.stderr}")
