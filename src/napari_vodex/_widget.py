"""
This module is an example of a barebones QWidget plugin for napari

For Widget specification see: https://napari.org/stable/plugins/guides.html?#widgets

"""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import napari

# imports info: https://napari.org/stable/plugins/best_practices.html :
# Don’t import from PyQt5 or PySide2 in your plugin: use qtpy. If you use from PyQt5 import QtCore (or similar) in
# your plugin, but the end-user has chosen to use PySide2 for their Qt backend — or vice versa — then your plugin
# will fail to import. Instead use from qtpy import   QtCore. qtpy is a Qt compatibility layer that will import from
# whatever backend is installed in the environment.


from qtpy.QtWidgets import QApplication

import napari

from ._model import VodexModel
from ._controller import VodexController
from ._view import VodexView


class VodexWidget(VodexView):
    # your QWidget.__init__ can optionally request the napari viewer instance
    # in one of two ways:
    # 1. use a parameter called `napari_viewer`
    # 2. use a type annotation of 'napari.viewer.Viewer' for any parameter

    def __init__(self, viewer: 'napari.viewer.Viewer' = None):
        super().__init__(viewer)

        self._model = VodexModel()
        self._controller = VodexController(model=self._model, view=self)


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    window = VodexWidget()
    window.show()
    sys.exit(app.exec_())
