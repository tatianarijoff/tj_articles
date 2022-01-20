# tj_articles
## Table of contents
 - [Introduction](#introduction)
 - [Prerequisites](#prerequisites)
 - [Tasks performed by tj_article](#tasks-performed-by-pytlwall)
 - [Structure of the package](#structure-of-the-package)

## Introduction
"tj_articles" is a python code which allows to search articles in pubmed and collect some
information about.

It is also possible to calculate the impedance of a list of chambers to "build" an entire accelerator.

## prerequisites
tj_articles requires python3 with 
- pandas
- numpy
- matplotlib
- seaborn
- biopython 
- pylatex
- worlcloud

## Tasks performed by tj_articles

The tj_articles
- allows to combine columns of keywords with different type of combination
- for each keywords combination extract the pubmed article_id
- for each pubmed article id extract the xml, collec the xml information, create a dataframe with these datas
- in addition to the dataframe allows to export data in a specific excel with the columns needed by the revision process
- allows to plot the results

## Structure of the package

 - The **source code** is in tj_articles_analysis folder.
 - **run_analysis.py** allows you to run the analysis
 - **article_search.ipnb** allows you to run the analysis with jupyter
 - **License** information is contained in the file "LICENSE.txt"
 - This **documentation** is contained in the file "README.md"
 - The analysis would start from a project directory, the default is project001 and the input files are in the input folder inside the project directory
   the output and working directory are automatically created
   
