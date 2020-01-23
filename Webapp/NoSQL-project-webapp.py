import streamlit as st
from pymongo import MongoClient
import pandas as pd
import numpy as np
import plotly_express as px
import plotly.graph_objects as go
import copy
import json
import re
import time
import pycountry
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

def filter_q3(df, day, month, year):
    filtered_df = df.copy()
    if len(day) != 0:
        filtered_df = filtered_df[(filtered_df['Day'].isin(day))]
    if len(month) != 0:
        filtered_df = filtered_df[filtered_df['Month'].isin(month)]
    if len(year) != 0:
        filtered_df = filtered_df[filtered_df['Year'].isin(year)]
    return filtered_df

#########################################################################
#############################    Queries    ###########################
#########################################################################

def query3(source, year="2019", month ="[0-9][0-9]" , day = "[0-9][0-9]") :
    db, collection = connect_mongo('query3')
    query3_params =  {'SourceCommonName':source, "Year": year, "Month" : {"$regex": month}, "Day": {"$regex":day}}
    df_q3 = read_mongo(collection, query3_params)
    return df_q3

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


elif navigation=='Question 3':

    st.markdown('Pour une source de donnés passée en paramètre, affichez les thèmes, personnes, lieux dont les articles de cette source parlent ainsi que le nombre d’articles et le ton moyen des articles (pour chaque thème/personne/lieu); permettez une agrégation par jour/mois/année.')

    source = st.sidebar.text_input('Source name','theguardian.com')

    day = st.sidebar.selectbox('Day', ['[0-9][0-9]','01','02','03','04','05','06','07','08','09','10',
                                         '11','12','13','14','15','16','17','18','19','20',
                                         '21','22','23','24','25','26','27','28','29','30','31'])
    month = st.sidebar.selectbox('Month', ['[0-9][0-9]','01','02','03','04','05','06','07','08','09','10','11','12'])
    year = st.sidebar.selectbox('Year', ['2019','2018'])

    df_q3 = query3(source, year=year, month = month , day = day)

    df_themes = df_q3.set_index('GKGRECORDID').join(df_q3.set_index('GKGRECORDID').Themes.apply(pd.Series).stack().reset_index(level=0).rename(columns={0:'Theme'}).set_index('GKGRECORDID')).reset_index()
    df_persons = df_q3.set_index('GKGRECORDID').join(df_q3.set_index('GKGRECORDID').Persons.apply(pd.Series).stack().reset_index(level=0).rename(columns={0:'Person'}).set_index('GKGRECORDID')).reset_index()
    df_countries =df_q3.set_index('GKGRECORDID').join(df_q3.set_index('GKGRECORDID').Countries.apply(pd.Series).stack().reset_index(level=0).rename(columns={0:'Country'}).set_index('GKGRECORDID')).reset_index()

    tone_country = df_countries.groupby('Country').mean().reset_index()
    tone_person = df_persons.groupby('Person').mean().reset_index()
    tone_theme = df_themes.groupby('Theme').mean().reset_index()

    st.markdown("**Pays traités par cette source :**")

    country = tone_country.set_index('Country').join(df_countries.Country.value_counts())
    country = country.rename(columns={'Country':'Number of articles'})
    country.reset_index(inplace=True)

    fig = px.scatter(country, x="Tone", y="Number of articles", color='Country')
    st.plotly_chart(fig)

    st.markdown("**Top 10:**")
    fig = px.bar(x=df_countries.Country.value_counts().index[:10], y=df_countries.Country.value_counts().values[:10])
    st.plotly_chart(fig)

    st.markdown("**Personnes traitées par cette source :**")

    person = tone_person.set_index('Person').join(df_persons.Person.value_counts())
    person = person.rename(columns={'Person':'Number of articles'})
    person.reset_index(inplace=True)

    fig = px.scatter(person, x="Tone", y="Number of articles", color='Person')
    st.plotly_chart(fig)

    st.markdown("**Top 10:**")
    fig = px.bar(x=df_persons.Person.value_counts().index[:10], y=df_persons.Person.value_counts().values[:10])
    st.plotly_chart(fig)

    st.markdown("**Thèmes traitées par cette source :**")

    theme = tone_theme.set_index('Theme').join(df_themes.Theme.value_counts())
    theme = theme.rename(columns={'Theme':'Number of articles'})
    theme.reset_index(inplace=True)

    st.write(theme)
    #fig = px.scatter(theme, x="Tone", y="Number of articles", color='Theme')
    #st.plotly_chart(fig)

    st.markdown("**Top 10:**")
    fig = px.bar(x=df_themes.Theme.value_counts().index[:10], y=df_themes.Theme.value_counts().values[:10])
    st.plotly_chart(fig)

    def iso(country):
        pays = pycountry.countries.get(alpha_2=country)
        return pays.alpha_3

    st.write(iso('US'))

    country['iso']=country['Country'].apply(iso)
    st.write(country)

    #fig = px.choropleth(country, locations="Country", color="Tone", range_color=[20,80])


    #themes = st.sidebar.multiselect('Themes', df_themes['Theme'].unique())
    #country = st.sidebar.multiselect('Countries', df_countries['Country'].unique())
    #persons = st.sidebar.multiselect('Persons', df_persons['Person'].unique())


    #df_filtered_q3 = filter_q3(df_q3, themes, country, city, persons, day, month, year)

    #st.markdown("Nombre d'articles :")
    #df_filtered_q3.GKGRECORDID.nunique()

    #st.markdown('Ton moyen des articles:')
    #df_filtered_q3.groupby('GKGRECORDID').max().Tone.mean()

elif navigation=='Question 4':
    print("")
