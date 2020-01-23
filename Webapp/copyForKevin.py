import streamlit as st
from pymongo import MongoClient
import pandas as pd
import numpy as np
import plotly_express as px
import pycountry

import plotly.graph_objects as go
import copy
import json
import re
import time
import os.path

st.title('Projet NoSQL')

#########################################################################
#############################    Functions    ###########################
#########################################################################

def connect_mongo(collection_name):

    client = MongoClient("mongodb://gdeltuser:gdeltpass@172.31.24.60:27017,172.31.28.231:27017,172.31.25.118:27017/gdelt." + collection_name + "?replicaSet=rsGdelt", readPreference='primaryPreferred')

    db = client['gdelt']
    collection = db[collection_name]
    return db, collection

def read_mongo(collection, query={}, no_id=True):
    """ Read from Mongo and Store into DataFrame """

    # Make a query to the specific DB and Collection
    cursor = collection.find(query)

    # Expand the cursor and construct the DataFrame
    df =  pd.DataFrame(list(cursor))

    # Delete the _id
    if no_id:
        del df['_id']

    return df

def filter_q3(df, themes, country, city, persons, day, month, year):
    filtered_df = df.copy()
    if len(themes) != 0 :
        filtered_df = filtered_df[(filtered_df['Themes'].isin(themes))]
        mode ='city'
    if len(country) != 0:
        filtered_df = filtered_df[(filtered_df['Country'].isin(country))]
    if len(city) != 0:
        filtered_df = filtered_df[filtered_df['City'].isin(city)]
    if len(persons) != 0:
        filtered_df = filtered_df[filtered_df['Persons'].isin(persons)]
    if len(day) != 0:
        filtered_df = filtered_df[(filtered_df['Day'].isin(day))]
    if len(month) != 0:
        filtered_df = filtered_df[filtered_df['Month'].isin(month)]
    if len(year) != 0:
        filtered_df = filtered_df[filtered_df['year'].isin(year)]
    return filtered_df

#########################################################################
#############################    Queries    ###########################
#########################################################################

def query3(source) :
    db, collection = connect_mongo('query3')
    df_q3 = read_mongo(collection, {'SourceCommonName':source})
    return df_q3

def query2(source, year="2019", month ="[0-9][0-9]" , day = "[0-9][0-9]") :
    db, collection = connect_mongo('query2')
    if type(month) == list :
        month = "|".join(month)
    if type(day) == list :
        day = "|".join(day)
    query2_params =  {"ActionGeo_CountryCode": source, "Year": year, "Month" : {"$regex": month}, "Day": {"$regex":day}}
    df_q2 = read_mongo(collection, query2_params)
    df_q2 = df_q2.sort_values(by = "numMentions", ascending = False)
    return df_q2

def iso(country):
    pays = pycountry.countries.get(alpha_2=country.upper())
    if pays is not None:
        return pays.alpha_3
    else:
        return ''

#########################################################################
###########################    Visualization    #########################
#########################################################################

navigation = st.sidebar.radio("Navigation",('Home','Question 1', 'Question 2','Question 3', 'Question 4'))

if navigation=='Home':
    st.markdown(r'''
    ------------------------
    # Intro
    ------------------------

    *" The Global Database of Events, Language, and Tone (GDELT), est une initiative pour construire un catalogue de comportements et de croyances sociales à travers le monde, reliant chaque personne, organisation, lieu, dénombrement, thème, source d’information, et événement à travers la planète en un seul réseau massif qui capture ce qui se passe dans le monde, le contexte, les implications ainsi que la perception des gens sur chaque jour".*

    Cette base de données a eu beaucoup d’utilisations, pour mieux comprendre l’évolution et l’impact de la crise financière du 2008 (Bayesian dynamic financial networks with time-varying predictors) ou analyser l’évolution des relations entre des pays impliquées dans des conflits (Massive Media Event Data Analysis to Assess World-Wide Political Conflict and Instability ).

    L’objectif du projet est de concevoir un système qui permet d’analyser le jeu de donnees GDELT et ses sources de donnees.

    ------------------------
    # Objectif
    ------------------------

    L’objectif de ce projet est de proposer un système de stockage distribué, résilient et performant sur AWS pour repondre aux question suivantes:
    * afficher le nombre d’articles/évènements qu’il y a eu pour chaque triplet (jour, pays de l’évènement, langue de l’article).
    * pour un pays donné en paramètre, affichez les évènements qui y ont eu place triées par le nombre de mentions (tri décroissant); permettez une agrégation par jour/mois/année
    * pour une source de donnés passée en paramètre (gkg.SourceCommonName) affichez les thèmes, personnes, lieux dont les articles de cette sources parlent ainsi que le le nombre d’articles et le ton moyen des articles (pour chaque thème/personne/lieu); permettez une agrégation par jour/mois/année.
    * dresser la cartographie des relations entre les pays d’après le ton des articles : pour chaque paire (pays1, pays2), calculer le nombre d’article, le ton moyen (aggrégations sur Année/Mois/Jour, filtrage par pays ou carré de coordonnées)

    ''')

elif navigation=='Question 1':
    print("")


elif navigation=='Question 2':
    print("")
    #db, collection = connect_mongo('query2')
    #df_q2 = read_mongo(collection, {})


    source = st.sidebar.text_input('Pays :', "FR")
    year = st.sidebar.selectbox("Année :", ["2018","2019","2017","2020"])
    month = st.sidebar.multiselect("Mois :", ["[0-1][0-9]","01","02","03", "04","05","06","07","08","09","10","11","12"])
    day = st.sidebar.multiselect("Jour :", ["[0-1][0-9]","01","02","03", "04","05","06","07","08","09","10","11","12",
                                          "13","14","15", "16","17","18","19","20","21","22","23","24", "25","26","27","28", "29", "30"])

#source = st.sidebar.selectbox('Pays :', ["US", "FR", "EN"])
    df_q2 = query2(source, year=year, month=month, day=day).copy()
    st.dataframe(df_q2)
    #df = px.data.gapminder()
    df = df_q2.groupby(["ActionGeo_CountryCode","Month"]).sum()
    df['iso']=df['Country'].apply(iso)
    fig = px.choropleth(df, locations="iso", color="numMentions", animation_frame="Month", range_color=[20,80], width=800, height=800)
    st.plotly_chart(fig)
    print("")


elif navigation=='Question 3':

    st.markdown('Pour une source de donnés passée en paramètre, affichez les thèmes, personnes, lieux dont les articles de cette source parlent ainsi que le le nombre d’articles et le ton moyen des articles (pour chaque thème/personne/lieu); permettez une agrégation par jour/mois/année.')

    source = st.text_input('Source name', 'theguardian.com')

    df_q3 = query3(source).copy()

    df_q3.nunique()

    themes = st.sidebar.multiselect('Themes', df_q3['Themes'].unique())
    country = st.sidebar.multiselect('Country', df_q3['Country'].unique())
    city = st.sidebar.multiselect('City', df_q3['City'].unique())
    persons = st.sidebar.multiselect('Persons', df_q3['Persons'].unique())
    day = st.sidebar.multiselect('Day', df_q3['Day'].unique())
    month = st.sidebar.multiselect('Month', df_q3['Month'].unique())
    year = st.sidebar.multiselect('Year', df_q3['Year'].unique())

    df_filtered_q3 = filter_q3(df_q3, themes, country, city, persons, day, month, year)

    st.markdown("Nombre d'articles :")
    df_filtered_q3.GKGRECORDID.nunique()

    st.markdown('Ton moyen des articles:')
    df_filtered_q3.groupby('GKGRECORDID').max().Tone.mean()

elif navigation=='Question 4':
    print("")
