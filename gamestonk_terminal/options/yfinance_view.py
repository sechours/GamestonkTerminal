"""Yfinance options view"""
__docformat__ = "numpy"

import os
from bisect import bisect_left

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import yfinance as yf

import gamestonk_terminal.config_plot as cfp
import gamestonk_terminal.feature_flags as gtff
from gamestonk_terminal.helper_funcs import export_data, plot_autoscale
from gamestonk_terminal.options import op_helpers, yfinance_model


def plot_oi(
    ticker: str,
    expiry: str,
    min_sp: float,
    max_sp: float,
    calls_only: bool,
    puts_only: bool,
    export: str,
):
    """Plot open interest

    Parameters
    ----------
    ticker: str
        Ticker
    expiry: str
        Expiry date for options
    min_sp: float
        Min strike to consider
    max_sp: float
        Max strike to consider
    calls_only: bool
        Show calls only
    puts_only: bool
        Show puts only
    export: str
        Format to export file
    """
    options = yfinance_model.get_option_chain(ticker, expiry)
    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "oi_yf",
        options,
    )
    calls = options.calls
    puts = options.puts
    current_price = float(yf.Ticker(ticker).info["regularMarketPrice"])

    if min_sp == -1:
        min_strike = 0.75 * current_price
    else:
        min_strike = min_sp

    if max_sp == -1:
        max_strike = 1.25 * current_price
    else:
        max_strike = max_sp

    if calls_only and puts_only:
        print("Both flags selected, please select one", "\n")
        return

    call_oi = calls.set_index("strike")["openInterest"] / 1000
    put_oi = puts.set_index("strike")["openInterest"] / 1000

    df_opt = pd.merge(call_oi, put_oi, left_index=True, right_index=True)
    df_opt = df_opt.rename(
        columns={"openInterest_x": "OI_call", "openInterest_y": "OI_put"}
    )

    max_pain = op_helpers.calculate_max_pain(df_opt)
    plt.style.use("classic")
    fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=cfp.PLOT_DPI)

    if not calls_only:
        put_oi.plot(
            x="strike",
            y="openInterest",
            label="Puts",
            ax=ax,
            marker="o",
            ls="-",
            c="r",
        )
    if not puts_only:
        call_oi.plot(
            x="strike",
            y="openInterest",
            label="Calls",
            ax=ax,
            marker="o",
            ls="-",
            c="g",
        )
        ax.axvline(
            current_price, lw=2, c="k", ls="--", label="Current Price", alpha=0.7
        )
        ax.axvline(max_pain, lw=3, c="k", label=f"Max Pain: {max_pain}", alpha=0.7)
        ax.grid("on")
        ax.set_xlabel("Strike Price")
        ax.set_ylabel("Open Interest (1k) ")
        ax.set_xlim(min_strike, max_strike)

        if gtff.USE_ION:
            plt.ion()

        ax.set_title(f"Open Interest for {ticker.upper()} expiring {expiry}")
        plt.legend(loc=0)
        fig.tight_layout(pad=1)

    plt.show()
    plt.style.use("default")
    print("")


def plot_vol(
    ticker: str,
    expiry: str,
    min_sp: float,
    max_sp: float,
    calls_only: bool,
    puts_only: bool,
    export: str,
):
    """Plot volume

    Parameters
    ----------
    ticker: str
        Ticker
    expiry: str
        Expiry date for options
    min_sp: float
        Min strike to consider
    max_sp: float
        Max strike to consider
    calls_only: bool
        Show calls only
    puts_only: bool
        Show puts only
    export: str
        Format to export file
    """
    options = yfinance_model.get_option_chain(ticker, expiry)
    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "vol_yf",
        options,
    )
    calls = options.calls
    puts = options.puts
    current_price = float(yf.Ticker(ticker).info["regularMarketPrice"])

    if min_sp == -1:
        min_strike = 0.75 * current_price
    else:
        min_strike = min_sp

    if max_sp == -1:
        max_strike = 1.25 * current_price
    else:
        max_strike = max_sp

    if calls_only and puts_only:
        print("Both flags selected, please select one", "\n")
        return

    call_v = calls.set_index("strike")["volume"] / 1000
    put_v = puts.set_index("strike")["volume"] / 1000
    plt.style.use("classic")
    fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=cfp.PLOT_DPI)

    if not calls_only:
        put_v.plot(
            x="strike",
            y="volume",
            label="Puts",
            ax=ax,
            marker="o",
            ls="-",
            c="r",
        )
    if not puts_only:
        call_v.plot(
            x="strike",
            y="volume",
            label="Calls",
            ax=ax,
            marker="o",
            ls="-",
            c="g",
        )
    ax.axvline(current_price, lw=2, c="k", ls="--", label="Current Price", alpha=0.7)
    ax.grid("on")
    ax.set_xlabel("Strike Price")
    ax.set_ylabel("Volume (1k) ")
    ax.set_xlim(min_strike, max_strike)

    if gtff.USE_ION:
        plt.ion()

    ax.set_title(f"Volume for {ticker.upper()} expiring {expiry}")
    plt.legend(loc=0)
    fig.tight_layout(pad=1)

    plt.show()
    plt.style.use("default")
    print("")


def plot_volume_open_interest(
    ticker: str,
    expiry: str,
    min_sp: float,
    max_sp: float,
    min_vol: float,
    export: str,
):
    """Plot volume and open interest

    Parameters
    ----------
    ticker: str
        Stock ticker
    expiry: str
        Option expiration
    min_sp: float
        Min strike price
    max_sp: float
        Max strike price
    min_vol: float
        Min volume to consider
    export: str
        Format for exporting data
    """

    options = yfinance_model.get_option_chain(ticker, expiry)
    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "voi_yf",
        options,
    )
    calls = options.calls
    puts = options.puts
    current_price = float(yf.Ticker(ticker).info["regularMarketPrice"])

    # Process Calls Data
    df_calls = calls.pivot_table(
        index="strike", values=["volume", "openInterest"], aggfunc="sum"
    ).reindex()
    df_calls["strike"] = df_calls.index
    df_calls["type"] = "calls"
    df_calls["openInterest"] = df_calls["openInterest"]
    df_calls["volume"] = df_calls["volume"]
    df_calls["oi+v"] = df_calls["openInterest"] + df_calls["volume"]
    df_calls["spot"] = round(current_price, 2)

    df_puts = puts.pivot_table(
        index="strike", values=["volume", "openInterest"], aggfunc="sum"
    ).reindex()
    df_puts["strike"] = df_puts.index
    df_puts["type"] = "puts"
    df_puts["openInterest"] = df_puts["openInterest"]
    df_puts["volume"] = -df_puts["volume"]
    df_puts["openInterest"] = -df_puts["openInterest"]
    df_puts["oi+v"] = df_puts["openInterest"] + df_puts["volume"]
    df_puts["spot"] = round(current_price, 2)

    call_oi = calls.set_index("strike")["openInterest"] / 1000
    put_oi = puts.set_index("strike")["openInterest"] / 1000

    df_opt = pd.merge(call_oi, put_oi, left_index=True, right_index=True)
    df_opt = df_opt.rename(
        columns={"openInterest_x": "OI_call", "openInterest_y": "OI_put"}
    )

    max_pain = op_helpers.calculate_max_pain(df_opt)

    if min_vol == -1 and min_sp == -1 and max_sp == -1:
        # If no argument provided, we use the percentile 50 to get 50% of upper volume data
        volume_percentile_threshold = 50
        min_vol_calls = np.percentile(df_calls["oi+v"], volume_percentile_threshold)
        min_vol_puts = np.percentile(df_puts["oi+v"], volume_percentile_threshold)

        df_calls = df_calls[df_calls["oi+v"] > min_vol_calls]
        df_puts = df_puts[df_puts["oi+v"] < min_vol_puts]

    else:
        if min_vol > -1:
            df_calls = df_calls[df_calls["oi+v"] > min_vol]
            df_puts = df_puts[df_puts["oi+v"] < -min_vol]

        if min_sp > -1:
            df_calls = df_calls[df_calls["strike"] > min_sp]
            df_puts = df_puts[df_puts["strike"] > min_sp]

        if max_sp > -1:
            df_calls = df_calls[df_calls["strike"] < max_sp]
            df_puts = df_puts[df_puts["strike"] < max_sp]

    if df_calls.empty and df_puts.empty:
        print(
            "The filtering applied is too strong, there is no data available for such conditions.\n"
        )
        return

    # Initialize the matplotlib figure
    _, ax = plt.subplots(figsize=plot_autoscale(), dpi=cfp.PLOT_DPI)

    # make x axis symmetric
    axis_origin = max(abs(max(df_puts["oi+v"])), abs(max(df_calls["oi+v"])))
    ax.set_xlim(-axis_origin, +axis_origin)

    sns.set_style(style="darkgrid")

    g = sns.barplot(
        x="oi+v",
        y="strike",
        data=df_calls,
        label="Calls: Open Interest",
        color="lightgreen",
        orient="h",
    )

    g = sns.barplot(
        x="volume",
        y="strike",
        data=df_calls,
        label="Calls: Volume",
        color="green",
        orient="h",
    )

    g = sns.barplot(
        x="oi+v",
        y="strike",
        data=df_puts,
        label="Puts: Open Interest",
        color="pink",
        orient="h",
    )

    g = sns.barplot(
        x="volume",
        y="strike",
        data=df_puts,
        label="Puts: Volume",
        color="red",
        orient="h",
    )

    # draw spot line
    s = [float(strike.get_text()) for strike in ax.get_yticklabels()]
    spot_index = bisect_left(s, current_price)  # find where the spot is on the graph
    spot_line = ax.axhline(spot_index, ls="--", color="dodgerblue", alpha=0.3)

    # draw max pain line
    max_pain_index = bisect_left(s, max_pain)
    max_pain_line = ax.axhline(max_pain_index, ls="-", color="black", alpha=0.3)
    max_pain_line.set_linewidth(3)

    # format ticklabels without - for puts
    g.set_xticks(g.get_xticks())
    xlabels = [f"{x:,.0f}".replace("-", "") for x in g.get_xticks()]
    g.set_xticklabels(xlabels)

    plt.title(
        f"{ticker} volumes for {expiry} (open interest displayed only during market hours)"
    )
    ax.invert_yaxis()

    _ = ax.legend()
    handles, _ = ax.get_legend_handles_labels()
    handles.append(spot_line)
    handles.append(max_pain_line)

    # create legend labels + add to graph
    labels = [
        "Calls open interest",
        "Calls volume ",
        "Puts open interest",
        "Puts volume",
        "Current stock price",
        f"Max pain = {max_pain}",
    ]

    plt.legend(handles=handles[:], labels=labels)
    sns.despine(left=True, bottom=True)

    if gtff.USE_ION:
        plt.ion()
    plt.show()
    plt.style.use("default")
    print("")
