# imports info: https://napari.org/stable/plugins/best_practices.html :
# Don’t import from PyQt5 or PySide2 in your plugin: use qtpy. If you use from PyQt5 import QtCore (or similar) in
# your plugin, but the end-user has chosen to use PySide2 for their Qt backend — or vice versa — then your plugin
# will fail to import. Instead use from qtpy import   QtCore. qtpy is a Qt compatibility layer that will import from
# whatever backend is installed in the environment.

import sys
# swap PyQt5 to qtpy before publishing
from PyQt5.QtWidgets import (
    QApplication,
    QComboBox,
    QScrollArea,
    QSizePolicy,
    QFrame,
    QToolButton,
    QCheckBox,
    QTabWidget,
    QFormLayout,
    QLineEdit,
    QStackedLayout,
    QVBoxLayout,
    QWidget,
)
# _______________________________________________________________________________
# Collapsable implementation from https://stackoverflow.com/questions/52615115/how-to-create-collapsible-box-in-pyqt

from PyQt5 import QtCore


class CollapsibleBox(QWidget):
    def __init__(self, title=""):
        super().__init__()

        self.toggle_button = QToolButton(text=title, checkable=True, checked=False)
        self.toggle_button.setStyleSheet("QToolButton { border: none; }")
        self.toggle_button.setToolButtonStyle(
            QtCore.Qt.ToolButtonTextBesideIcon
        )
        self.toggle_button.setArrowType(QtCore.Qt.RightArrow)
        self.toggle_button.pressed.connect(self.on_pressed)

        self.toggle_animation = QtCore.QParallelAnimationGroup(self)

        self.content_area = QScrollArea(maximumHeight=0, minimumHeight=0)
        self.content_area.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.content_area.setFrameShape(QFrame.NoFrame)

        lay = QVBoxLayout(self)
        lay.setSpacing(0)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self.toggle_button)
        lay.addWidget(self.content_area)

        self.toggle_animation.addAnimation(
            QtCore.QPropertyAnimation(self, b"minimumHeight")
        )
        self.toggle_animation.addAnimation(
            QtCore.QPropertyAnimation(self, b"maximumHeight")
        )
        self.toggle_animation.addAnimation(
            QtCore.QPropertyAnimation(self.content_area, b"maximumHeight")
        )

    @QtCore.pyqtSlot()
    def on_pressed(self):
        checked = self.toggle_button.isChecked()
        self.toggle_button.setArrowType(
            QtCore.Qt.DownArrow if not checked else QtCore.Qt.RightArrow
        )
        self.toggle_animation.setDirection(
            QtCore.QAbstractAnimation.Forward
            if not checked
            else QtCore.QAbstractAnimation.Backward
        )
        self.toggle_animation.start()

    def setContentLayout(self, layout):
        lay = self.content_area.layout()
        del lay
        self.content_area.setLayout(layout)
        collapsed_height = (
                self.sizeHint().height() - self.content_area.maximumHeight()
        )
        content_height = layout.sizeHint().height()
        duration = 5

        for i in range(self.toggle_animation.animationCount()):
            animation = self.toggle_animation.animationAt(i)
            animation.setDuration(duration)
            animation.setStartValue(collapsed_height)
            animation.setEndValue(collapsed_height + content_height)

        content_animation = self.toggle_animation.animationAt(
            self.toggle_animation.animationCount() - 1
        )
        content_animation.setDuration(duration)
        content_animation.setStartValue(0)
        content_animation.setEndValue(content_height)


# _______________________________________________________________________________
# Drag implementation from https://www.pythonguis.com/faq/pyqt-drag-drop-widgets/

from PyQt5.QtWidgets import QHBoxLayout, QLabel
from PyQt5.QtCore import Qt, QMimeData, pyqtSignal
from PyQt5.QtGui import QDrag, QPixmap


class DragItem(QLabel):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setContentsMargins(25, 5, 25, 5)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("border: 1px solid black;")
        # Store data separately from display label, but use label for default.
        self.data = self.text()

    def set_data(self, data):
        self.data = data

    def mouseMoveEvent(self, e):
        if e.buttons() == Qt.LeftButton:
            drag = QDrag(self)
            mime = QMimeData()
            drag.setMimeData(mime)

            pixmap = QPixmap(self.size())
            self.render(pixmap)
            drag.setPixmap(pixmap)

            drag.exec_(Qt.MoveAction)


class DragWidget(QWidget):
    """
    Generic list sorting handler.
    """

    orderChanged = pyqtSignal(list)

    def __init__(self, *args, orientation=Qt.Orientation.Vertical, **kwargs):
        super().__init__()
        self.setAcceptDrops(True)

        # Store the orientation for drag checks later.
        self.orientation = orientation

        if self.orientation == Qt.Orientation.Vertical:
            self.blayout = QVBoxLayout()
        else:
            self.blayout = QHBoxLayout()

        self.setLayout(self.blayout)

    def dragEnterEvent(self, e):
        e.accept()

    def dropEvent(self, e):
        pos = e.pos()
        widget = e.source()

        for n in range(self.blayout.count()):
            # Get the widget at each index in turn.
            w = self.blayout.itemAt(n).widget()
            if self.orientation == Qt.Orientation.Vertical:
                # Drag drop vertically.
                drop_here = pos.y() < w.y() + w.size().height() // 2
            else:
                # Drag drop horizontally.
                drop_here = pos.x() < w.x() + w.size().width() // 2

            if drop_here:
                # We didn't drag past this widget.
                # insert to the left of it.
                self.blayout.insertWidget(n - 1, widget)
                self.orderChanged.emit(self.get_item_data())
                break

        e.accept()

    def add_item(self, item):
        self.blayout.addWidget(item)

    def get_item_data(self):
        data = []
        for n in range(self.blayout.count()):
            # Get the widget at each index in turn.
            w = self.blayout.itemAt(n).widget()
            data.append(w.data)
        return data


# Drag classes end________________________________________________________________________

class Files(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Nested Layouts Example")
        # create an outer layout
        outerLayout = QVBoxLayout()
        # Create a form layout for the label and line edit
        topLayout = QFormLayout()
        # Add a label and a line added to the form layout
        topLayout.addRow('Some Text: ', QLineEdit())
        # Create a layout for the checkboxes
        optionsLayout = QVBoxLayout()
        # Add some checkboxes to the layout
        optionsLayout.addWidget(QCheckBox("Option 1"))
        optionsLayout.addWidget(QCheckBox("Option 2"))
        optionsLayout.addWidget(QCheckBox("Option 3"))
        # Nest the inner layouts into the outer layout
        outerLayout.addLayout(topLayout)
        outerLayout.addLayout(optionsLayout)
        self.setLayout(outerLayout)


class Labels(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Nested Layouts Example")
        # create an outer layout
        outerLayout = QVBoxLayout()
        # Create a form layout for the label and line edit
        topLayout = QFormLayout()
        # Add a label and a line added to the form layout
        topLayout.addRow('Some Text: ', QLineEdit())
        # Create a layout for the checkboxes
        optionsLayout = QVBoxLayout()
        # Add some checkboxes to the layout
        optionsLayout.addWidget(QCheckBox("Option 1"))
        optionsLayout.addWidget(QCheckBox("Option 2"))
        optionsLayout.addWidget(QCheckBox("Option 3"))
        # Nest the inner layouts into the outer layout
        outerLayout.addLayout(topLayout)
        outerLayout.addLayout(optionsLayout)
        self.setLayout(outerLayout)


class PageWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QStackedLayout Example")

        # Create a top-level layout
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Create and connect the combo box to switch between annotation type pages
        self.pageCombo = QComboBox()
        self.pageCombo.addItems(["Cycle", "Timeline"])
        self.pageCombo.activated.connect(self.switchPage)

        # Create the stacked layout
        self.stackedLayout = QStackedLayout()

        # Create the first page
        self.page1 = QWidget()
        self.page1Layout = QFormLayout()
        self.page1Layout.addRow("Labels:", QLineEdit())
        self.page1Layout.addRow("Duration:", QLineEdit())
        self.page1.setLayout(self.page1Layout)
        self.stackedLayout.addWidget(self.page1)

        # Create the second page
        self.page2 = QWidget()
        self.page2Layout = QFormLayout()
        self.page2Layout.addRow("Labels:", QLineEdit())
        self.page2Layout.addRow("Duration:", QLineEdit())
        self.page2.setLayout(self.page2Layout)
        self.stackedLayout.addWidget(self.page2)

        # Add the combo box and the stacked layout to the top-level layout
        layout.addWidget(self.pageCombo)
        layout.addLayout(self.stackedLayout)

    def switchPage(self):
        """
        What to do when the annotation type is changed.
        Change the stackedLayout based on the pageCombo currentIndex.
        Switching the page keeps the information on the previous page!
        """
        self.stackedLayout.setCurrentIndex(self.pageCombo.currentIndex())


class FileOrderWidget(QWidget):

    def __init__(self, file_names):
        super().__init__()
        self.drag = DragWidget(orientation=Qt.Orientation.Vertical)
        for n, l in enumerate(file_names):
            item = DragItem(l)
            item.set_data(n)  # Store the initial order.
            self.drag.add_item(item)

        # Print out the changed order.
        self.drag.orderChanged.connect(print)

        layout = QVBoxLayout()
        layout.addStretch(1)
        layout.addWidget(self.drag)
        layout.addStretch(1)
        self.setLayout(layout)


class MyWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QTabWidget Example")
        self.resize(270, 110)
        # Create a top-level layout
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Create the tab widget with two tabs
        tabs = QTabWidget()
        # can add an QIcon here ;)
        tabs.addTab(FileOrderWidget(["File1", "File2", "File3"]), "Files")

        theBox = CollapsibleBox(title="I am the box")
        optionsLayout = QVBoxLayout()
        # Add some checkboxes to the layout
        optionsLayout.addWidget(QCheckBox("Option 1"))
        optionsLayout.addWidget(QCheckBox("Option 2"))
        optionsLayout.addWidget(QCheckBox("Option 3"))
        theBox.setContentLayout(optionsLayout)

        tabs.addTab(theBox, "CollapsibleBox")
        tabs.addTab(Labels(), "Network")

        # add tabs to the top-level layout
        layout.addWidget(tabs)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyWidget()
    window.show()
    sys.exit(app.exec_())
