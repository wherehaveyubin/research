# 🌎 Research Repository by Yubin Lee

This repository contains Python code, spatial analysis tools, and visualizations used in my academic papers and conference presentations. It includes work in **accessibility, urban human mobility, network, spatial regression analysis**.

<br/>

## 📚 Table of Contents
- [Overview]
- [1. COVID-19 Medical Accessibility in Korea]
- [2. Healthcare Accessibility using Card and Telecom Data]
- [3. Urban Mobility and Bike-Sharing in the US]
- [Tech Stack]

<br/>

## 📍 Overview

My research primarily focuses on spatial accessibility and human mobility to understand and improve urban systems.  
This repository is organized by research topic, with each section linking to relevant project folders and publications.

<br/>

## 1. 😷 COVID-19 Medical Accessibility in Korea

Analysis of accessibility to beds in the Negative Pressure Isolation Room (NPIR) in Seoul, Gyeonggi, and Incheon.
<br/>
- Data: crawled NPIR beds capacity, cralwed COVID-19 confirmed case, building type
- Methods: 2SFCA, E2SFCA, GWR

| Year | Project | Description |
|------|---------|-------------|
| 2021 | [Master’s Thesis](./2021-masters-thesis) | 2SFCA analysis of isolation facility access and GWR on confirmed case building types in Seoul, Gyeonggi, and Incheon, South Korea. |
| 2023 | [Updated Accessibility Analysis (Seoul)](./2023-Accessibility-to-Isolation-Beds-in-Seoul) | Enhanced E2SFCA with updated data. |

<br/>

## 2. 🏥 Healthcare Accessibility using Credit Card and Mobile Phone Data

Accessibility to nighttime hospitals on weekdays and weekends using E2SFCA and multi-source mobility data (card + telecom) in Seoul and Gyeongbuk, South Korea.
<br/>
- Data: Shinhan credit card transaction, SK telecom mobility data, crawled nighttime-available doctor capacity
- Methods: E2SFCA

| Year | Project | Description |
|------|---------|-------------|
| 2024 | [Night-Time Hospital Access](./2024-Night-Time-Hospital-Accessibility) | Analyzed regional disparities in night-time hospital accessibility using mobility data and the E2SFCA method. |

<br/>

## 3. 🚲 Urban Mobility and Bike-Sharing in the US

Analysis of shared bike usage in Austin, Texas using community detection, 2SFCA, and GWR.
<br/>
- Data: MetroBike transaction
- Methods: Community detection, 2SFCA, GWR

| Year | Project | Description |
|------|---------|-------------|
| 2025 | [MetroBike Study](./2025-MetroBike) | Evaluated shared bike usage patterns and accessibility across Census Block Groups (CBGs) in Austin, Texas. |

<br/>

## ⚙️ Tech Stack

- **Python**: Pandas, GeoPandas, NetworkX
- **GIS**: ArcGIS Pro, QGIS
- **Visualization**: Matplotlib, Seaborn
- **Data**: (crawled) data from government websites, credit card (Shinhan card) data, mobile phone (SK telecom) data
  
<br/>
