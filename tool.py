import pandas as pd
import numpy as np
import re
import math
class YTlinkconverter:
    def __init__(self, link):
        self.link = link
    def convert_YT_link(self,link):
        """
        Convert a YouTube link by replacing special characters to make it usable as part of a file name.

        Args:
        link (str): The YouTube link to be converted.

        Returns:
        str: The converted link usable as part of a file name.
        """
        link = link.replace('/', '-')
        # link = link.replace(':','-')
        link = link.replace('?', '_')
        link = link.replace('=', ',')
        return link
    def convert_original_YT_link (self, link):
        """
        Convert a previously modified YouTube link back to its original format.

        Args:
        link (str): The modified YouTube link.

        Returns:
        str: The original YouTube link after conversion.
        """
        link = link.replace('-','/')
        # link = link.replace(':','-')
        link = link.replace('_', '?')
        link = link.replace(',', '=')
        return link

    def obtain_link_from_file (self, link):
        """
        Extract the YouTube link from a file name.

        Args:
        filename (str): The file name containing the YouTube link.

        Returns:
        str: The YouTube link extracted from the file name.
        """
        link = link.replace('-dataframe-','')
        link = self.convert_original_YT_link(link)
        return link


link = 'https://www.youtube.com/watch?v=O7MVN2Az7G0'

cv = YTlinkconverter(link)

l = cv.convert_YT_link(link)
print(l)
print(cv.convert_original_YT_link(l))


class StratifiedSampling:
    

    def sampler(self,total, group):

        """

        It takes as input the total number of elements and the number of groups.
        It returns a list of indices corresponding to the central positions of each group in the original DataFrame.

        Args:
        total (int): The total of element to sample.

        group (int): The number of group to divide the total.

        Returns:
        list: The list with the position of the element.
        """

        lunghezza = len(total)

        distanza= lunghezza / group
        distanza = math.ceil(distanza)

        in_mezzo = (distanza / 2)
        

        posizione =0
        list_finale =[]
        for i in range(group):
            posizione = posizione + (distanza-int(in_mezzo))
            if 0 < posizione < lunghezza:
                list_finale.append(total[posizione])

        return list_finale
    

    def is_youtube_channel_url(self,url):
        """
        Verifica se l'URL specificato è un link a un canale YouTube.

        Args:
            url: L'URL da verificare.

        Returns:
            True se l'URL è un link a un canale YouTube, False altrimenti.
        """
        # Espressione regolare per i canali YouTube
        regex = r"https?://(?:www\.)?youtube\.com/(?:@)?[a-zA-Z0-9-_]+(?:/featured)?"
        
        match = re.match(regex, url)
        return bool(match)
