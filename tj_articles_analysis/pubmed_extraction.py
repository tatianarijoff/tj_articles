import pandas as pd
import os
import numpy as np
from Bio import Entrez, Medline
import xml.etree.ElementTree as ET


class PubMedExtraction(object):
    '''The PubMedExtraction object finds the pubmed info based on
       keywords lists. It generates a DataFrame with all the useful
       information for article analysis'''
    def __init__(self):
        Entrez.email = "tatiana.rijoff@gmail.com"
        self.idlist = []
        return

    def load_pubmed_from_key(self, keywords):
        '''The find_id function finds the pubmed id based on
           keywords lists. The used keys are saved in an output excel '''
        idlist = []
        for ind, row in keywords.key_search.iterrows():
            mykey = keywords.key_search['Keywords'][ind]
            handle = Entrez.esearch(db='pubmed', term=mykey,
                                    sort='relevance',
                                    retmax=1000,
                                    usehistory="n")
            record = Entrez.read(handle)
            handle.close()
            print('Articles found with %s: %s' % (mykey,
                                                  record['Count']))
            keywords.key_search.loc[ind, 'articles'] = ', '\
                .join(record['IdList'])
            nbr = len(record['IdList'])
            keywords.key_search.loc[ind, 'nbr_articles'] = nbr
            idlist.extend(record["IdList"])
            for myid in record['IdList']:
                keywords.articles_found_add(myid, mykey)
        idlist = list(set(idlist))
        idlist = map(str, idlist) 
        self.idlist.extend(idlist)
        return

    def save_pubmed_idlist(self, filename):
        print(filename)
        with open(filename, 'w') as f:
            for item in self.idlist:
                f.write("%s\n" % item)

    def load_pubmed_idlist(self, filename):
        if os.path.isfile(filename):
            f = open(filename)
            for line in f.readlines():
                self.idlist.append(line.strip())
            f.close()
        else:
            print('No old data to load')
        return

    def find_info_xml(self, xml_dir):
        '''The find_xml function finds the pubmed info based on the id.
           and return the data in the xml format '''
        for article_id in self.idlist:
            if os.path.isfile(xml_dir + str(article_id) + '.xml'):
                print(f'Data for {article_id} already collected')
            else:
                print(f'Collecting Pubmed data for {article_id}')
                fetch_handle = Entrez.efetch(db='pubmed', rettype='medline',
                                             id=article_id, retmode="xml")
                xml_data = fetch_handle.read()
                fetch_handle.close()
                f = open(xml_dir + str(article_id) + '.xml', "wb")
                f.write(xml_data)
                f.close()
        return


    def find_info_xml_single(self, xml_dir, article_id):
        print(f'Collecting data for {article_id}')
        fetch_handle = Entrez.efetch(db='pubmed', rettype='medline',
                                     id=article_id, retmode="xml")
        xml_data = fetch_handle.read()
        fetch_handle.close()
        f = open(xml_dir + article_id + '.xml', "wb")
        f.write(xml_data)
        f.close()
        return
