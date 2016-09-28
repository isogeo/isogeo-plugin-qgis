# -*- coding: utf-8 -*-

import datetime
import webbrowser
from urllib import quote
from PyQt4.QtCore import QUrl

class Tools(object):
    """Basic class that holds utilitary methods for the plugin."""

    def calcul_nb_page(self, nb_fiches):
        """Calculate the number of pages for a given number of results."""
        if nb_fiches <= 15:
            nb_page = 1
        else:
            if (nb_fiches % 15) == 0:
                nb_page = (nb_fiches / 15)
            else:
                nb_page = (nb_fiches / 15) + 1
        return nb_page

    def handle_date(self, input_date):
        """Create a date object with the string given as a date by the API."""
        date = input_date.split("T")[0]
        year = int(date.split('-')[0])
        month = int(date.split('-')[1])
        day = int(date.split('-')[2])
        new_date = datetime.date(year, month, day)
        return new_date.strftime("%Y-%m-%d")
        return new_date

    def open_webpage(self, link):
        """Open the bugtracker on the user's default browser."""
        if type(link) is QUrl:
            link = link.toString()

        webbrowser.open(
            link,
            new=0,
            autoraise=True)

    def get_tags(self, answer):
        """Return a tag dictionnary from the API answer.

        This parse the tags contained in API_answer[tags] and class them so
        they are more easy to handle in other function such as
        update_fields()
        """
        # Initiating the dicts
        tags = answer['tags']
        resources_types = {}
        owners = {}
        keywords = {}
        themeinspire = {}
        formats = {}
        srs = {}
        actions = {}
        # loops that sort each tag in the corresponding dict, keeping the
        # same "key : value" structure.
        for tag in tags.keys():
            # owners
            if tag.startswith('owner'):
                owners[tag] = tags[tag]
            # custom keywords
            elif tag.startswith('keyword:isogeo'):
                keywords[tag] = tags[tag]
            # INSPIRE themes
            elif tag.startswith('keyword:inspire-theme'):
                themeinspire[tag] = tags[tag]
            # formats
            elif tag.startswith('format'):
                formats[tag] = tags[tag]
            # coordinate systems
            elif tag.startswith('coordinate-system'):
                srs[tag] = tags[tag]
            # available actions (the last 2 are a bit specific as the value
            # field is empty and have to be filled manually)
            elif tag.startswith('action'):
                if tag.startswith('action:view'):
                    actions[tag] = u'View'
                elif tag.startswith('action:download'):
                    actions[tag] = u'Download'
                elif tag.startswith('action:other'):
                    actions[tag] = u'Other action'
                # Test : to be removed eventually
                else:
                    actions[tag] = u'fonction get_tag à revoir'
                    self.dockwidget.txt_input.setText(tag)
            # resources type
            elif tag.startswith('type'):
                if tag.startswith('type:vector'):
                    resources_types[tag] = u'Vecteur'
                elif tag.startswith('type:raster'):
                    resources_types[tag] = u'Raster'
                elif tag.startswith('type:resource'):
                    resources_types[tag] = u'Ressource'
                elif tag.startswith('type:service'):
                    resources_types[tag] = u'Service géographique'
        # Creating the final object the function will return : a dictionary
        # of dictionaries
        new_tags = {}
        new_tags['type'] = resources_types
        new_tags['owner'] = owners
        new_tags['keywords'] = keywords
        new_tags['themeinspire'] = themeinspire
        new_tags['formats'] = formats
        new_tags['srs'] = srs
        new_tags['actions'] = actions
        return new_tags

    def format_path(self, string):
        """Reformat windows path for them to be understood by QGIS."""
        new_string = ""
        for character in string:
            if character == '\\':
                new_string += "/"
            else:
                new_string += character
        return new_string

    def mail_to_isogeo(self, lang):
        """Preformat a mail asking for an Isogeo account."""
        if lang == "fr":
            webbrowser.open('http://www.isogeo.com/fr/Plugin-QGIS/22',
                            new=0,
                            autoraise=True
                            )
        else:
            webbrowser.open('http://www.isogeo.com/en/QGIS-Plugin/22',
                            new=0,
                            autoraise=True
                            )
