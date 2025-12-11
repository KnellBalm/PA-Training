import os
import duckdb
import plotly.graph_objects as go

DB_PATH = os.getenv("DUCKDB_PATH", "db/event_log.duckdb")


def revenue_timeseries():
    con = duckdb.connect(DB_PATH)
    df = con.execute("SELECT date, revenue FROM daily_metrics ORDER BY date").df()
    con.close()

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df["date"],
            y=df["revenue"],
            mode="lines+markers",
            name="Revenue",
        )
    )
    fig.update_layout(
        title="Daily Revenue",
        xaxis_title="Date",
        yaxis_title="Revenue",
        template="plotly_dark",
    )
    return fig
