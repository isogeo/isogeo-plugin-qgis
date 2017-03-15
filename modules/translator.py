# -*- coding: UTF-8 -*-
#!/usr/bin/env python
from __future__ import (absolute_import, unicode_literals)
# ----------------------------------------------------------------------------

"""
Additionnal strings to be translated in the exports.
"""

# Created:      18/10/2016
# Updated:      22/11/2016
# ---------------------------------------------------------------------------

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
            "other": "Autre"
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
            "security": "Sécurité"
            },
        "conditions": {
            "license": "Licence :",
            "noLicense": "Pas de licence associée"
            },
        "constraintType": {
            "none": " ",
            "access": "Accès",
            "usage": "Usage"
            },
        "formatTypes": {
            "vectorDataset": "Vecteur",
            "vector-dataset": "Vecteur",
            "rasterDataset": "Raster",
            "raster-dataset": "Raster",
            "resource": "Ressources",
            "service": "Service géographique"
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
            "user": "Utilisateur"
            },
        "frequencyUpdateHelp": "Tous les ",
        "frequencyTypes": {
            "years": "an(s)",
            "months": "mois",
            "weeks": "semaine(s)",
            "days": "jour(s)",
            "hours": "heure(s)",
            "minutes": "minute(s)",
            "seconds": "seconde(s)"
            },
        "events": {
            "update": "Mise à jour",
            "creation": "Création",
            "published": "Publication"
            },
        "quality": {
            "specification": "Spécification",
            "conformant": "Conformité",
            "isConform": "Conforme",
            "isNotConform": "Non conforme",
            "topologicalConsistency": "Cohérence topologique"
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
            "other": "Other"
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
            "security": "Security"
            },
        "conditions": {
            "license": "License:",
            "noLicense": "No attached license"
            },
        "constraintType": {
            "none": " ",
            "access": "Access",
            "usage": "Usage"
            },
        "formatTypes": {
            "vectorDataset": "Vector",
            "vector-dataset": "Vector",
            "rasterDataset": "Raster",
            "raster-dataset": "Raster",
            "resource": "Resources",
            "series": "Series",
            "service": "Service"
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
            "user": "User"
            },
        "frequencyUpdateHelp": "Every ",
        "frequencyTypes": {
            "years": "year(s)",
            "months": "month(s)",
            "weeks": "week(s)",
            "days": "day(s)",
            "hours": "hour(s)",
            "minutes": "minute(s)",
            "seconds": "second(s)"
            },
        "events": {
            "update": "Update",
            "creation": "Creation",
            "published": "Publication"
            },
        "quality": {
            "specification": "Specification",
            "conformant": "Conformity",
            "isConform": "Conformant",
            "isNotConform": "Not conformant",
            "topologicalConsistency": "Topological consistency"
            },
}

# ##############################################################################
# ########## Classes ###############
# ##################################


class IsogeoTranslator(object):
    """Makes easier the translation of Isogeo API specific strings."""

    def __init__(self, lang="FR"):
        """Set text dictionary depending on language passed."""
        if lang.upper() == "FR":
            self.translations = dict_md_fields_fr
        else:
            self.translations = dict_md_fields_en

        super(IsogeoTranslator, self).__init__()

    def tr(self, subdomain=None, string_to_translate=""):
        """Returns translation of string passed."""
        if subdomain:
            str_translated = self.translations.get(subdomain, {"error": "Subdomain not found: {}".format(subdomain)})\
                                              .get(string_to_translate, "String not found")
        else:
            str_translated = self.translations.get(string_to_translate, "String not found")
        # end of method
        return str_translated

# ##############################################################################
# ##### Stand alone program ########
# ##################################

if __name__ == '__main__':
    """Standalone execution."""
    # French
    translator_fr = IsogeoTranslator("FR")
    print(translator_fr.tr("roles", "pointOfContact"))

    # English
    translator_en = IsogeoTranslator("EN")
    print(translator_en.tr("roles", "pointOfContact"))
    # print(dict_md_fields_fr.get("roles"))
    # print(dict_md_fields_fr.get("frequencyTypes"))
