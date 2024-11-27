# -*- coding: UTF-8 -*-
#! python3  # noqa E265

"""Additionnal strings to be translated from Isogeo API."""

# ##############################################################################
# ########## Globals ###############
# ##################################

dict_md_fields_fr = {
    "restrictions": {
        "none": " ",
        "copyright": "Copyright",
        "patent": "Brevet",
        "patentPending": "Brevet en attente",
        "trademark": "Marque déposée",
        "license": "Licence",
        "intellectualPropertyRights": "Droits de propriété intellectuelle",
        "restricted": "Limité",
        "other": "Autre",
    },
    "limitations": {
        "title": "Limitations",
        "add": "Ajouter une nouvelle limitation",
        "edit": "Editer la limitation",
        "restriction": "Restriction :",
        "description": "Description :",
        "type": "Type :",
        "directive": "Directive :",
        "legal": "Légale",
        "security": "Sécurité",
    },
    "conditions": {"license": "Licence :", "noLicense": "Pas de licence associée"},
    "constraintType": {"none": " ", "access": "Accès", "usage": "Usage"},
    "formatTypes": {
        "dataset": "Jeux de données",
        "vectorDataset": "Vecteur",
        "vector-dataset": "Vecteur",
        "noGeoDataset": "Donnée (tabulaire non géographique)",
        "no-geo-dataset": "Donnée (tabulaire non géographique)",
        "rasterDataset": "Raster",
        "raster-dataset": "Raster",
        "resource": "Ressources",
        "series": "Ensemble de données",
        "service": "Service géographique",
    },
    "roles": {
        "author": "Auteur",
        "pointOfContact": "Point de contact",
        "custodian": "Administrateur",
        "distributor": "Distributeur",
        "originator": "Créateur",
        "owner": "Propriétaire",
        "principalInvestigator": "Analyste principal",
        "processor": "Responsable du traitement",
        "publisher": "Éditeur (publication)",
        "resourceProvider": "Fournisseur",
        "user": "Utilisateur",
    },
    "frequencyTypes": {
        "frequencyUpdateHelp": "Tous les ",
        "years": "an(s)",
        "months": "mois",
        "weeks": "semaine(s)",
        "days": "jour(s)",
        "hours": "heure(s)",
        "minutes": "minute(s)",
        "seconds": "seconde(s)",
    },
    "frequencyShortTypes": {
        "Y": "an(s)",
        "M": "mois",
        "W": "semaine(s)",
        "D": "jour(s)",
        "H": "heure(s)",
        "m": "minute(s)",
        "S": "seconde(s)",
    },
    "events": {
        "update": "Mise à jour",
        "creation": "Création",
        "published": "Publication",
    },
    "quality": {
        "specification": "Spécification",
        "conformant": "Conformité",
        "isConform": "Conforme",
        "isNotConform": "Non conforme",
        "topologicalConsistency": "Cohérence topologique",
    },
}

dict_md_fields_en = {
    "restrictions": {
        "none": " ",
        "copyright": "Copyright",
        "patent": "Patent",
        "patentPending": "Patent pending",
        "trademark": "Trademark",
        "license": "License",
        "intellectualPropertyRights": "Intellectual property rights",
        "restricted": "Restricted",
        "other": "Other",
    },
    "limitations": {
        "title": "Limitations",
        "add": "Add new limitation",
        "edit": "Edit limitation",
        "restriction": "Restriction:",
        "description": "Description:",
        "type": "Type:",
        "directive": "Directive:",
        "legal": "Legal",
        "security": "Security",
    },
    "conditions": {"license": "License:", "noLicense": "No attached license"},
    "constraintType": {"none": " ", "access": "Access", "usage": "Usage"},
    "formatTypes": {
        "dataset": "Dataset",
        "vectorDataset": "Vector",
        "vector-dataset": "Vector",
        "noGeoDataset": "Dataset (non-geographic tabular)",
        "no-geo-dataset": "Dataset (non-geographic tabular)",
        "rasterDataset": "Raster",
        "raster-dataset": "Raster",
        "resource": "Resources",
        "series": "Series",
        "service": "Service",
    },
    "roles": {
        "author": "Author",
        "pointOfContact": "Point of contact",
        "custodian": "Custodian",
        "distributor": "Distributor",
        "originator": "Originator",
        "owner": "Owner",
        "principalInvestigator": "Principal investigator",
        "processor": "Processor",
        "publisher": "Publisher",
        "resourceProvider": "Resource provider",
        "user": "User",
    },
    "frequencyTypes": {
        "frequencyUpdateHelp": "Every ",
        "years": "year(s)",
        "months": "month(s)",
        "weeks": "week(s)",
        "days": "day(s)",
        "hours": "hour(s)",
        "minutes": "minute(s)",
        "seconds": "second(s)",
    },
    "frequencyShortTypes": {
        "Y": "year(s)",
        "M": "month(s)",
        "W": "week(s)",
        "D": "day(s)",
        "H": "hour(s)",
        "m": "minute(s)",
        "S": "second(s)",
    },
    "events": {"update": "Update", "creation": "Creation", "published": "Publication"},
    "quality": {
        "specification": "Specification",
        "conformant": "Conformity",
        "isConform": "Conformant",
        "isNotConform": "Not conformant",
        "topologicalConsistency": "Topological consistency",
    },
}

# ##############################################################################
# ########## Classes ###############
# ##################################


class IsogeoTranslator(object):
    """Makes easier the translation of Isogeo API specific strings.

    :param str lang: language code to apply. EN or FR.
    """

    def __init__(self, lang: str = "FR"):
        """Instantiate IsogeoTranslator depending on required language.

        :param str lang: language code to apply. EN or FR.
        """
        if lang.upper() == "FR":
            self.translations = dict_md_fields_fr
        else:
            self.translations = dict_md_fields_en

        super(IsogeoTranslator, self).__init__()

    def tr(self, subdomain: str, string_to_translate: str = "") -> str:
        """Returns translation of string passed.

        :param str subdomain: subpart of strings dictionary.
         Must be one of self.translations.keys() i.e. 'restrictions'
        :param str string_to_translate: string you want to translate
        """
        if subdomain not in self.translations.keys():
            raise ValueError(
                "'{}' is not a correct subdomain."
                " Must be one of {}".format(subdomain, self.translations.keys())
            )
        else:
            pass
        # translate
        str_translated = self.translations.get(
            subdomain, {"error": "Subdomain not found: {}".format(subdomain)}
        ).get(string_to_translate, "String not found")

        # end of method
        return str_translated


# ##############################################################################
# ##### Stand alone program ########
# ##################################
if __name__ == "__main__":
    """Standalone execution."""
    # French
    translator_fr = IsogeoTranslator("FR")
    print(translator_fr.tr("roles", "pointOfContact"))

    # English
    translator_en = IsogeoTranslator("EN")
    print(translator_en.tr("roles", "pointOfContact"))
    # print(dict_md_fields_fr.get("roles"))
    # print(dict_md_fields_fr.get("frequencyTypes"))
