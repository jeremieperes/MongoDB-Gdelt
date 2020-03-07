# GDELT Exploration

Project carried out as part of the MS BigData 2019/2020 at Télécom Paris by : 
- Li XU
- Benyang SUN
- Jérémie PERES
- Kevin FERIN

## Introduction

"The Global Database of Events, Language, and Tone (GDELT), is an initiative to build a catalogue of social behaviours and beliefs around the world, linking every person, organisation, place, count, theme, source of information, and event across the planet into one massive network that captures what is happening in the world, the context, implications, and people's perception of each day.

This database has had many uses, to better understand the evolution and impact of the 2008 financial crisis (Bayesian dynamic financial networks with time-varying predictors) or to analyse the evolution of relations between countries involved in conflicts (Massive Media Event Data Analysis to Assess World-Wide Political Conflict and Instability).

The aim of the project is to build an architecture for analysing the GDELT dataset and its data sources.

## Objective

The objective of this project is to propose a distributed, resilient and high-performance storage system on AWS to answer the following questions:

- Display the number of articles/events there were for each triplet (day, country of the event, language of the article).
- For a given country in parameter, display the events that took place there sorted by the number of mentions (descending sort); allow an aggregation by day/month/year.
- For a data source passed in parameter (gkg.SourceCommonName) display the themes, people, places that the articles of this source talk about as well as the number of articles and the average tone of the articles (for each theme/person/place); allow aggregation by day/month/year.
- Map the relationships between countries according to the tone of the articles: for each pair (country1, country2), calculate the number of articles, the average tone (aggregating to Year/Month/Day, filtering by country or square of coordinates)

## Architecture

![Architecture](Images/Archi.png)

The installation of the architecture on AWS is described step by step in [ce Markdown](Configuration_Environment_AWS.md)

## ETL

The ETL process of the GDELT files was done in a Zeppelin Notebook, using Spark (Scala). The Notebook is available in the [Notebooks](Notebooks)

## Webapp

The webapp was made in Python via the [Streamlit](https://www.streamlit.io/) library. The Python script of the webapp is available in the folder [Webapp](Webapp)

Below are some screenshots of the webapp :

**Number of articles between the US and France in 2019**

![NbArticle-FR-US](Images/NbArticle-FR-US.png)

**World media coverage (i.e. for each country the average value of Number of articles / Number of events)**

![Couverture-mediatique](Images/Couverture-mediatique.png)

More vizualisation examples are available in the [Images](Images) folder.


## Launching the visualization webapp

After loading the data into the MongoDB collections, run the following lines of code :

- **Project clone :**
```
git clone https://github.com/jeremieperes/MongoDB-Gdelt.git
```
- **Launching the web app :**
```
cd Webapp
streamlit run NoSQL-project-webapp.py
```

- **Viewing:**
Open a browser then :
```
locahost:8501
```
