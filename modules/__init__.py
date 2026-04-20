from pathlib import Path

# Logger name based on plugin directory — must be defined BEFORE submodule imports
# so that submodules can do `from . import PLG_LOGGER_NAME` during their loading
PLG_LOGGER_NAME = "IsogeoQgisPlugin.{}".format(Path(__file__).parent.parent.name)

from .api import Authenticator, ApiRequester, SharesParser
from .metadata_display import MetadataDisplayer
from .results import ResultsManager, CacheManager
from .tools import IsogeoPlgTools
from .quick_search import QuickSearchManager
from .search_form import SearchFormManager
from .user_inform import UserInformer
from .settings_manager import SettingsManager
