'''
@authors: Tatiana Rijoff, tatiana.rijoff@gmail.com
@date:    11/01/2022

tj_articles allows a basic search of articles in pubmed using a combination of keywords
'''
import pandas as pd
import os
import shutil
import glob

from tj_articles_analysis import Keywords
from tj_articles_analysis import PubMedExtraction
from tj_articles_analysis import TjArticlesAnalysis

# ~ 
# ~ Prepare the environment
# ~
base_dir = 'project001/'
input_dir = base_dir  + 'input/'
output_dir = base_dir  + 'output/'
if not os.path.isdir(output_dir):
    os.mkdir(output_dir)
working_dir = base_dir + 'tmp/'
if not os.path.isdir(working_dir):
    os.mkdir(working_dir)
keys_dir = output_dir + 'keys/'
if not os.path.isdir(keys_dir):
    os.mkdir(keys_dir)
pubmed_dir = working_dir + 'pubmed/'
if not os.path.isdir(pubmed_dir):
    os.mkdir(pubmed_dir)
xml_dir = working_dir + 'xml/'
if not os.path.isdir(xml_dir):
    os.mkdir(xml_dir)
abstract_dir = working_dir + 'abstracts/'
if not os.path.isdir(abstract_dir):
    os.mkdir(abstract_dir)
latex_dir = working_dir + 'latex/'
if not os.path.isdir(latex_dir):
    os.mkdir(latex_dir)
pdf_dir = output_dir + 'pdf/'
if not os.path.isdir(pdf_dir):
    os.mkdir(pdf_dir)
img_dir = output_dir + 'img/'
if not os.path.isdir(img_dir):
    os.mkdir(img_dir)

country_df = pd.read_excel(input_dir + 'country_dict.xlsx')

# ~
# ~ keywords
# ~ 
key_list = Keywords()
# ~ Load an already created list of keywords
key_list.load_keywords_list(keys_dir + 'keywords_list.xlsx')

# ~ add data from other keys and save all the results in the excel
# default when the keywords is more than one word the sentence is between quote ' '
# key_list.find_keys_from_excel(input_dir + 'keywords.xlsx', 'TwoColumns')

# mod2 from the second column the keywords are not in quotes (this means 
# that publmed will consider an AND between the words )
key_list.find_keys_from_excel_mod2(input_dir + 'keywords.xlsx', 'TwoColumns')

# mod3 for all the columns the keywords are not in quotes (this means 
# that publmed will consider an AND between the words )
# key_list.find_keys_from_excel(input_dir + 'keywords.xlsx', 'TwoColumns')

key_list.save_keywords_list(keys_dir + 'keywords_list.xlsx')

# ~
# ~ Pubmed
# ~ 
pub_engine = PubMedExtraction()
# Load the information from a pre-saved file
pub_engine.load_pubmed_idlist(pubmed_dir + 'id_list.txt')
key_list.load_articles(keys_dir + 'articles_found.xlsx')

# Add data from the other key and save all the results in the excel
pub_engine.load_pubmed_from_key(key_list)
pub_engine.save_pubmed_idlist(pubmed_dir + 'id_list.txt')
key_list.save_keywords(keys_dir + 'keywords_list.xlsx')
key_list.save_articles(keys_dir + 'articles_found.xlsx')

# Load xml for each article
pub_engine.find_info_xml(xml_dir)

# ~
# ~ Articles analysis
# ~ 
my_analysis = TjArticlesAnalysis(country_df, abstract_dir)

# Load the information a presaved file
my_analysis.load_data_analysis(output_dir + 'info_extraction.xlsx')

# find information for the articles

for article_id in pub_engine.idlist:
    my_analysis.collect_pubmed_data(xml_dir, article_id, key_list)
print("save information in ", (output_dir + 'info_extraction.xlsx'))
my_analysis.save_data_analysis(output_dir + 'info_extraction.xlsx')
print("save information in ", (output_dir + 'revision_articles.xlsx'))
# ~ the revision excel is specific for the project and the code must be customized by user
my_analysis.save_for_review(output_dir + 'revision_articles.xlsx')

# Create pdf
for article_id in pub_engine.idlist:
    my_analysis.create_pdf(article_id, latex_dir)

for file in glob.glob(latex_dir+'*.pdf'):
    print(file)
    shutil.copy(file, pdf_dir)

# ~
# ~ Plot results
# ~ 
my_analysis.plot_years(img_dir + 'years.png')
my_analysis.plot_countries(img_dir + 'countries.png', img_dir + 'countries_collab.png')
my_analysis.plot_wordclouds_countries(img_dir + 'wordclouds_countries.png')

my_analysis.plot_pubkeys(img_dir + 'pubkeys.png')
