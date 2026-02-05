import os
import uuid
import mimetypes
import zipfile
from pathlib import Path
from PIL import Image
import exifread

# 支持的文件类型
SUPPORTED_IMAGE_TYPES = {
    'image/jpeg': ['jpg', 'jpeg'],
    'image/png': ['png'],
    'image/raw': ['raw', 'cr2', 'nef', 'arw']
}

# 文件大小限制（字节）
FILE_SIZE_LIMITS = {
    'jpg': 50 * 1024 * 1024,  # 50MB
    'raw': 200 * 1024 * 1024  # 200MB
}


# 确保目录存在
def ensure_dir(dir_path: str):
    Path(dir_path).mkdir(parents=True, exist_ok=True)


# 生成唯一文件名
def generate_unique_filename(original_filename: str) -> str:
    ext = os.path.splitext(original_filename)[1].lower()
    return f"{uuid.uuid4()}{ext}"


# 获取文件MIME类型
def get_file_mime_type(file_path: str) -> str:
    mime_type, _ = mimetypes.guess_type(file_path)
    return mime_type or 'application/octet-stream'


# 验证文件类型
def validate_file_type(filename: str, file_type: str = None) -> bool:
    ext = os.path.splitext(filename)[1].lower().lstrip('.')

    for mime, extensions in SUPPORTED_IMAGE_TYPES.items():
        if ext in extensions:
            return True

    return False


# 验证文件大小
def validate_file_size(filename: str, file_size: int) -> bool:
    ext = os.path.splitext(filename)[1].lower().lstrip('.')

    if ext in ['jpg', 'jpeg']:
        return file_size <= FILE_SIZE_LIMITS['jpg']
    elif ext in ['raw', 'cr2', 'nef', 'arw']:
        return file_size <= FILE_SIZE_LIMITS['raw']

    return False


# 生成缩略图
def generate_thumbnail(image_path: str, output_path: str, size: tuple = (200, 200)) -> str:
    try:
        with Image.open(image_path) as img:
            img.thumbnail(size)
            img.save(output_path, 'JPEG', quality=85)
        return output_path
    except Exception as e:
        print(f"生成缩略图失败: {e}")
        return ""


# 提取EXIF信息
def extract_exif_data(image_path: str) -> dict:
    exif_data = {}
    try:
        with open(image_path, 'rb') as f:
            tags = exifread.process_file(f)

            # 提取关键EXIF信息
            exif_mapping = {
                'Image Make': 'camera_make',
                'Image Model': 'camera_model',
                'EXIF DateTimeOriginal': 'capture_time',
                'EXIF ExifImageWidth': 'width',
                'EXIF ExifImageLength': 'height',
                'EXIF ISOSpeedRatings': 'iso',
                'EXIF FNumber': 'aperture',
                'EXIF ExposureTime': 'exposure_time',
                'EXIF FocalLength': 'focal_length'
            }

            for tag, key in exif_mapping.items():
                if tag in tags:
                    exif_data[key] = str(tags[tag])

    except Exception as e:
        print(f"提取EXIF信息失败: {e}")

    return exif_data


# 解压ZIP文件
def extract_zip_file(zip_path: str, extract_dir: str) -> list:
    extracted_files = []

    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            for file_info in zip_ref.infolist():
                # 跳过目录和恶意路径
                if file_info.is_dir() or '..' in file_info.filename:
                    continue

                # 验证文件类型
                if validate_file_type(file_info.filename):
                    zip_ref.extract(file_info, extract_dir)
                    extracted_files.append(os.path.join(extract_dir, file_info.filename))

    except Exception as e:
        print(f"解压ZIP文件失败: {e}")

    return extracted_files