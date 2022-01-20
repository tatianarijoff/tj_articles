import pandas as pd
import numpy as np
import itertools
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import seaborn as sns

max_key_cols = 6


class Keywords(object):
    '''The Keywords object extracts the keywords from a file
       and convert in a list of dictionary with keywords groups'''
    def __init__(self):
        self.key_search = pd.DataFrame(columns=['Keywords', 'articles',
                                                'nbr_articles'])
        self.articles_found = pd.DataFrame(columns=['id_article', 'key'])
        self.key_nbr = 0
        self.grp_colname = []
        return

    def find_keys_from_excel(self, excel_file, sheet):
        '''This function allows to load keywords from excel when there are not
           groups defined, so that every column identifies a keywords list'''
        df = pd.read_excel(excel_file, sheet_name=sheet)
        df = df.replace(np.nan, '__', regex=True)
        index = 0
        col = df.columns[index]
        count_words = df[col].str.count(' ')
        df[col].loc[(count_words > 0)] = '"' +  \
            df[col].loc[(count_words > 0)] +  '"'
        combi = df[col]

        for index in range(1, len(df.columns)):
            col = df.columns[index]
            count_words = df[col].str.count(' ')
            df[col].loc[(count_words > 0)] = '"' +  \
                df[col].loc[(count_words > 0)] +  '"'
            combi = list(map(' AND '.join, itertools.product(combi, df[col])))
            combi = [item for item in combi if item.find('__') < 0]
            for el in combi:
                data = pd.DataFrame([el], columns=['Keywords'])
                self.key_search = df.concat([self.key_search, data]).drop_duplicates().reset_index(drop=True)
        self.key_nbr = self.key_search['Keywords'].count()
        return


    def find_keys_from_excel_mod2(self, excel_file, sheet):
        '''This function allows to load keywords from excel when there are not
           groups defined, so that every column identifies a keywords list
           this mod2 function not use the quote around the columns from
           the second one, this means that pubmed will consider the 
           keywords as words with AND'''
        df = pd.read_excel(excel_file, sheet_name=sheet)
        df = df.replace(np.nan, '__', regex=True)
        index = 0
        col = df.columns[index]
        count_words = df[col].str.count(' ')
        df[col].loc[(count_words > 0)] = '"' +  \
            df[col].loc[(count_words > 0)] +  '"'
        combi = df[col]

        for index in range(1, len(df.columns)):
            col = df.columns[index]
            count_words = df[col].str.count(' ')
            combi = list(map(' AND '.join, itertools.product(combi, df[col])))
            combi = [item for item in combi if item.find('__') < 0]
            for el in combi:
                data = pd.DataFrame([el], columns=['Keywords'])
                self.key_search = self.key_search.append(data,
                                                         ignore_index=True)
        self.key_nbr = self.key_search['Keywords'].count()
        return

    def find_keys_from_excel_mod3(self, excel_file, sheet):
        '''This function allows to load keywords from excel when there are not
           groups defined, so that every column identifies a keywords list
           this mod3 function not use the quote, this means that pubmed
           will consider the keywords as words with AND'''
        df = pd.read_excel(excel_file, sheet_name=sheet)
        df = df.replace(np.nan, '__', regex=True)
        index = 0
        col = df.columns[index]
        count_words = df[col].str.count(' ')
        combi = df[col]

        for index in range(1, len(df.columns)):
            col = df.columns[index]
            count_words = df[col].str.count(' ')
            combi = list(map(' AND '.join, itertools.product(combi, df[col])))
            combi = [item for item in combi if item.find('__') < 0]
            for el in combi:
                data = pd.DataFrame([el], columns=['Keywords'])
                self.key_search = self.key_search.append(data,
                                                          ignore_index=True)
        self.key_nbr = self.key_search['Keywords'].count()
        return

    def save_keywords_list(self, filename):
        with pd.ExcelWriter(filename, mode='w') as writer:  
            self.key_search.to_excel(writer, columns=['Keywords'], 
                            index = False)

    def load_keywords_list(self, filename):
        try:
            df = pd.read_excel(filename)
            df['articles'] = ''
            df['nbr_articles'] = '' 
            self.key_search = self.key_search.append(df, ignore_index=True)
        except FileNotFoundError:
            print('Nothing old to load, go for the new')
        return

    def articles_found_add(self, myid, mykey):
        tmp_dic = {'id_article': str(myid), 'key': mykey}
        ind = self.key_search[self.key_search['Keywords'] == mykey]\
                  .index.tolist()
        self.articles_found = self.articles_found.append(tmp_dic,
                                                         ignore_index=True)
        return

    def find_keys_str(self, article_id):
        key_list = self.articles_found[self.articles_found['id_article'] ==
                                       article_id]['key'].values
        key_string = '; '.join(key_list)
        return key_string

    def save_keywords(self, filename):
        with pd.ExcelWriter(filename, mode='w') as writer:  
            self.key_search.to_excel(writer, index = False)

    def save_articles(self, filename):
        with pd.ExcelWriter(filename, mode='w') as writer:  
            self.articles_found.to_excel(writer, index = False)

    def load_keywords(self, filename):
        df = pd.read_excel(filename)
        self.key_search = self.key_search.append(df, ignore_index=True)
        return

    def load_articles(self, filename):
        try:
            df = pd.read_excel(filename)
            self.articles_found = self.articles_found.append(df, ignore_index=True)
        except FileNotFoundError:
            print('Nothing old to load, go for the new')
        return
