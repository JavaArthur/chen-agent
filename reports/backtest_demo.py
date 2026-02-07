#!/usr/bin/env python3
"""
回测框架演示脚本
展示如何使用 backtest.py 进行股票回测
"""

import sys
sys.path.insert(0, '.')

from backtest import (
    Backtester,
    MovingAverageCrossStrategy,
    RSIStrategy,
    MACDStrategy,
    BollingerBandsStrategy,
    compare_strategies
)
import pandas as pd
import numpy as np


def demo_mock_data():
    """演示1: 使用模拟数据进行回测"""
    print("\n" + "="*70)
    print("📊 演示1: 模拟数据回测")
    print("="*70)
    
    # 生成模拟股价数据
    np.random.seed(42)
    dates = pd.date_range('2023-01-01', '2024-01-01', freq='D')
    returns = np.random.normal(0.0005, 0.02, len(dates))
    prices = 100 * np.exp(np.cumsum(returns))
    
    mock_data = pd.DataFrame({
        'Open': prices * 0.99,
        'High': prices * 1.02,
        'Low': prices * 0.98,
        'Close': prices,
        'Volume': np.random.randint(1000000, 10000000, len(dates))
    }, index=dates)
    
    print(f"✅ 生成模拟数据: {len(mock_data)} 条")
    print(f"   日期: {mock_data.index[0].date()} ~ {mock_data.index[-1].date()}")
    
    # 运行回测
    strategy = MovingAverageCrossStrategy(20, 50)
    backtester = Backtester(
        symbol='MOCK',
        strategy=strategy,
        start_date='2023-02-01',
        end_date='2023-12-01',
        initial_capital=100000
    )
    backtester.load_mock_data(mock_data)
    result = backtester.run()
    
    print(result)
    
    # 尝试保存图表（如果有matplotlib）
    try:
        backtester.plot_results(result, save_path='demo_result.png')
    except Exception as e:
        print(f"⚠️  无法生成图表: {e}")
    
    return result


def demo_real_data():
    """演示2: 使用真实数据（需要yfinance）"""
    print("\n" + "="*70)
    print("📊 演示2: 真实数据回测 (AAPL)")
    print("="*70)
    
    try:
        strategy = MovingAverageCrossStrategy(20, 50)
        backtester = Backtester(
            symbol='AAPL',
            strategy=strategy,
            start_date='2023-01-01',
            end_date='2024-01-01',
            initial_capital=100000
        )
        result = backtester.run()
        print(result)
        
        # 保存结果
        backtester.save_report(result, 'aapl_backtest.json')
        
        return result
        
    except ImportError as e:
        print(f"❌ {e}")
        print("   跳过真实数据回测，使用模拟数据演示")
        return None


def demo_strategy_comparison():
    """演示3: 多策略对比"""
    print("\n" + "="*70)
    print("📊 演示3: 多策略对比")
    print("="*70)
    
    # 使用模拟数据进行对比
    np.random.seed(42)
    dates = pd.date_range('2023-01-01', '2024-01-01', freq='D')
    returns = np.random.normal(0.0005, 0.02, len(dates))
    prices = 100 * np.exp(np.cumsum(returns))
    
    mock_data = pd.DataFrame({
        'Open': prices * 0.99,
        'High': prices * 1.02,
        'Low': prices * 0.98,
        'Close': prices,
        'Volume': np.random.randint(1000000, 10000000, len(dates))
    }, index=dates)
    
    strategies = [
        MovingAverageCrossStrategy(10, 30),
        MovingAverageCrossStrategy(20, 50),
        RSIStrategy(14, 30, 70),
        MACDStrategy(12, 26, 9),
        BollingerBandsStrategy(20, 2),
    ]
    
    print(f"\n对比 {len(strategies)} 个策略:\n")
    
    results = []
    for strategy in strategies:
        bt = Backtester(
            symbol='MOCK',
            strategy=strategy,
            start_date='2023-02-01',
            end_date='2023-12-01',
            initial_capital=100000
        )
        bt.load_mock_data(mock_data)
        result = bt.run()
        results.append(result.to_dict())
        print(f"✅ {result.strategy_name:25} | 收益: {result.total_return:>8.2%} | 交易: {result.trade_count:>2}次")
    
    # 创建对比表
    df = pd.DataFrame(results)
    print("\n" + "="*70)
    print("📈 策略对比汇总")
    print("="*70)
    print(df.to_string(index=False))
    
    # 找出最佳策略
    best_idx = df['total_return'].str.rstrip('%').astype(float).idxmax()
    best = df.iloc[best_idx]
    print(f"\n🏆 最佳策略: {best['strategy_name']}")
    print(f"   总收益率: {best['total_return']}")
    print(f"   夏普比率: {best['sharpe_ratio']}")


def demo_custom_strategy():
    """演示4: 自定义策略"""
    print("\n" + "="*70)
    print("📊 演示4: 自定义策略")
    print("="*70)
    
    from backtest import Strategy
    
    class DualMAVolumeStrategy(Strategy):
        """双均线+成交量策略示例"""
        def __init__(self, ma_fast=10, ma_slow=30, vol_period=20):
            super().__init__(f"DualMA_Vol_{ma_fast}_{ma_slow}")
            self.ma_fast = ma_fast
            self.ma_slow = ma_slow
            self.vol_period = vol_period
        
        def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
            df = data.copy()
            
            # 计算均线
            df['MA_fast'] = df['Close'].rolling(self.ma_fast).mean()
            df['MA_slow'] = df['Close'].rolling(self.ma_slow).mean()
            
            # 计算成交量均线
            df['Vol_MA'] = df['Volume'].rolling(self.vol_period).mean()
            
            # 生成信号：金叉+放量买入，死叉卖出
            df['signal'] = 0
            golden_cross = (df['MA_fast'] > df['MA_slow']) & (df['Volume'] > df['Vol_MA'])
            dead_cross = df['MA_fast'] < df['MA_slow']
            
            df.loc[golden_cross, 'signal'] = 1
            df.loc[dead_cross, 'signal'] = -1
            
            return df
    
    # 生成模拟数据
    np.random.seed(42)
    dates = pd.date_range('2023-01-01', '2024-01-01', freq='D')
    returns = np.random.normal(0.0005, 0.02, len(dates))
    prices = 100 * np.exp(np.cumsum(returns))
    
    mock_data = pd.DataFrame({
        'Open': prices * 0.99,
        'High': prices * 1.02,
        'Low': prices * 0.98,
        'Close': prices,
        'Volume': np.random.randint(1000000, 10000000, len(dates))
    }, index=dates)
    
    # 运行自定义策略
    strategy = DualMAVolumeStrategy(10, 30, 20)
    bt = Backtester(
        symbol='MOCK',
        strategy=strategy,
        start_date='2023-02-01',
        end_date='2023-12-01',
        initial_capital=100000
    )
    bt.load_mock_data(mock_data)
    result = bt.run()
    
    print(f"✅ 自定义策略: {result.strategy_name}")
    print(result)
    
    print("\n💡 自定义策略模板:\n")
    print("""
class MyStrategy(Strategy):
    def __init__(self, param1=10):
        super().__init__("MyStrategy")
        self.param1 = param1
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        df = data.copy()
        # 计算指标
        df['indicator'] = ...
        # 生成信号
        df['signal'] = 0
        df.loc[买入条件, 'signal'] = 1
        df.loc[卖出条件, 'signal'] = -1
        return df
""")


def main():
    """主函数"""
    print("\n" + "="*70)
    print("🚀 股票回测框架演示")
    print("="*70)
    print("\n这个脚本展示了 backtest.py 的主要功能:")
    print("  1. 使用模拟数据进行回测")
    print("  2. 使用真实股票数据回测")
    print("  3. 多策略对比")
    print("  4. 自定义策略")
    
    # 运行演示
    demo_mock_data()
    demo_real_data()
    demo_strategy_comparison()
    demo_custom_strategy()
    
    print("\n" + "="*70)
    print("✅ 演示完成!")
    print("="*70)
    print("\n📖 详细文档请查看: backtest_usage.md")
    print("   源代码: backtest.py")
    print("\n💡 安装依赖后可以使用真实数据:")
    print("   pip install yfinance pandas numpy matplotlib")


if __name__ == "__main__":
    main()
