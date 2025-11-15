import sqlite3
import pandas as pd
import folium
import os

from folium.plugins import LocateControl

import plotly.graph_objects as go
from folium import IFrame

BASE_DIR = os.path.dirname(os.path.abspath(__file__))   # analysis/
DB_PATH = os.path.join(BASE_DIR, "..", "data", "pa_bridges_clean.db")


def main():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("""
        SELECT STRUCTURE_NUMBER_008, LAT_016, LONG_017,
               DECK_COND_058, SUPERSTRUCTURE_COND_059,
               SUBSTRUCTURE_COND_060, LOCATION_009, DATA_YEAR
        FROM pa_bridges_clean
        WHERE DATA_YEAR = 2025
    """, conn)
    conn.close()

    df = df.dropna(subset=["LAT_016", "LONG_017"])

    m = folium.Map(location=[41.0, -77.0], zoom_start=7)

    def cond_color(c):
        if pd.isna(c):
            return "gray"
        c = int(c)
        if c <= 4:
            return "red"
        elif c <= 6:
            return "orange"
        else:
            return "green"

    for _, row in df.iterrows():
        popup = f"""
        <b>ID:</b> {row['STRUCTURE_NUMBER_008']}<br>
        <b>Location:</b> {row['LOCATION_009']}<br>
        <b>Deck:</b> {row['DECK_COND_058']}<br>
        <b>Super:</b> {row['SUPERSTRUCTURE_COND_059']}<br>
        <b>Sub:</b> {row['SUBSTRUCTURE_COND_060']}<br>
        <b>Year:</b> {row['DATA_YEAR']}
        """
        folium.CircleMarker(
            location=[row["LAT_016"], row["LONG_017"]],
            radius=4,
            color=cond_color(row["DECK_COND_058"]),
            fill=True,
            fill_opacity=0.8,
            popup=folium.Popup(popup, max_width=500)
        ).add_to(m)

    legend_html = """
     <div style="position: fixed; 
                 bottom: 50px; left: 50px; width: 150px; height: 120px; 
                 border:2px solid grey; z-index:9999; font-size:14px;
                 background-color:white;
                 ">
     &nbsp;<b>Condition Legend</b><br>
     &nbsp;<i class="fa fa-circle" style="color:green"></i>&nbsp;Good (7-9)<br>
     &nbsp;<i class="fa fa-circle" style="color:orange"></i>&nbsp;Fair (5-6)<br>
     &nbsp;<i class="fa fa-circle" style="color:red"></i>&nbsp;Poor (0-4)<br>
     &nbsp;<i class="fa fa-circle" style="color:gray"></i>&nbsp;Unknown<br>
     </div>
     """
    m.get_root().html.add_child(folium.Element(legend_html))

    LocateControl(auto_start=False).add_to(m)


    cond_counts = df["DECK_COND_058"].value_counts().sort_index()

    fig = go.Figure(data=[
        go.Bar(x=cond_counts.index.astype(str), y=cond_counts.values)
    ])


    fig.update_layout(
        title=dict(
            text="Bridge Deck Condition Distribution",
            x=0.5,
            xanchor='center',
            font=dict(size=14)
        ),

        height=230,
        margin=dict(l=30, r=10, t=35, b=35), 
    )


    chart_html = fig.to_html(
        full_html=False,
        include_plotlyjs='cdn',
        config={
            'responsive': True,
            'displaylogo': False, 
            'modeBarButtonsToRemove': [
                'zoom2d', 'pan2d', 'select2d', 'lasso2d',
                'zoomIn2d', 'zoomOut2d', 'autoScale2d',
                'resetScale2d'
            ]
        }
    )


    floating_chart_html = f'''
    <div id="chart-container" style="
        position: fixed;
        bottom: 20px;
        right: 20px;

        width: 350px;
        height: 260px;

        background: rgba(255,255,255,0.85);
        backdrop-filter: blur(6px);
        border-radius: 12px;
        border: 1px solid rgba(200,200,200,0.6);
        box-shadow: 0px 4px 14px rgba(0,0,0,0.25);

        z-index: 999999;
        padding: 8px;
        overflow: hidden;
    ">
        <div style="font-weight:bold; text-align: center; margin-bottom: 4px; font-size: 14px;">
            Bridge Condition Chart
        </div>

        {chart_html}
    </div>
    '''


    m.get_root().html.add_child(folium.Element(floating_chart_html))


            


    m.save("../frontend/map.html")
    print("Map saved to frontend/map.html")

if __name__ == "__main__":
    main()
