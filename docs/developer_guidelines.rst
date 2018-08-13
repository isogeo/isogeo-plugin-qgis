Dev documentation
=================


# UI

Qt is used (through PyQt) to build the graphical user interface ([see this VS Code extension for PyQt](https://github.com/mine2chow/PYQT-Integration)).
Qt Designer is useful to build the UI files.

## Widgets naming rules

To make development easier, widgets are prefixed with their class:

QpushButton = btn_
QComboBox = cbb_
QLineEdit = txt_
QLabel used for an icon = ico_
QLabel used for a text = lbl_
QTabWidget = tab_
QGridLayout (only when is really impacting) = lyt_
QTableWidget = tbl_
QGroupBox (only when it's really impacting) = grp_

## Resources (images...)

In Qt images are considered as resources which can be inserted/linked by QWidgets. That's the `resources.qrc`file which is used to link files and widgets.

### Source and prepare

Icons come from the Font Awesome project and more specifically from the svg/png converter: https://github.com/encharm/Font-Awesome-SVG-PNG.
Rules:

* icons are not renamed to keep the correspondance with Font Awesome
* SVG format is preferred to ensure graphical consistency and responsiveness
* SVG are prettified to gain some precious octets ([see this VS Code extension](https://github.com/lishu/vscode-svg))
* the same color is applied to the most of icons:

### Organization

Resources are stored in the `resources`subfolder and organized in subfolders corresponding to different UI files. Resources used in various UI files are stored at the root.


## Translations (i18n)

Qt handle translation for UI labels and strings in code.

## Compilation

UI and resources need to be compiled to Python. Commands are set in the `make.bat`file stored at the repository root.
