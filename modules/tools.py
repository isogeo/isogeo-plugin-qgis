# -*- coding: utf-8 -*-

import datetime
import webbrowser
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

    def format_button_title(self, title):
        """Format the title for it to fit the button."""
        words = title.split(' ')
        line_length = 0
        lines = []
        string = ""
        for word in words:
            line_length += len(word)
            if line_length < 22:
                string += word + " "
            else:
                line_length = len(word)
                lines.append(string[:-1])
                string = word + " "
        if string[:-1] not in lines:
            lines.append(string[:-1])
        final_text = ""
        for line in lines:
            final_text += line + "\n"
        final_text = final_text[:-1]
        return final_text

    def build_request_url(self, params):
        """Build the request url according to the widgets."""
        # Base url for a request to Isogeo API
        url = 'https://v1.api.isogeo.com/resources/search?'
        # Build the url according to the params
        filters = ""
        # Owner
        if params.get('owner') is not None:
            filters += params.get('owner') + " "
        # INSPIRE keywords
        if params.get('inspire') is not None:
            filters += params.get('inspire') + " "
        # Format
        if params.get('format') is not None:
            filters += params.get('format') + " "
        # Data type
        if params.get('datatype') is not None:
            filters += params.get('datatype') + " "
        # Action : view
        if params.get("view"):
            filters += "action:view "
        # Action : download
        if params.get("download"):
            filters += "action:download "
        # Action : Other
        if params.get("other"):
            filters += "action:other "
        # No actions
        if params.get("noaction"):
            filters += "has-no:action "
        # Keywords
        for keyword in params["keys"]:
            filters += keyword + " "
        # Formating the filters
        if filters != "":
            filters = "q={0}".format(filters[:-1])
        # Geographical filter
        if params.get("geofilter") is not None:
            if params.get("coord") is not False:
                filters += "&box={0}&rel={1}".format(params.get("coord"),
                                                     params.get("operation"))
            else:
                pass
        else:
            pass
        # Sorting order and direction
        if params.get("show"):
            filters += "&ob={0}&od={1}".format(params.get("ob"),
                                               params.get("od"))
            filters += "&_include=links,serviceLayers,layers"
            limit = 15
        else:
            limit = 0
        # Limit and offset
        offset = (params.get("page") - 1) * 15
        filters += "&_limit={0}&_offset={1}".format(limit, offset)
        # Language
        "&_lang={0}".format(params.get("lang"))
        # BUILDING FINAL URL
        url += filters
        return url

    def build_wfs_url(self, raw_url):
        """Reformat the input WFS url so it fits QGIS criterias.

        Tests weither all the needed information is provided in the url, and
        then build the url in the syntax understood by QGIS.
        """
        title = raw_url[0]
        input_url = raw_url[1].split("?")[0] + "?"
        try:
            list_parameters = raw_url[1].split("?")[1].split('&')
        except IndexError:
            return 0
        valid = False
        srs_defined = False
        for i in list_parameters:
            ilow = i.lower()
            if "typename=" in ilow:
                valid = True
                name = i.split('=')[1]
                typename = i
            elif "layers=" in ilow or "layer=" in ilow:
                valid = True
                name = i.split('=')[1]
                typename = "typename=" + name
            elif "getcapabilities" in ilow:
                valid = True
                name = title
                typename = "typename=" + name
            elif "srsname=" in ilow:
                srs_defined = True
                srs = i

        if valid is True:
            output_url = input_url + typename

            if srs_defined is True:
                output_url += '&' + srs

            output_url += '&service=WFS&version=1.0.0&request=GetFeature'

            output = ["WFS", name, output_url]
            return output

        else:
            return 0

    def build_wms_url(self, raw_url):
        """Reformat the input WMS url so it fits QGIS criterias.

        Tests weither all the needed information is provided in the url, and
        then build the url in the syntax understood by QGIS.
        """
        title = raw_url[0]
        input_url = raw_url[1].split("?")[0] + "?"
        try:
            list_parameters = raw_url[1].split("?")[1].split('&')
        except IndexError:
            return 0
        valid = False
        style_defined = False
        srs_defined = False
        format_defined = False
        for i in list_parameters:
            ilow = i.lower()
            if "layers=" in ilow:
                valid = True
                name = i.split('=')[1]
                layers = i
            elif "layer=" in ilow:
                valid = True
                name = i.split('=')[1]
                layers = "layers=" + name
            elif "getcapabilities" in ilow:
                valid = True
                name = title
                layers = "layers=" + title
            elif "styles=" in ilow:
                style_defined = True
                style = i
            elif "crs=" in ilow:
                srs_defined = True
                srs = i
            elif "format=" in ilow:
                format_defined = True
                imgformat = i

        if valid is True:
            if input_url.lower().startswith('url='):
                output_url = input_url + "&" + layers
            else:
                output_url = "url=" + input_url + "&" + layers

            if style_defined is True:
                output_url += '&' + style
            else:
                output_url += '&styles='

            if format_defined is True:
                output_url += '&' + imgformat
            else:
                output_url += '&format=image/png'

            if srs_defined is True:
                output_url += '&' + srs
            output = ["WMS", name, output_url]
            return output

        else:
            return 0

    def build_postgis_dict(self, input_dict):
        """Build the dict that stores informations about PostGIS connexions."""
        final_dict = {}
        for k in sorted(input_dict.allKeys()):
            if k.startswith("PostgreSQL/connections/")\
                    and k.endswith("/database"):
                if len(k.split("/")) == 4:
                    connection_name = k.split("/")[2]
                    password_saved = input_dict.value(
                        'PostgreSQL/connections/' +
                        connection_name +
                        '/savePassword')
                    user_saved = input_dict.value(
                        'PostgreSQL/connections/' +
                        connection_name +
                        '/saveUsername')
                    if password_saved == 'true' and user_saved == 'true':
                        dictionary = {'name':
                                      input_dict.value(
                                          'PostgreSQL/connections/' +
                                          connection_name +
                                          '/database'),
                                      'host':
                                      input_dict.value(
                                          'PostgreSQL/connections/' +
                                          connection_name +
                                          '/host'),
                                      'port':
                                      input_dict.value(
                                          'PostgreSQL/connections/' +
                                          connection_name +
                                          '/port'),
                                      'username':
                                      input_dict.value(
                                          'PostgreSQL/connections/' +
                                          connection_name +
                                          '/username'),
                                      'password':
                                      input_dict.value(
                                          'PostgreSQL/connections/' +
                                          connection_name +
                                          '/password')}
                        final_dict[
                            input_dict.value('PostgreSQL/connections/' +
                                             connection_name +
                                             '/database')
                        ] = dictionary
                    else:
                        continue
                else:
                    pass
            else:
                pass
        return final_dict
