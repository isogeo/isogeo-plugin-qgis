import pkgutil
import sys

print(QGis.QGIS_VERSION)

# packages
packages = sorted( [x[1] for x in list(pkgutil.iter_modules())])
print("Available Python packages: {}".format(len(packages)))
# other way but not really pretty: help("modules")

#----------------------------------------------------------------
# packages and detailed modules
sysmods = sorted(sys.modules.keys())
print("\nAvailable Python packages and modules: {}".format(len(sysmods)))

# print all of them
#for module in sorted(sysmods.keys()):
#    print(module)

# test if some module is present
# print("owslib" in sysmods)
# print("requests" in sysmods)

#----------------------------------------------------------------
# 3rd party packages
print("\nAvailable Python 3rd party packages and their versions")
for dist in __import__('pkg_resources').working_set:
   print("- {}: {}".format(dist.project_name.replace('Python', ''),
                                      dist.version))