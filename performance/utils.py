"""
性能测试共享工具函数
"""
from typing import List


def percentile(data: List[float], percentile_rank: int) -> float:
    """计算百分位数"""
    if not data:
        return 0.0
    sorted_data = sorted(data)
    index = int(len(sorted_data) * percentile_rank / 100)
    return sorted_data[min(index, len(sorted_data) - 1)]
