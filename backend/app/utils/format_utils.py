from datetime import datetime
from typing import Any


# 格式化日期时间
def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    if not dt:
        return ""
    return dt.strftime(format_str)


# 格式化文件大小
def format_file_size(size_bytes: int) -> str:
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.2f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"


# 分页响应格式化
def format_pagination_response(
        items: list,
        total: int,
        page: int,
        page_size: int
) -> dict:
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size
    }


# 模型转字典
def model_to_dict(model: Any, exclude: list = None) -> dict:
    if exclude is None:
        exclude = []

    result = {}
    for column in model.__table__.columns:
        if column.name not in exclude:
            value = getattr(model, column.name)

            # 处理日期时间
            if isinstance(value, datetime):
                result[column.name] = format_datetime(value)
            else:
                result[column.name] = value

    return result