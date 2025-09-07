def calculate_correlation(x, y):
    """
    计算皮尔逊相关系数
    
    Args:
        x: 第一个变量的数值列表
        y: 第二个变量的数值列表
    
    Returns:
        相关系数值 (float)
    """
    if len(x) != len(y):
        raise ValueError("x and y must have the same length")
    
    if len(x) == 0:
        raise ValueError("Input arrays cannot be empty")
    
    n = len(x)
    
    # 计算均值
    x_mean = sum(x) / n
    y_mean = sum(y) / n
    
    # 计算分子: Σ[(xi - x̄)(yi - ȳ)]
    numerator = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
    
    # 计算分母: √[Σ(xi - x̄)² × Σ(yi - ȳ)²]
    sum_x_squared = sum((x[i] - x_mean) ** 2 for i in range(n))
    sum_y_squared = sum((y[i] - y_mean) ** 2 for i in range(n))
    
    denominator = (sum_x_squared * sum_y_squared) ** 0.5
    
    if denominator == 0:
        return 0  # 避免除零错误
    
    return numerator / denominator