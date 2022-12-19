# imports info: https://napari.org/stable/plugins/best_practices.html :
# Don’t import from PyQt5 or PySide2 in your plugin: use qtpy. If you use from PyQt5 import QtCore (or similar) in
# your plugin, but the end-user has chosen to use PySide2 for their Qt backend — or vice versa — then your plugin
# will fail to import. Instead use from qtpy import   QtCore. qtpy is a Qt compatibility layer that will import from
# whatever backend is installed in the environment.

import sys
# swap PyQt5 to qtpy before publishing
from PyQt5.QtWidgets import (
    QApplication,
    QAbstractItemView,
    QComboBox,
    QScrollArea,
    QSizePolicy,
    QFrame,
    QToolButton,
    QPushButton,
    QCheckBox,
    QTabWidget,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QFormLayout,
    QLineEdit,
    QStackedLayout,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QFileDialog
)
from pathlib import Path

import vodex as vx

# _______________________________________________________________________________
# Collapsable implementation from https://stackoverflow.com/questions/52615115/how-to-create-collapsible-box-in-pyqt

from PyQt5 import QtCore


class CollapsibleBox(QWidget):
    def __init__(self, title="", checked=False):
        super().__init__()

        self.toggle_button = QToolButton(text=title, checkable=True, checked=checked)
        self.toggle_button.setStyleSheet("QToolButton { border: none; }")
        self.toggle_button.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
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

        self.toggle_animation.addAnimation(QtCore.QPropertyAnimation(self, b"minimumHeight"))
        self.toggle_animation.addAnimation(QtCore.QPropertyAnimation(self, b"maximumHeight"))
        self.toggle_animation.addAnimation(QtCore.QPropertyAnimation(self.content_area, b"maximumHeight"))

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


# ______________________________________________________________________

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


class FileListDisplay(QWidget):
    """
    Shows files in the folder. Allows editing.
    """

    def __init__(self, file_names=(f"file {i}" for i in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11])):
        super().__init__()

        self.setWindowTitle("Files in the recording")

        self.list_widget = None
        self.button_layout = None
        self.save_button = None
        self.delete_button = None
        self.edit_button = None
        main_layout = self.get_editable_layout(file_names)

        self.setLayout(main_layout)

    def get_editable_layout(self, file_names):
        """
        Creates the layout that allows to edit the files and their order.
        """
        # Create a top-level layout
        edit_layout = QVBoxLayout()
        # prepare the list
        self.list_widget = QListWidget()
        # setting drag drop mode
        self.list_widget.setDragDropMode(QAbstractItemView.InternalMove)
        self.fill_list(file_names)
        edit_layout.addWidget(self.list_widget)

        self.button_layout = QHBoxLayout()
        self.delete_button = QPushButton("Delete File")
        self.delete_button.clicked.connect(self.delete_file)
        self.button_layout.addWidget(self.delete_button)

        self.save_button = QPushButton("Save File Order")
        self.save_button.clicked.connect(self.freeze)
        self.button_layout.addWidget(self.save_button)

        edit_layout.addLayout(self.button_layout)

        return edit_layout

    def fill_list(self, file_names):
        # clear existing items
        self.list_widget.clear()
        # add file names and order to the list
        for name in file_names:
            # adding items to the list widget
            self.list_widget.addItem(QListWidgetItem(name))

    def delete_file(self):
        """
        Removes a file from the list.
        """
        curItem = self.list_widget.currentItem()
        self.list_widget.takeItem(self.list_widget.row(curItem))
        print(self.list_widget.row(curItem))

    def freeze(self):
        """
        Freeze the file-list widget: doesn't allow any modifications until Edit button is pressed.
        """
        print("In 1")
        try:
            self.list_widget.setDragEnabled(False)
            self.list_widget.setEnabled(False)
            # hide the buttons
            self.delete_button.hide()
            self.save_button.hide()
            # add a note
            self.edit_button = QPushButton("Edit Files")
            self.edit_button.clicked.connect(self.unfreeze)
            self.button_layout.addWidget(self.edit_button)

        except Exception as e:
            print(e)
        print("Done 1")

    def unfreeze(self):
        """
        Unfreeze the file-list widget: doesn't allow any modifications until Edit button is pressed.
        """
        try:
            self.list_widget.setDragEnabled(True)
            self.list_widget.setEnabled(True)
            # hide a button
            self.edit_button.hide()
            # show the buttons
            self.delete_button.show()
            self.save_button.show()
        except Exception as e:
            print(e)

    def get_file_names(self):
        """
        Returns the list of files in the order as they appear in the list.
        """
        all_items = [self.list_widget.item(i).text() for i in range(self.list_widget.count())]
        return all_items


class FileTab(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Files Tab")
        # Create a top-level layout
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # get directory box and browse button
        self.data_dir = None
        self.dir_location = None
        self.browse_button = None
        main_layout.addWidget(QLabel("Blah blah blah insert folder here :"))
        main_layout.addLayout(self._get_dir_layout())

        # get file type combo box
        self.file_type = None
        self.file_types = None
        main_layout.addLayout(self._get_ftype_layout())
        main_layout.addWidget(QLabel("* Currently only supports tiffiles.\n   Support for other types can be added."))

        # get files button
        self.fm = None
        files_button = QPushButton("Get Files")
        files_button.clicked.connect(self.initialize_fm)
        files_button.clicked.connect(self.freeze_dir)
        main_layout.addWidget(files_button)
        # change directory button
        self.edit_dir_button = QPushButton("Change Directory")
        self.edit_dir_button.clicked.connect(self.remove_fm)
        self.edit_dir_button.clicked.connect(self.unfreeze_dir)
        main_layout.addWidget(self.edit_dir_button)
        self.edit_dir_button.hide()

        # list file names
        main_layout.addWidget(QLabel("Inspect the files carefully!\nThe files appear in the order in which they will "
                                     "be read!\nYou can delete unwanted files and reorder if the order is not "
                                     "correct."))
        self.list_widget = FileListDisplay([])
        self.list_widget.save_button.clicked.connect(self.update_fm)
        main_layout.addWidget(self.list_widget)

    def _get_dir_layout(self):
        dir_layout = QHBoxLayout()
        self.dir_location = QLineEdit()
        dir_layout.addWidget(self.dir_location)

        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self.browse)
        dir_layout.addWidget(self.browse_button)
        return dir_layout

    def _get_ftype_layout(self):
        ftype_layout = QHBoxLayout()
        ftype_layout.addWidget(QLabel("File type: "))
        self.file_types = QComboBox()
        # Add your file type here
        # if you have implemented a support for another type for VoDEx
        self.file_types.addItems(vx.VX_SUPPORTED_TYPES.keys())
        ftype_layout.addWidget(self.file_types)
        return ftype_layout

    def browse(self):
        try:
            start_dir = str(Path().absolute())
            if Path(self.dir_location.text()).is_dir():
                start_dir = self.dir_location.text()

            selected_dir = QFileDialog.getExistingDirectory(caption='Choose Directory', directory=start_dir)
            self.dir_location.setText(selected_dir)
        except Exception as e:
            print(e)

    def freeze_dir(self):
        self.dir_location.setEnabled(False)
        self.browse_button.hide()
        self.edit_dir_button.show()

    def unfreeze_dir(self):
        self.dir_location.setEnabled(True)
        self.browse_button.show()
        self.edit_dir_button.hide()

    def initialize_fm(self):
        """
        Executed when [Get Files] button is pressed.
        Initialises FileManager and adds files to the list to inspect.
        """
        try:
            self.data_dir = self.dir_location.text()
            self.file_type = self.file_types.currentText()

            # create FileManager
            self.fm = vx.FileManager(self.data_dir, file_type=self.file_type)
            self.list_widget.fill_list(self.fm.file_names)
        except Exception as e:
            print("Error!")
            print(e)

    def update_fm(self):
        """
        Executed when [Save File Order] button is pressed.
        Updates a FileManager based on the files in the box.
        """
        try:
            file_names = self.list_widget.get_file_names()
            # create new FileManager from updated file list
            self.fm = vx.FileManager(self.data_dir, file_type=self.file_type, file_names=file_names)

            print(self.fm)
        except Exception as e:
            print("Error!")
            print(e)

    def remove_fm(self):
        """
        Executed when the [Change Directory] button is pressed.
        Deletes existing FileManager and clears file list.
        """
        try:
            # remove FileManager
            self.fm = None
            # clear files from list and make it active
            self.list_widget.list_widget.clear()
            self.list_widget.unfreeze()
        except Exception as e:
            print("Error!")
            print(e)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FileTab()
    window.show()
    sys.exit(app.exec_())
