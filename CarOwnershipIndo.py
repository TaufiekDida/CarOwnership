import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

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
    
    st_map = st_folium(map,width=700,height=450)
    

def main():
    st.set_page_config(APP_TITLE)
    st.title(APP_TITLE) 
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
    st.write(df_selected)

    
    # display map
    st.subheader("Interactive map showing car ownership - population ratio density")
    display_map(df,year)
    
    # display top 5 highest
    st.subheader("5 Provinces with highest Car-Population Ratio")
    st.write(df.query("Year == @year").nlargest(5,"Number of cars per 1000 people"))
    
    # display top 5 lowest
    st.subheader("\n\n 5 Provinces with lowest Car-Population Ratio")
    st.write(df.query("Year == @year").nsmallest(5,"Number of cars per 1000 people"))
    
    
    
    
if __name__ == '__main__':
    main()
