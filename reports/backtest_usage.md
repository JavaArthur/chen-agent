# 股票回测框架使用指南

## 快速开始

### 1. 基础回测（单一策略）

```python
from backtest import (
    Backtester, 
    MovingAverageCrossStrategy,
    RSIStrategy,
    MACDStrategy,
    BollingerBandsStrategy
)

# 创建策略
strategy = MovingAverageCrossStrategy(short_window=20, long_window=50)

# 创建回测引擎
backtester = Backtester(
    symbol='AAPL',           # 股票代码
    strategy=strategy,       # 策略对象
    start_date='2023-01-01', # 开始日期
    end_date='2024-01-01',   # 结束日期
    initial_capital=100000,  # 初始资金
    commission=0.001,        # 手续费率 (0.1%)
    slippage=0.001           # 滑点 (0.1%)
)

# 运行回测
result = backtester.run()

# 打印结果
print(result)

# 可视化
backtester.plot_results(result, save_path='result.png')

# 保存报告
backtester.save_report(result, 'report.json')
```

### 2. 多策略对比

```python
from backtest import compare_strategies

# 定义多个策略
strategies = [
    MovingAverageCrossStrategy(10, 30),
    MovingAverageCrossStrategy(20, 50),
    RSIStrategy(14, 30, 70),
    MACDStrategy(12, 26, 9),
    BollingerBandsStrategy(20, 2),
]

# 对比回测
comparison = compare_strategies(
    symbol='AAPL',
    strategies=strategies,
    start_date='2023-01-01',
    end_date='2024-01-01',
    initial_capital=100000
)

# 查看对比结果
print(comparison)
```

## 内置策略

### 1. 移动平均线交叉策略 (MovingAverageCrossStrategy)

```python
strategy = MovingAverageCrossStrategy(
    short_window=20,  # 短期均线周期
    long_window=50    # 长期均线周期
)
# 金叉买入，死叉卖出
```

### 2. RSI策略 (RSIStrategy)

```python
strategy = RSIStrategy(
    period=14,        # RSI计算周期
    oversold=30,      # 超卖阈值 (低于此值买入)
    overbought=70     # 超买阈值 (高于此值卖出)
)
```

### 3. MACD策略 (MACDStrategy)

```python
strategy = MACDStrategy(
    fast=12,     # 快线周期
    slow=26,     # 慢线周期
    signal=9     # 信号线周期
)
# MACD上穿信号线买入，下穿卖出
```

### 4. 布林带策略 (BollingerBandsStrategy)

```python
strategy = BollingerBandsStrategy(
    window=20,    # 均线周期
    num_std=2     # 标准差倍数
)
# 触及下轨买入，触及上轨卖出
```

## 自定义策略

```python
from backtest import Strategy
import pandas as pd

class MyStrategy(Strategy):
    def __init__(self, param1=10, param2=20):
        super().__init__(f"MyStrategy_{param1}_{param2}")
        self.param1 = param1
        self.param2 = param2
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        df = data.copy()
        
        # 计算你的指标
        df['indicator'] = ...
        
        # 生成信号
        df['signal'] = 0
        df.loc[...买入条件..., 'signal'] = 1
        df.loc[...卖出条件..., 'signal'] = -1
        
        return df

# 使用自定义策略
strategy = MyStrategy(param1=10, param2=20)
backtester = Backtester('AAPL', strategy, '2023-01-01', '2024-01-01')
result = backtester.run()
```

## 输出指标说明

| 指标 | 说明 |
|------|------|
| **Total Return** | 总收益率 |
| **Annualized Return** | 年化收益率 |
| **Max Drawdown** | 最大回撤（最大亏损比例）|
| **Sharpe Ratio** | 夏普比率（风险调整后收益）|
| **Trade Count** | 交易次数 |
| **Win Rate** | 胜率 |

## 支持的股票代码

使用 Yahoo Finance 格式：

- 美股: `AAPL`, `MSFT`, `GOOGL`, `TSLA`
- A股: `000001.SS` (上证指数), `000001.SZ` (平安银行)
- 港股: `0700.HK` (腾讯), `9988.HK` (阿里巴巴)
- ETF: `SPY`, `QQQ`, `SH`

## 完整示例

```python
#!/usr/bin/env python3
from backtest import *

# 定义要测试的策略
strategies = [
    MovingAverageCrossStrategy(5, 20),    # 短线均线
    MovingAverageCrossStrategy(20, 60),   # 中线均线
    RSIStrategy(14, 30, 70),              # 标准RSI
    RSIStrategy(7, 20, 80),               # 敏感RSI
    MACDStrategy(),                        # 标准MACD
]

# 运行对比
results = compare_strategies(
    symbol='000001.SS',        # 上证指数
    strategies=strategies,
    start_date='2022-01-01',   # 回测2年
    end_date='2024-01-01',
    initial_capital=100000
)

# 找出最佳策略
best = results.loc[results['total_return'].idxmax()]
print(f"\n🏆 最佳策略: {best['strategy_name']}")
print(f"   收益率: {best['total_return']}")
```

## 依赖安装

```bash
pip install yfinance pandas numpy matplotlib
```

## 注意事项

1. **数据获取**: 需要网络连接获取 Yahoo Finance 数据
2. **A股数据**: A股代码后缀 `.SS` (上海) 或 `.SZ` (深圳)
3. **回测偏差**: 历史表现不代表未来收益
4. **滑点和手续费**: 默认设置可能不符合实际，请根据实际情况调整
