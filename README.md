# CSGO-Scraper
爬取饰品市场数据，辅助建立投资策略（更新中）

---
## 📂 项目结构

```
CSGO-Scraper/
├── cscraper/
│   ├── database/              # 基础数据库
│   ├── __init__.py            # 初始化文件
│   ├── csplot.py              # 指标绘图
│   ├── fetch_steam.py         # 获取Steam市场数据
│   ├── fetch_uusm.py          # 获取uusm市场数据
│   ├── indicators.py          # 计算相关指标
│   └── utils.py               # 工具函数
└── .gitignore                  
```

---

## 💡 使用指南

### 1.快速上手
```
brainstorm_steam(item_name)            # 生成Steam市场报告
```
说明：输入想要查询的饰品名称(`str`)，一键生成商品报告(Markdown文件)

### 2.Steam市场行情获取
```
get_realtime_steam(item_name)          # 获取实时行情
get_history_steam(item_name)           # 获取历史行情
```
说明：输入想要查询的饰品名称(`str`)，返回一个`pd.DataFrame`包含Steam市场的实时行情(最低价、在售数量、成交量、平均价)或历史行情(历史每日成交量、平均成交价)
### 3.指标计算函数
```
get_ma_n(df_history, n)                # 计算n日移动平均线(MAn)
get_rsi_n(df_history, n)               # 计算n日相对强弱指数(RSIn)
get_vol_ratio_n(df_history, n)         # 计算n日量比(VRn)
get_rv_n(df_history, n)                # 计算n日滚动波动率(RVn)
get_boll_n(df_history, n)              # 计算n日布林带(Bolln)
get_max_drawdown_n(df_history, n)      # 计算回撤情况及修复情况
```
说明：输入历史行情的数据帧和窗口天数，返回一个`pd.DataFrame`包含MAn等指标

注：`get_max_drawdown_n`返回的是一个包含回撤和修复情况的`Dict`

### 4.绘图函数
```
plot_ma(df_ma, chart_path)             # 绘制MAn图像
plot_rv(df_rv, chart_path)             # 绘制RVn图像
plot_vr(df_vr, chart_path)             # 绘制VRn图像
plot_boll(df_boll, chart_path)         # 绘制Bolln图像
plot_rsi(df_rsi, chart_path)           # 绘制RSIn图像
```
说明：输入由对应指标函数计算结果的数据帧和想要保存图像的位置，在对应路径得到对应图像
