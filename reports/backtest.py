#!/usr/bin/env python3
"""
股票回测框架
支持：指定日期范围、多策略、可视化、收益率计算
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Callable, Optional, Tuple
from dataclasses import dataclass
from abc import ABC, abstractmethod
import json

# 可选依赖
try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
    # 设置中文显示
    plt.rcParams['font.sans-serif'] = ['DejaVu Sans']
    plt.rcParams['axes.unicode_minus'] = False
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("⚠️  matplotlib 未安装，可视化功能不可用。运行: pip install matplotlib")

try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False
    print("⚠️  yfinance 未安装，数据获取功能不可用。运行: pip install yfinance")


@dataclass
class BacktestResult:
    """回测结果数据结构"""
    strategy_name: str
    symbol: str
    start_date: str
    end_date: str
    initial_capital: float
    final_capital: float
    total_return: float  # 总收益率
    annualized_return: float  # 年化收益率
    max_drawdown: float  # 最大回撤
    sharpe_ratio: float  # 夏普比率
    trade_count: int  # 交易次数
    win_rate: float  # 胜率
    equity_curve: pd.Series  # 权益曲线
    trades: List[Dict]  # 交易记录
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            'strategy_name': self.strategy_name,
            'symbol': self.symbol,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'initial_capital': self.initial_capital,
            'final_capital': self.final_capital,
            'total_return': f"{self.total_return:.2%}",
            'annualized_return': f"{self.annualized_return:.2%}",
            'max_drawdown': f"{self.max_drawdown:.2%}",
            'sharpe_ratio': f"{self.sharpe_ratio:.2f}",
            'trade_count': self.trade_count,
            'win_rate': f"{self.win_rate:.2%}",
        }
    
    def __str__(self) -> str:
        """字符串表示"""
        return f"""
╔══════════════════════════════════════════════════════════╗
║                   回测结果报告                            ║
╠══════════════════════════════════════════════════════════╣
║ 策略: {self.strategy_name:<20} 标的: {self.symbol:<10}       ║
║ 回测区间: {self.start_date} ~ {self.end_date}               ║
╠══════════════════════════════════════════════════════════╣
║ 初始资金: {self.initial_capital:>12,.2f}                              ║
║ 最终资金: {self.final_capital:>12,.2f}                              ║
║ 总收益率: {self.total_return:>11.2%}                               ║
║ 年化收益: {self.annualized_return:>11.2%}                               ║
║ 最大回撤: {self.max_drawdown:>11.2%}                               ║
║ 夏普比率: {self.sharpe_ratio:>11.2f}                               ║
║ 交易次数: {self.trade_count:>12}                               ║
║ 胜率:     {self.win_rate:>11.2%}                               ║
╚══════════════════════════════════════════════════════════╝
"""


class Strategy(ABC):
    """策略基类"""
    
    def __init__(self, name: str):
        self.name = name
    
    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        生成交易信号
        返回DataFrame，包含'signal'列：1(买入), -1(卖出), 0(持有)
        """
        pass
    
    def __str__(self):
        return f"Strategy({self.name})"


class MovingAverageCrossStrategy(Strategy):
    """移动平均线交叉策略"""
    
    def __init__(self, short_window: int = 20, long_window: int = 50):
        super().__init__(f"MA_Cross_{short_window}_{long_window}")
        self.short_window = short_window
        self.long_window = long_window
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        df = data.copy()
        df['MA_short'] = df['Close'].rolling(window=self.short_window).mean()
        df['MA_long'] = df['Close'].rolling(window=self.long_window).mean()
        
        # 生成信号
        df['signal'] = 0
        df.loc[df['MA_short'] > df['MA_long'], 'signal'] = 1  # 金叉买入
        df.loc[df['MA_short'] < df['MA_long'], 'signal'] = -1  # 死叉卖出
        
        # 只保留信号变化点
        df['position'] = df['signal'].diff().fillna(0)
        
        return df


class RSIStrategy(Strategy):
    """RSI相对强弱指数策略"""
    
    def __init__(self, period: int = 14, oversold: int = 30, overbought: int = 70):
        super().__init__(f"RSI_{period}_{oversold}_{overbought}")
        self.period = period
        self.oversold = oversold
        self.overbought = overbought
    
    def calculate_rsi(self, prices: pd.Series) -> pd.Series:
        """计算RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.period).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        df = data.copy()
        df['RSI'] = self.calculate_rsi(df['Close'])
        
        df['signal'] = 0
        df.loc[df['RSI'] < self.oversold, 'signal'] = 1  # 超卖买入
        df.loc[df['RSI'] > self.overbought, 'signal'] = -1  # 超买卖出
        
        return df


class MACDStrategy(Strategy):
    """MACD策略"""
    
    def __init__(self, fast: int = 12, slow: int = 26, signal: int = 9):
        super().__init__(f"MACD_{fast}_{slow}_{signal}")
        self.fast = fast
        self.slow = slow
        self.signal = signal
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        df = data.copy()
        
        # 计算MACD
        ema_fast = df['Close'].ewm(span=self.fast).mean()
        ema_slow = df['Close'].ewm(span=self.slow).mean()
        df['MACD'] = ema_fast - ema_slow
        df['Signal_Line'] = df['MACD'].ewm(span=self.signal).mean()
        df['Histogram'] = df['MACD'] - df['Signal_Line']
        
        # 生成信号
        df['signal'] = 0
        df.loc[df['MACD'] > df['Signal_Line'], 'signal'] = 1  # MACD上穿信号线买入
        df.loc[df['MACD'] < df['Signal_Line'], 'signal'] = -1  # MACD下穿信号线卖出
        
        return df


class BollingerBandsStrategy(Strategy):
    """布林带策略"""
    
    def __init__(self, window: int = 20, num_std: int = 2):
        super().__init__(f"BB_{window}_{num_std}")
        self.window = window
        self.num_std = num_std
    
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        df = data.copy()
        
        # 计算布林带
        df['MA'] = df['Close'].rolling(window=self.window).mean()
        df['STD'] = df['Close'].rolling(window=self.window).std()
        df['Upper'] = df['MA'] + (df['STD'] * self.num_std)
        df['Lower'] = df['MA'] - (df['STD'] * self.num_std)
        
        # 生成信号
        df['signal'] = 0
        df.loc[df['Close'] < df['Lower'], 'signal'] = 1  # 触及下轨买入
        df.loc[df['Close'] > df['Upper'], 'signal'] = -1  # 触及上轨卖出
        
        return df


class Backtester:
    """回测引擎"""
    
    def __init__(
        self,
        symbol: str,
        strategy: Strategy,
        start_date: str,
        end_date: str,
        initial_capital: float = 100000.0,
        commission: float = 0.001,  # 手续费率
        slippage: float = 0.001,  # 滑点
    ):
        """
        初始化回测引擎
        
        Args:
            symbol: 股票代码 (如 'AAPL', '000001.SS')
            strategy: 策略对象
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            initial_capital: 初始资金
            commission: 手续费率
            slippage: 滑点率
        """
        self.symbol = symbol
        self.strategy = strategy
        self.start_date = datetime.strptime(start_date, '%Y-%m-%d')
        self.end_date = datetime.strptime(end_date, '%Y-%m-%d')
        self.initial_capital = initial_capital
        self.commission = commission
        self.slippage = slippage
        self.data = None
        self.trades = []
        
    def fetch_data(self) -> pd.DataFrame:
        """获取历史数据"""
        if not YFINANCE_AVAILABLE:
            raise ImportError("yfinance 未安装，无法获取数据。运行: pip install yfinance")
        
        print(f"📊 正在获取 {self.symbol} 数据 ({self.start_date.date()} ~ {self.end_date.date()})...")
        
        # 多获取一些数据用于计算指标
        extended_start = self.start_date - timedelta(days=100)
        
        ticker = yf.Ticker(self.symbol)
        data = ticker.history(start=extended_start, end=self.end_date)
        
        if data.empty:
            raise ValueError(f"无法获取 {self.symbol} 的数据")
        
        # 过滤到指定日期范围
        self.data = data[data.index >= self.start_date.strftime('%Y-%m-%d')].copy()
        
        print(f"✅ 获取到 {len(self.data)} 条数据")
        return self.data
    
    def load_mock_data(self, data: pd.DataFrame = None) -> pd.DataFrame:
        """
        加载模拟数据（用于测试或离线环境）
        
        Args:
            data: 自定义DataFrame，必须包含 'Close' 列
                 如果为None，则生成随机游走数据
        """
        if data is not None:
            self.data = data.copy()
            print(f"✅ 已加载自定义数据: {len(self.data)} 条")
            return self.data
        
        # 生成随机游走模拟数据
        print("📊 生成模拟数据...")
        dates = pd.date_range(start=self.start_date - timedelta(days=50), 
                             end=self.end_date, freq='D')
        
        np.random.seed(42)
        returns = np.random.normal(0.001, 0.02, len(dates))
        prices = 100 * np.exp(np.cumsum(returns))
        
        self.data = pd.DataFrame({
            'Open': prices * (1 + np.random.normal(0, 0.001, len(dates))),
            'High': prices * (1 + abs(np.random.normal(0, 0.01, len(dates)))),
            'Low': prices * (1 - abs(np.random.normal(0, 0.01, len(dates)))),
            'Close': prices,
            'Volume': np.random.randint(1000000, 10000000, len(dates))
        }, index=dates)
        
        # 过滤到指定日期范围
        self.data = self.data[self.data.index >= self.start_date.strftime('%Y-%m-%d')]
        
        print(f"✅ 已生成模拟数据: {len(self.data)} 条")
        return self.data
    
    def run(self) -> BacktestResult:
        """运行回测"""
        if self.data is None:
            self.fetch_data()
        
        # 生成信号
        df = self.strategy.generate_signals(self.data)
        
        # 初始化
        capital = self.initial_capital
        position = 0  # 持仓数量
        equity_curve = []
        self.trades = []
        
        for i, (date, row) in enumerate(df.iterrows()):
            price = row['Close']
            signal = row.get('signal', 0)
            
            # 买入信号
            if signal == 1 and position == 0:
                # 计算可买入数量（考虑手续费和滑点）
                cost_price = price * (1 + self.slippage)
                max_shares = int(capital * (1 - self.commission) / cost_price)
                
                if max_shares > 0:
                    cost = max_shares * cost_price
                    commission_fee = cost * self.commission
                    total_cost = cost + commission_fee
                    
                    if total_cost <= capital:
                        position = max_shares
                        capital -= total_cost
                        self.trades.append({
                            'date': date,
                            'type': 'BUY',
                            'price': cost_price,
                            'shares': max_shares,
                            'cost': total_cost,
                            'capital': capital
                        })
            
            # 卖出信号
            elif signal == -1 and position > 0:
                sell_price = price * (1 - self.slippage)
                revenue = position * sell_price
                commission_fee = revenue * self.commission
                net_revenue = revenue - commission_fee
                
                # 计算盈亏
                buy_trade = next((t for t in reversed(self.trades) if t['type'] == 'BUY'), None)
                if buy_trade:
                    pnl = net_revenue - buy_trade['cost']
                    pnl_pct = pnl / buy_trade['cost']
                else:
                    pnl = pnl_pct = 0
                
                capital += net_revenue
                self.trades.append({
                    'date': date,
                    'type': 'SELL',
                    'price': sell_price,
                    'shares': position,
                    'revenue': net_revenue,
                    'pnl': pnl,
                    'pnl_pct': pnl_pct,
                    'capital': capital
                })
                position = 0
            
            # 计算当前权益
            equity = capital + position * price
            equity_curve.append({'date': date, 'equity': equity})
        
        # 计算回测指标
        return self._calculate_metrics(equity_curve)
    
    def _calculate_metrics(self, equity_curve: List[Dict]) -> BacktestResult:
        """计算回测指标"""
        equity_df = pd.DataFrame(equity_curve).set_index('date')['equity']
        
        # 基本指标
        final_capital = equity_df.iloc[-1]
        total_return = (final_capital - self.initial_capital) / self.initial_capital
        
        # 年化收益率
        days = (equity_df.index[-1] - equity_df.index[0]).days
        years = days / 365.25
        annualized_return = (1 + total_return) ** (1 / years) - 1 if years > 0 else 0
        
        # 最大回撤
        cummax = equity_df.cummax()
        drawdown = (equity_df - cummax) / cummax
        max_drawdown = drawdown.min()
        
        # 夏普比率 (假设无风险利率为2%)
        daily_returns = equity_df.pct_change().dropna()
        risk_free_rate = 0.02 / 252  # 日无风险利率
        excess_returns = daily_returns - risk_free_rate
        sharpe_ratio = np.sqrt(252) * excess_returns.mean() / daily_returns.std() if daily_returns.std() != 0 else 0
        
        # 交易统计
        completed_trades = [t for t in self.trades if t['type'] == 'SELL']
        trade_count = len(completed_trades)
        win_count = sum(1 for t in completed_trades if t.get('pnl', 0) > 0)
        win_rate = win_count / trade_count if trade_count > 0 else 0
        
        return BacktestResult(
            strategy_name=self.strategy.name,
            symbol=self.symbol,
            start_date=self.start_date.strftime('%Y-%m-%d'),
            end_date=self.end_date.strftime('%Y-%m-%d'),
            initial_capital=self.initial_capital,
            final_capital=final_capital,
            total_return=total_return,
            annualized_return=annualized_return,
            max_drawdown=max_drawdown,
            sharpe_ratio=sharpe_ratio,
            trade_count=trade_count,
            win_rate=win_rate,
            equity_curve=equity_df,
            trades=self.trades
        )
    
    def plot_results(self, result: BacktestResult, save_path: Optional[str] = None):
        """可视化回测结果"""
        if not MATPLOTLIB_AVAILABLE:
            print("⚠️  matplotlib 未安装，无法生成图表")
            print("   运行: pip install matplotlib")
            return None
        
        fig, axes = plt.subplots(3, 1, figsize=(14, 12))
        
        # 1. 价格走势和交易点
        ax1 = axes[0]
        ax1.plot(self.data.index, self.data['Close'], label='Price', color='gray', alpha=0.7)
        
        # 标记买卖点
        for trade in result.trades:
            if trade['type'] == 'BUY':
                ax1.scatter(trade['date'], trade['price'], marker='^', color='red', s=100, zorder=5, label='Buy' if trade == result.trades[0] else '')
            else:
                color = 'green' if trade.get('pnl', 0) > 0 else 'orange'
                ax1.scatter(trade['date'], trade['price'], marker='v', color=color, s=100, zorder=5, label='Sell (Win)' if color == 'green' and trade == result.trades[1] else 'Sell (Loss)' if color == 'orange' and trade == result.trades[1] else '')
        
        ax1.set_title(f'{result.symbol} - {result.strategy_name}', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Price')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. 权益曲线
        ax2 = axes[1]
        ax2.plot(result.equity_curve.index, result.equity_curve, label='Strategy', color='blue', linewidth=2)
        ax2.axhline(y=result.initial_capital, color='gray', linestyle='--', alpha=0.5, label='Initial Capital')
        
        # 添加收益率标注
        ax2.text(0.02, 0.95, f'Total Return: {result.total_return:.2%}', 
                transform=ax2.transAxes, fontsize=11, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        ax2.set_title('Equity Curve', fontsize=12, fontweight='bold')
        ax2.set_ylabel('Capital')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 3. 回撤曲线
        ax3 = axes[2]
        cummax = result.equity_curve.cummax()
        drawdown = (result.equity_curve - cummax) / cummax
        ax3.fill_between(drawdown.index, drawdown, 0, color='red', alpha=0.3)
        ax3.plot(drawdown.index, drawdown, color='red', linewidth=1)
        ax3.set_title(f'Drawdown (Max: {result.max_drawdown:.2%})', fontsize=12, fontweight='bold')
        ax3.set_ylabel('Drawdown')
        ax3.set_xlabel('Date')
        ax3.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"📊 图表已保存至: {save_path}")
        else:
            plt.show()
        
        return fig
    
    def save_report(self, result: BacktestResult, filepath: str):
        """保存回测报告"""
        report = {
            'summary': result.to_dict(),
            'trades': result.trades,
            'equity_curve': result.equity_curve.to_dict()
        }
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"📄 报告已保存至: {filepath}")


def compare_strategies(
    symbol: str,
    strategies: List[Strategy],
    start_date: str,
    end_date: str,
    initial_capital: float = 100000.0
) -> pd.DataFrame:
    """
    对比多个策略
    
    Returns:
        DataFrame 包含各策略的回测指标
    """
    results = []
    
    for strategy in strategies:
        print(f"\n{'='*60}")
        print(f"正在回测: {strategy.name}")
        print('='*60)
        
        backtester = Backtester(
            symbol=symbol,
            strategy=strategy,
            start_date=start_date,
            end_date=end_date,
            initial_capital=initial_capital
        )
        
        try:
            result = backtester.run()
            results.append(result.to_dict())
            print(result)
        except Exception as e:
            print(f"❌ 回测失败: {e}")
    
    return pd.DataFrame(results)


# ==================== 使用示例 ====================

if __name__ == "__main__":
    # 示例1: 单一策略回测
    print("="*60)
    print("示例1: 单一策略回测 - AAPL移动平均线交叉")
    print("="*60)
    
    strategy = MovingAverageCrossStrategy(short_window=20, long_window=50)
    backtester = Backtester(
        symbol='AAPL',
        strategy=strategy,
        start_date='2023-01-01',
        end_date='2024-01-01',
        initial_capital=100000.0
    )
    
    result = backtester.run()
    print(result)
    
    # 可视化
    backtester.plot_results(result, save_path='backtest_result.png')
    
    # 保存报告
    backtester.save_report(result, 'backtest_report.json')
    
    # 示例2: 多策略对比
    print("\n" + "="*60)
    print("示例2: 多策略对比")
    print("="*60)
    
    strategies = [
        MovingAverageCrossStrategy(20, 50),
        RSIStrategy(14, 30, 70),
        MACDStrategy(12, 26, 9),
        BollingerBandsStrategy(20, 2),
    ]
    
    comparison = compare_strategies(
        symbol='AAPL',
        strategies=strategies,
        start_date='2023-01-01',
        end_date='2024-01-01'
    )
    
    print("\n📊 策略对比结果:")
    print(comparison.to_string())
