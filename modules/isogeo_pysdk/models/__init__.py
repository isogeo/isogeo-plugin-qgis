# coding: utf-8
#! python3  # noqa: E265

# models which are imported in a specific order handling their inter-dependencies
from .contact import Contact  # noqa: F401
from .workgroup import Workgroup  # noqa: F401

from .application import Application  # noqa: F401
from .catalog import Catalog  # noqa: F401

from .coordinates_system import CoordinateSystem  # noqa: F401
from .event import Event  # noqa: F401
from .format import Format  # noqa: F401
from .datasource import Datasource  # noqa: F401
from .directive import Directive  # noqa: F401
from .feature_attributes import FeatureAttribute  # noqa: F401
from .keyword import Keyword  # noqa: F401
from .keyword_search import KeywordSearch  # noqa: F401
from .invitation import Invitation  # noqa: F401
from .license import License  # noqa: F401
from .limitation import Limitation  # noqa: F401
from .link import Link  # noqa: F401
from .metadata import Metadata  # noqa: F401
from .metadata_search import MetadataSearch  # noqa: F401
from .share import Share  # noqa: F401
from .service_layer import ServiceLayer  # noqa: F401
from .service_operation import ServiceOperation  # noqa: F401
from .specification import Specification  # noqa: F401
from .thesaurus import Thesaurus  # noqa: F401
from .user import User  # noqa: F401

# depending on License model
from .condition import Condition  # noqa: F401

# depending on Specification model
from .conformity import Conformity  # noqa: F401

# depending on previous models
from .bulk_request import BulkRequest  # noqa: F401
from .bulk_report import BulkReport  # noqa: F401

# shortcuts or confusion reducers
Account = User
Group = Workgroup
Resource = Metadata
ResourceSearch = MetadataSearch
