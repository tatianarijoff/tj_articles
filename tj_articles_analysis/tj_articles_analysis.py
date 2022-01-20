import numpy as np
import pandas as pd
import os
import re
import xml.etree.ElementTree as ET
from pylatex import Document, Section, Subsection, Command, LargeText
from pylatex.utils import italic, NoEscape, bold
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import seaborn as sns
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator


class TjArticlesAnalysis(object):
    '''The TjArticlesAnalysis object collects the articles informations in a useful
       DataFrame and allows some output analysis'''
    def __init__(self, country_df, abstract_dir):
        self.country_dict = country_df
        self.data_analysis = pd.DataFrame()
        self.create_data_structs()
         
        self.abstract_dir = abstract_dir
        return

    def create_data_structs(self):
        '''The create_data_columns function generates the analysis_data
            columns.'''
        self.data_analysis['id'] = ''
        self.data_analysis['filename'] = ''
        self.data_analysis['orig'] = ''
        self.data_analysis['to_be_included'] = ''
        self.data_analysis['year'] = ''
        self.data_analysis['language'] = ''
        self.data_analysis['first_author'] = ''
        self.data_analysis['title'] = ''
        self.data_analysis['journal'] = ''
        self.data_analysis['pub_type'] = ''
        self.data_analysis['authors'] = ''
        self.data_analysis['authors_info'] = ''
        self.data_analysis['country'] = ''
        self.data_analysis['keywords_major'] = ''
        self.data_analysis['keywords_minor'] = ''
        self.data_analysis['search_key'] = ''

        return

    def collect_pubmed_data(self, xml_dir, article_id, keywords):
        print(f'Collecting data for {article_id}')
        mytree = ET.parse(xml_dir + article_id + '.xml')
        xml_data = mytree.getroot()
        ind = self.data_analysis.index[self.data_analysis['id'] ==
                                           article_id].tolist()
        if len(ind) == 0:
            data = pd.DataFrame([article_id], columns=['id'])
            self.data_analysis = self.data_analysis.append(data,
                                                            ignore_index=True)
        ind = self.data_analysis.index[self.data_analysis['id'] ==
                                           article_id].tolist()
        self.read_authors_countries(ind, xml_data)
        self.read_year(ind, xml_data)
        filename = str(ind[0]) + '_' + \
                   self.data_analysis.loc[ind, 'first_author'] +  '_' + \
                   self.data_analysis.loc[ind, 'year']
        self.data_analysis.loc[ind, 'filename'] =  filename
        self.data_analysis.loc[ind, 'orig'] = 'Pubmed'
        self.data_analysis.loc[ind, 'to_be_included'] = True
        self.read_title(ind, xml_data)
        self.read_language(ind, xml_data)
        if ( self.data_analysis.loc[ind, 'language'].values[0] != 'eng'):
            self.data_analysis.loc[ind, 'to_be_included'] = False
        self.read_journal(ind, xml_data)
        self.read_publication_type(ind, xml_data)
        list_keys = keywords.find_keys_str(article_id)
        print(list_keys)
        self.data_analysis.loc[ind, 'search_key'] = list_keys
        self.read_keywords(ind, xml_data)
        self.write_abstract(article_id, xml_data)

    def read_authors_countries(self, ind, xml_data):
        authors_list = []
        authors_info = []
        country_list = []
        country_final_list = []
        count_line = 0
        for author in xml_data.iter('Author'):
            for el in author.iter():
                if (el.tag == 'LastName'):
                    author_name = el.text
                    author_info = author_name
                    authors_list.append(author_name)
                    if count_line == 5:
                        authors_list.append("\\")
                        count_line = 0
                elif (el.tag == 'CollectiveName'):
                    author_name = el.text
                    author_info = author_name
                    authors_list.append(author_name)
                    if count_line == 5:
                        authors_list.append("\\")
                        count_line = 0
                if(el.tag == 'Affiliation'):
                    affil = el.text
                    country = self.find_country(affil)
                    if country:
                        country_list.append(country)
                        author_info += "(" + country +")"
                        if ('@' in affil):
                            country_final_list.append(country)
                            match_mail = re.search(r'[\w\.-]+@[\w\.-]+',
                                                   affil)
                            email = match_mail.group(0)
                            author_info += "Email:  " + email
            authors_info.append(author_info)
            count_line +=1

        country_list = list(set(country_list))
        country_final_list = list(set(country_final_list))
        # if all the author has the same country this is the country of the
        # article
        if (len(country_list) == 1):
            country_final_list = country_list
        try:
            self.data_analysis.loc[ind, 'first_author'] = authors_list[0]
        except IndexError:
            self.data_analysis.loc[ind, 'first_author'] = 'NoAuthor'
        self.data_analysis.loc[ind, 'authors'] = ', '.join(authors_list)
        self.data_analysis.loc[ind, 'authors_info'] = ', '.join(authors_info)
        self.data_analysis.loc[ind, 'country'] = ', '.join(country_final_list)
        return

    def read_year(self, ind, xml_data):
        for pubdate in xml_data.iter('PubDate'):
            for el in pubdate.iter():
                if (el.tag == 'Year'):
                    self.data_analysis.loc[ind, 'year'] = str(el.text)
                    return
                if (el.tag == 'MedlineDate'):
                    twodates = el.text.split('-')
                    year = twodates[0][:4]
                    self.data_analysis.loc[ind, 'year'] = str(year)
                    return

    def read_title(self, ind, xml_data):
        for tmp_title in xml_data.iter('ArticleTitle'):
            title = tmp_title.text
        try:
            self.data_analysis.loc[ind, 'title'] = title
        except UnboundLocalError:
            for tmp_title in xml_data.iter('BookTitle'):
                title = tmp_title.text
            self.data_analysis.loc[ind, 'title'] = title
        return

    def read_language(self, ind, xml_data):
        for tmp_language in xml_data.iter('Language'):
            language = tmp_language.text
        self.data_analysis.loc[ind, 'language'] = language
        return

    def read_journal(self, ind, xml_data):
        for jou in xml_data.iter('Title'):
            journal = jou.text
        try:
            self.data_analysis.loc[ind, 'journal'] = journal
        except UnboundLocalError:
            self.data_analysis.loc[ind, 'journal'] = ' '
        return

    def read_publication_type(self, ind, xml_data):
        pub_type = ''
        for el in xml_data.iter('PublicationType'):
            pub_type += el.text + '|'
        self.data_analysis.loc[ind, 'pub_type'] = pub_type
        return

    def read_keywords(self, ind, xml_data):

        key_major = []
        key_minor = []
        for keylist in xml_data.iter('KeywordList'):
            for el in keylist.iter():
                if(el.tag == 'Keyword'):
                    key = el.text
                    try:
                        if (el.attrib['MajorTopicYN'] == 'Y'):
                            key_major.append(key)
                        else:
                            key_minor.append(key)
                    except KeyError:
                        key_major.append(key)
        for keylist in xml_data.iter('Keyword'):
            for el in keylist.iter():
                if(el.tag == 'DescriptorName'):
                    key = el.text
                    try:
                        if (el.attrib['MajorTopicYN'] == 'Y'):
                            key_major.append(key)
                        else:
                            key_minor.append(key)
                    except KeyError:
                        key_major.append(key)
        for keylist in xml_data.iter('MeshHeading'):
            for el in keylist.iter():
                if(el.tag == 'DescriptorName'):
                    key = el.text
                    if (el.attrib['MajorTopicYN'] == 'Y'):
                        key_major.append(key)
                    else:
                        key_minor.append(key)

        self.data_analysis.loc[ind, 'keywords_major'] = ', '.join(key_major)
        self.data_analysis.loc[ind, 'keywords_minor'] = ', '.join(key_minor)
        return

    def write_abstract(self, article_id, xml_data):
        abstract_analysis = []
        for abstract_list in xml_data.iter('AbstractText'):
            for el in abstract_list.iter():
                if el.text == None:
                    continue
                abstract = el.text
                try:
                    label = el.attrib['Label']
                    abstract_analysis.append(label + ':')
                    abstract_analysis.append(abstract)
                except KeyError:
                    abstract_analysis.append(abstract)
                if el.tail != None:
                    abstract_analysis.append(el.tail)

        with open(self.abstract_dir+str(article_id)+'.txt', 'w') as f:
            for item in abstract_analysis:
                f.write("%s\n" % item)
        

    def find_country(self, string):
        for ind in self.country_dict.index:
            country = self.country_dict['List1'][ind]
            if (country in string):
                return self.country_dict['List2'][ind]
        return ''

    def save_data_analysis(self, filename):
        with pd.ExcelWriter(filename, mode='w') as writer:  
            self.data_analysis.to_excel(writer, index = False)

    # ~ def save_for_review(self, filename):
        # ~ df_review = self.data_analysis
        # ~ df_review = df_review.drop(columns=['keywords_major',
                                            # ~ 'keywords_minor',
                                            # ~ 'search_key', 
                                            # ~ 'journal',
                                            # ~ 'authors',
                                            # ~ 'authors_info'])
        # ~ df_review['Framework  (1= Y, 0= No)'] = ' '
        # ~ df_review['Framework chacterization: Who developed  it(e.g. patient '\
                  # ~ 'association, clinicians, pharma, other)'] = ' '
        # ~ df_review['Framework chacterization: Aspects covered (e.g. diagnosis,'\
                  # ~ ' care, management)'] = ' '
        # ~ df_review['Framework chacterization: Population age'] = ' '
        # ~ df_review['Framework chacterization: Target audience (e.g. family '\
                  # ~ 'caregivers, patients)'] = ' '
        # ~ df_review['Framework chacterization: Formats in which the guidelines'\
                  # ~ ' were made available (e.g. pdf, online, interactive'\
                  # ~ ' formats)'] = ' '
        # ~ df_review['Evalutation by a 3rd party (1= Yes; 0= No)'] = ' '
        # ~ df_review['Editorial independence'] = ' '
        # ~ df_review['Dissemination (e.g. social media, e-mailing, website,'\
                  # ~ ' post)'] = ' '
        # ~ df_review['Access (public, private)'] = ' '
        # ~ with pd.ExcelWriter(filename, mode='w') as writer:  
            # ~ df_review.to_excel(writer, index = False)

    def save_for_review(self, filename):
        df_review = self.data_analysis
        df_review['Disease(ORPHACODE)'] = ''
        df_review['Patient Journey Mapping(1= Y, 0= No)'] = ''
        df_review['Aim of the article'] = ''
        df_review['Article Structure'] = ''
        df_review['Journey characterization'] = ''
        df_review['Aspects covered (e.g. diagnosis, care, management)'] = ''
        df_review['Population age'] = ''
        df_review['Target audience (e.g. family caregivers, patients)'] = ''
        df_review['Journey Format ( e.g. Image (Brainstorming, Written format, interative image, video)'] = ''
        df_review['Dissemination (e.g. social media, e-mailing, website, post)'] = ''
        df_review = df_review[['id', 
                    'filename', 
                    'country', 
                    'Disease(ORPHACODE)', 
                    'title', 
                    'Patient Journey Mapping(1= Y, 0= No)', 
                    'Aim of the article',
                    'Article Structure',
                    'Journey characterization',
                    'Aspects covered (e.g. diagnosis, care, management)',
                    'Population age',
                    'Target audience (e.g. family caregivers, patients)',
                    'Journey Format ( e.g. Image (Brainstorming, Written format, interative image, video)',
                    'Dissemination (e.g. social media, e-mailing, website, post)'
                    ]]
        with pd.ExcelWriter(filename, mode='w') as writer:  
            df_review.to_excel(writer, index = False)

    def load_data_analysis(self, filename):
        try:
            df = pd.read_excel(filename)
            df = df.astype({'id': 'str'})
            df = df.astype({'year': 'str'})
            self.data_analysis = pd.concat([self.data_analysis, df]).drop_duplicates().reset_index(drop=True)
            
        except FileNotFoundError:
            print('nothing old to load, look for something new')

    def create_pdf(self, article_id, latex_dir):
        try: 
            ind = self.data_analysis.index[self.data_analysis['id'] ==
                                            article_id].tolist()
            ind = ind[0]
        except IndexError:
            ind = self.data_analysis.index[self.data_analysis['id'] ==
                                int(article_id)].tolist()
            ind = ind[0]
        filename = self.data_analysis['filename'][ind]
        if os.path.isfile(latex_dir + filename + '.pdf'):
            print("Pdf %s already exists" % (filename))
            return
        print("+"*10)
        print("Generating Pdf %s" % (filename))

        doc = Document()

        doc.preamble.append(Command('title',
                            self.data_analysis['title'][ind]))
        doc.preamble.append(Command('author',
                            self.data_analysis['authors'][ind]))
        doc.preamble.append(Command('date',
                            self.data_analysis['year'][ind]))
        doc.append(NoEscape(r'\maketitle'))
        doc.append(LargeText(bold('Abstract\n\n')))
        doc.append('\n')
        abstract = ''
        f = open(self.abstract_dir + article_id + '.txt')
        for line in f.readlines():
            abstract += self.adjust_abstract(line)
        f.close()
        doc.append(abstract)
        doc.append('\n\n\n\n')
        doc.append('Keywords Major Topic: \n')
        doc.append(self.data_analysis['keywords_major'][ind])
        doc.append('\nOther keywords: \n')
        doc.append(self.data_analysis['keywords_minor'][ind])
        print(abstract)
        try:
            doc.generate_pdf(latex_dir + filename)
        except:
            fd = open(latex_dir + filename + '.error','w')
            fd.write('Error creating pdf')
            fd.close()
        return

    def adjust_abstract(self, abstract):
        abstract = abstract.replace(u'U2009', '')
        abstract = abstract.replace(u'\u0391', 'Alpha')
        abstract = abstract.replace(u'\u0392', 'Beta')
        abstract = abstract.replace(u'\u0393', 'Gamma')
        abstract = abstract.replace(u'\u0394', 'Delta')
        abstract = abstract.replace(u'\u03B1', 'alpha')
        abstract = abstract.replace(u'\u03B2', 'beta')
        abstract = abstract.replace(u'\u03B3', 'gamma')
        abstract = abstract.replace(u'\u03B4', 'delta')
        abstract = abstract.replace(u'\u2265', '>=')
        abstract = abstract.replace(u'U+2264', '<=')
        abstract = abstract.replace(u'\u2005', ' ')
        abstract = abstract.replace(u'U+2009', ' ')
        return abstract


    def plot_years(self, img_name):
        articles_per_year = self.data_analysis['year'].value_counts()\
                           .sort_index()
        fig, ax = plt.subplots(figsize=(12, 5))
        sns.set(style='whitegrid')
        articles_per_year.plot(kind='bar', facecolor='#00b359', width=0.7)
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        ax.grid(axis='x', linestyle='dashed', alpha=0.5)
        plt.ylabel('')
        plt.xlabel('Year', size=12, color='#4f4e4e')
        plt.title('Number of articles per year', size=16, color='#4f4e4e',
                  fontweight='bold')
        plt.xticks(size=12, color='#4f4e4e')
        plt.yticks(size=12, color='#4f4e4e')
        sns.despine(left=True)
        plt.savefig(img_name, bbox_inches='tight')

        return

    def plot_countries(self, img_name, img_name_collab):
        countries = pd.DataFrame(columns=['Country', 'Collaboration'])
        self.data_analysis['country'] = self.data_analysis['country']\
                                      .str.rstrip().fillna('to find')

        # Create the list of countries
        for index, row in self.data_analysis.iterrows():
            country = self.data_analysis['country'][index]
            list_country = country.split(', ')
            if (len(list_country) == 1):
                countries = countries.append({'Country': list_country[0],
                                             'Collaboration': False},
                                             ignore_index=True)
            elif (len(list_country) > 1):
                for country in list_country:
                    countries = countries.append({'Country': country,
                                                 'Collaboration': True},
                                                 ignore_index=True)
            else:
                continue
        art_per_country = countries['Country'].value_counts()\
                                              .sort_values(ascending=True)
        # Plot articles per country ignoring collaborations
        fig, ax = plt.subplots(figsize=(12, 5))
        sns.set(style='whitegrid')
        art_per_country.plot(kind='barh', facecolor='#00b359', width=0.8)
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        ax.grid(axis='y', linestyle='dashed', alpha=0.5)
        plt.xlabel('Nbr. of pubblication', size=14, color='#4f4e4e')
        plt.title('Number of articles per country', size=16, color='#4f4e4e',
                  fontweight='bold')
        plt.xticks(size=12, color='#4f4e4e')
        plt.yticks(size=12, color='#4f4e4e')
        sns.despine(left=True)
        plt.savefig(img_name, bbox_inches='tight')

        fig.clf()
        # Emphasize the collaboration
        art_nocoll = countries['Country'][countries['Collaboration'] == False]\
                              .value_counts()
        art_nocoll = pd.DataFrame(art_nocoll)
        art_nocoll.columns = ['no_coll']
        art_nocoll['Country'] = art_nocoll.index

        art_coll = countries['Country'][countries['Collaboration']]\
                            .value_counts()
        art_coll = pd.DataFrame(art_coll)
        art_coll.columns = ['coll']
        art_coll['Country'] = art_coll.index

        art_per_country = pd.DataFrame(art_per_country)
        art_per_country.columns = ['tot']
        art_per_country['Country'] = art_per_country.index
        art_per_country = art_per_country.join(art_nocoll.set_index('Country'),
                                               on='Country').fillna(0)
        art_per_country = art_per_country.join(art_coll.set_index('Country'),
                                               on='Country').fillna(0)
        # the column tot has bees used for obtaining the dataframe ordered,
        # now can be removed
        art_per_country = art_per_country.drop(['Country', 'tot'], axis=1)
        ax = art_per_country.plot(kind='barh', stacked=True, width=0.8,
                             color={'no_coll': '#00b359', 'coll': '#00e673'},
                             figsize=(12, 5))
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        ax.grid(axis='y', linestyle='dashed', alpha=0.5)
        plt.ylabel('')
        plt.xlabel('Nbr. of pubblication', size=14, color='#4f4e4e')
        plt.title('Number of articles per country', size=16, color='#4f4e4e',
                  fontweight='bold')
        plt.xticks(size=12, color='#4f4e4e')
        plt.yticks(size=12, color='#4f4e4e')
        plt.legend(['Without collaboration', 'International Collaboration'],
                   fontsize=14)
        sns.despine(left=True)
        plt.savefig(img_name_collab, bbox_inches='tight')

        return

    def plot_wordclouds_countries(self, img_name):
        self.data_analysis['country'] = self.data_analysis['country'].fillna('to find')
        text = ' '.join(self.data_analysis['country'])
        fig, ax = plt.subplots(figsize=(12, 5))
        wordcloud = WordCloud(background_color="white").generate(text)

        # Display the generated image:
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis("off")
        plt.savefig(img_name, bbox_inches='tight')

        return


    def plot_pubkeys(self, img_name):
        list1 = self.data_analysis['keywords_major'].fillna('')
        list2 = self.data_analysis['keywords_minor'].fillna('')
        fin_list = list1 + list2
        text = ' '.join(fin_list)
        fig, ax = plt.subplots(figsize=(12, 5))
        wordcloud = WordCloud(background_color="white").generate(text)

        # Display the generated image:
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis("off")
        plt.savefig(img_name, bbox_inches='tight')

        return
