import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px

# GeoJson file of Indonesian Provinces is taken from https://github.com/Vizzuality/growasia_calculator/blob/master/public/indonesia.geojson
# Kudos to the contributors

APP_TITLE = "Car Ownership-Population Ratio in Indonesia 2019-2021"
subhead = "The map and table is updated based on year basis. If you wish to view only specific province(s), just filter it out on the left side bar."

@st.cache()
def get_data():
    return pd.read_excel("Jumlah Kendaraan.xlsx")
def display_map(df,year):
    df = df[df["Year"]==year]
    
    map = folium.Map(location=[-1,120],zoom_start=4.1,
    titles = "CartoDB positron")
    
    choropleth = folium.Choropleth(
        geo_data="indonesia-prov.geojson",
        data=df,
        columns=("id","Number of cars per 1000 people"),
        key_on="id",
        fill_color="YlOrRd",
        line_opacity=0.8,
        highlight=True,
        legend=True
        )
    choropleth.geojson.add_to(map)
    
    for f in choropleth.geojson.data["features"]:
        f["properties"]["ratio"] = "car ratio per 1000 pop : " + "{0:.2f}".format(list(df.loc[(df['Year']==year) & (df['id']== f["id"]), "Number of cars per 1000 people"])[0])
    
    choropleth.geojson.add_child(
        folium.features.GeoJsonTooltip(["Propinsi","ratio"], 
                                       labels=False))
    
    st_map = st_folium(map,width=500,height=300)
    return st_map
    

def main():
    st.set_page_config(APP_TITLE,page_icon=":bar_chart:",layout="wide")
    st.title(f":bar_chart: {APP_TITLE}") 
    st.subheader(subhead)
    
    df = get_data()
    # display year filters
    year = st.sidebar.selectbox("Choose year here: ", [2021,2020,2019])
    
    
    
    # display province filter
    listprov = ["All"]
    listprov.extend(df["Province"].unique())
    province = st.sidebar.multiselect("Select province to display on the table: ", 
                                      options = listprov,
                                      default="All")
    
    # display car number, national population, and national average
    st.header(f"National summary at year {year}")
    
    dfnat = df.query("Year == @year")
    num_car = dfnat["Car"].sum()
    pop = dfnat["Population (in thousands)"].sum()
    natavg = "{0:.2f}".format(num_car/pop)
    
    lcol, midcol, rcol = st.columns(3)
    with lcol:
        st.write(f"Countrywide number of cars in {year} is:")
        st.write(f"{num_car} cars")
    
    with midcol:
        st.write(f"Indonesian population at year {year} is:")
        st.write(f"{pop}000 people")
    
    with rcol:
        st.write(f"National car to population per 1000 people in {year} is:")
        st.write(f"{natavg} cars per 1000 people")
 
    
 
    lcol,rcol = st.columns(2)
    
    # displaying filtered data
    df_selected = df
    if province == ["All"]:
        df_selected = df.query("Year == @year").loc[:,["Province",
                                                       "Population (in thousands)",
                                                       "Number of cars per 1000 people",
                                                       "Year"]]
    elif province != "All":
        df_selected = df.query("Year == @year & Province == @province").loc[:,["Province",
                                                       "Population (in thousands)",
                                                       "Number of cars per 1000 people",
                                                       "Year"]]
    
    with lcol:
        st.write("Data Summary")
        st.write("")
        st.write(df_selected[["Province",
                                     "Population (in thousands)",
                                     "Number of cars per 1000 people"]])

    
    # display map
    with rcol:
        st.write("Interactive map showing car ownership - population ratio density")
        display_map(df,year)
    
    # display top 5 highest
    st.subheader(f"Provinces with highest Car-Population Ratio in year {year}")
    top5high = df.query("Year == @year").nlargest(5,"Number of cars per 1000 people").loc[:,["Province","Number of cars per 1000 people"]].sort_values(by="Number of cars per 1000 people",ascending=True)
    figtop5 = px.bar(top5high,
                      x="Number of cars per 1000 people",
                      y=top5high.Province,
                      orientation="h",
                      title="5 Provinces with highest Car-Population Ratio")
    st.plotly_chart(figtop5)
    
    # display top 5 lowest
    
    st.subheader(f"Provinces with lowest Car-Population Ratio in year {year}")
    bot5low = df.query("Year == @year").nsmallest(5,
                                                  "Number of cars per 1000 people").loc[:,["Province","Number of cars per 1000 people"]].sort_values(by="Number of cars per 1000 people",ascending=True)

    figbot5 = px.bar(bot5low,
                      x="Number of cars per 1000 people",
                      y=bot5low.Province,
                      orientation="h",
                      title="5 Provinces with lowest Car-Population Ratio")
    figbot5.update_xaxes(range=[0,300])
    st.plotly_chart(figbot5)
    
    
    
    
if __name__ == '__main__':
    main()