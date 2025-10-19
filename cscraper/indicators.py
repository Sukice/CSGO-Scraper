from datetime import datetime, timedelta
import numpy as np

from cscraper.fetch_steam import get_history_data_steam


def get_ma_n(df, n=20):
    ma_col = f"MA{n}"
    df[ma_col] = df['price'].rolling(window=n, min_periods=1).mean().round(2)
    result = df[['date','name', ma_col]].reset_index(drop=True)
    return result

def get_rsi_n(df, n=20):
    df['change'] = df['price'].diff()  # Current close - previous close
    df['gain'] = df['change'].where(df['change'] > 0, 0)
    df['loss'] = -df['change'].where(df['change'] < 0, 0)
    df['avg_gain'] = df['gain'].rolling(window=n, min_periods=1).mean()
    df['avg_loss'] = df['loss'].rolling(window=n, min_periods=1).mean()
    df['rs'] = df['avg_gain'] / df['avg_loss'].replace(0, 0.0001)
    rsi_col = f"RSI{n}"
    df[rsi_col] = 100 - (100 / (1 + df['rs']))
    df[rsi_col] = df[rsi_col].round(2)
    result = df[['date','name', rsi_col]].copy()
    return result

def get_vol_ratio_n(df, n=20):
    vol_col = f"vol{n}"
    result_col = f"VR{n}"
    df[vol_col] = df['volume'].rolling(window=n, min_periods=1).mean().round(2)
    df[result_col] = (df['volume'] / df[vol_col]).round(2)
    result = df[['date', 'name', result_col]].copy()
    return result

def get_boll_n(df, n=20):
    ma_values = df['price'].rolling(window=n, min_periods=1).mean().round(2)
    std_values = df['price'].rolling(window=n, min_periods=1).std().round(2)
    df['upper'] = (ma_values + 2 * std_values).round(2)
    df['lower'] = (ma_values - 2 * std_values).round(2)
    df['mid'] = ma_values
    result = df[['date','name', 'upper', 'mid', 'lower']].copy().reset_index(drop=True)
    return result

def get_rv_n(df, n=20):
    df["log_change"] = np.log(df['price'] / df['price'].shift(1))
    rv_col = f"RV{n}"
    df[rv_col] = df['log_change'].rolling(window=n, min_periods=1).std() * np.sqrt(n)
    result = df[['date','name', rv_col]].copy()
    return result

def get_max_drawdown_n(df, n=90):
    target_date = datetime.now() - timedelta(days=n)
    df['date'] = df['date'].astype(str)
    df = df[df['date'] >= target_date.strftime("%Y%m%d")].copy()
    df['cum_max'] = df['price'].cummax()
    df['drawdown'] = df['price'] - df['cum_max']
    max_drawdown = df['drawdown'].min()
    trough_idx = df['drawdown'].idxmin()
    peak_idx = df.loc[:trough_idx, 'cum_max'].idxmax()
    post_trough_df = df[trough_idx:].copy()
    recovery_candidates = post_trough_df[post_trough_df['price'] >= df['price'][peak_idx]]
    recovery_success = False
    recovery_days = None
    recovery_date = None
    if not recovery_candidates.empty:
        recovery_success = True
        recovery_date_data = recovery_candidates.loc[recovery_candidates['date'].idxmin()]
        recovery_days = (recovery_date_data['date'] - df['date'][trough_idx]).days
        recovery_date = recovery_date_data['date']
    result = {
        'max_drawdown': float(max_drawdown),
        'max_drawdown_peak_date': str(df['date'][peak_idx]),
        'max_drawdown_peak_price': float(df['price'][peak_idx]),
        'max_drawdown_trough_date': str(df['date'][trough_idx]),
        'max_drawdown_trough_price': float(df['price'][trough_idx]),
        'recovery_success': bool(recovery_success),
        'recovery_days': int(recovery_days) if recovery_days is not None else None,
        'recovery_date': str(recovery_date.date()) if recovery_date is not None else None,
    }
    return result

if __name__ == '__main__':
    df = get_history_data_steam("梦魇武器箱")
    print(get_max_drawdown_n(df),'\n')
    print(get_vol_ratio_n(df),'\n')
    print(get_boll_n(df),'\n')
    print(get_rv_n(df),'\n')
    print(get_ma_n(df),'\n')
    print(get_rsi_n(df),'\n')

