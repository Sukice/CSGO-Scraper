from cscraper import *

if __name__ == "__main__":

    init_database_casecontent()
    init_database_namedata_case()

    df = get_realtime_data_steam("AK-47血腥运动（崭新出厂）")
    print(df,'\n')
    df = get_history_data_steam("梦魇武器箱")
    print(df,'\n')

    df = get_ma_n(df)
    print(df,'\n')
    df = get_rv_n(df)
    print(df,'\n')
    df = get_vol_ratio_n(df)
    print(df,'\n')
    df = get_boll_n(df)
    print(df,'\n')
    df = get_rsi_n(df)
    print(df,'\n')
    drawdown = get_max_drawdown_n(df)
    print(drawdown,'\n')

    brainstorm_steam("AK-47灼心怒焰（略有磨损）")