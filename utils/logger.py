"""
日志工具类
"""
import os
import logging
import logging.handlers
from typing import Optional
from pathlib import Path


def setup_logger(
    name: str,
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    max_size_mb: int = 10,
    backup_count: int = 5,
    log_format: Optional[str] = None,
    date_format: Optional[str] = None
) -> logging.Logger:
    """
    设置日志记录器

    Args:
        name: 日志记录器名称
        level: 日志级别
        log_file: 日志文件路径
        max_size_mb: 日志文件最大大小（MB）
        backup_count: 备份文件数量
        log_format: 日志格式
        date_format: 日期格式

    Returns:
        日志记录器
    """
    # 创建日志记录器
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # 如果已经有处理器，不重复添加
    if logger.handlers:
        return logger

    # 设置默认格式
    if log_format is None:
        log_format = "%(asctime)s [%(levelname)8s] %(message)s (%(filename)s:%(lineno)s)"
    if date_format is None:
        date_format = "%Y-%m-%d %H:%M:%S"

    formatter = logging.Formatter(log_format, datefmt=date_format)

    # 添加控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 添加文件处理器（如果指定了日志文件）
    if log_file:
        # 确保日志目录存在
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        # 创建轮转文件处理器
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_size_mb * 1024 * 1024,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    获取日志记录器

    Args:
        name: 日志记录器名称

    Returns:
        日志记录器
    """
    return logging.getLogger(name)


class RequestLogger:
    """请求日志记录器"""

    def __init__(self, logger: logging.Logger):
        """
        初始化请求日志记录器

        Args:
            logger: 日志记录器
        """
        self.logger = logger

    def log_request(
        self,
        method: str,
        url: str,
        headers: Optional[dict] = None,
        body: Optional[str] = None,
        status_code: Optional[int] = None,
        response_time: Optional[float] = None,
        error: Optional[str] = None
    ):
        """
        记录请求日志

        Args:
            method: 请求方法
            url: 请求URL
            headers: 请求头
            body: 请求体
            status_code: 响应状态码
            response_time: 响应时间（毫秒）
            error: 错误信息
        """
        log_data = {
            "method": method,
            "url": url,
        }

        if headers:
            # 过滤敏感信息
            filtered_headers = {k: v for k, v in headers.items()
                               if k.lower() not in ['authorization', 'cookie']}
            log_data["headers"] = filtered_headers

        if body:
            # 截断过长的请求体
            if len(body) > 1000:
                log_data["body"] = body[:1000] + "..."
            else:
                log_data["body"] = body

        if status_code is not None:
            log_data["status_code"] = status_code

        if response_time is not None:
            log_data["response_time_ms"] = round(response_time, 2)

        if error:
            log_data["error"] = error

        # 根据状态码选择日志级别
        if error:
            self.logger.error(f"请求失败: {log_data}")
        elif status_code and status_code >= 400:
            self.logger.warning(f"请求异常: {log_data}")
        else:
            self.logger.info(f"请求成功: {log_data}")

    def log_response(
        self,
        method: str,
        url: str,
        status_code: int,
        response_time: float,
        response_size: Optional[int] = None,
        response_body: Optional[str] = None
    ):
        """
        记录响应日志

        Args:
            method: 请求方法
            url: 请求URL
            status_code: 响应状态码
            response_time: 响应时间（毫秒）
            response_size: 响应大小（字节）
            response_body: 响应体
        """
        log_data = {
            "method": method,
            "url": url,
            "status_code": status_code,
            "response_time_ms": round(response_time, 2),
        }

        if response_size is not None:
            log_data["response_size_bytes"] = response_size

        if response_body:
            # 截断过长的响应体
            if len(response_body) > 1000:
                log_data["response_body"] = response_body[:1000] + "..."
            else:
                log_data["response_body"] = response_body

        # 根据状态码选择日志级别
        if status_code >= 500:
            self.logger.error(f"服务器错误: {log_data}")
        elif status_code >= 400:
            self.logger.warning(f"客户端错误: {log_data}")
        else:
            self.logger.info(f"响应成功: {log_data}")