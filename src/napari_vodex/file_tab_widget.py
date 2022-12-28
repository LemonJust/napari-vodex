# imports info: https://napari.org/stable/plugins/best_practices.html :
# Don’t import from PyQt5 or PySide2 in your plugin: use qtpy. If you use from PyQt5 import QtCore (or similar) in
# your plugin, but the end-user has chosen to use PySide2 for their Qt backend — or vice versa — then your plugin
# will fail to import. Instead use from qtpy import   QtCore. qtpy is a Qt compatibility layer that will import from
# whatever backend is installed in the environment.

import sys
# swap PyQt5 to qtpy before publishing
from PyQt5.QtCore import Qt, QPropertyAnimation, QAbstractAnimation, QParallelAnimationGroup

from PyQt5.QtWidgets import (

    QApplication,
    QDialog,
    QAbstractItemView,
    QGridLayout,
    QComboBox,
    QErrorMessage,
    QScrollArea,
    QSpinBox,
    QSizePolicy,
    QSplitter,
    QFrame,
    QTextBrowser,
    QTextEdit,
    QToolButton,
    QPushButton,
    QCheckBox,
    QTabWidget,
    QTableWidget,
    QLabel,
    QLayout,
    QListWidget,
    QListWidgetItem,
    QFormLayout,
    QLineEdit,
    QStackedLayout,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QFileDialog,
    QMessageBox,
    QTableWidgetItem,
    QHeaderView,
    QInputDialog

)

from pathlib import Path
from functools import partial

import vodex as vx

# _______________________________________________________________________________
# Collapsable implementation can be also found
# https://stackoverflow.com/questions/52615115/how-to-create-collapsible-box-in-pyqt

from PyQt5 import QtCore

from PyQt5.QtWidgets import (QPushButton, QDialog, QTreeWidget,
                             QTreeWidgetItem, QVBoxLayout,
                             QHBoxLayout, QFrame, QLabel,
                             QApplication)


class SectionExpandButton(QPushButton):
    """a QPushbutton that can expand or collapse its section
    """

    def __init__(self, item, text="", parent=None):
        super().__init__(text, parent)
        self.section = item
        self.clicked.connect(self.on_clicked)

    def on_clicked(self):
        """toggle expand/collapse of section by clicking
        """
        if self.section.isExpanded():
            self.section.setExpanded(False)
        else:
            self.section.setExpanded(True)


# modified from
# https://stackoverflow.com/questions/32476006/how-to-make-an-expandable-collapsable-section-widget-in-qt
class CollapsibleDialog(QWidget):
    """a dialog to which collapsible sections can be added;
    subclass and reimplement define_sections() to define sections and
        add them as (title, widget) tuples to self.sections
    """

    def __init__(self):
        super().__init__()
        self.tree = QTreeWidget()
        self.tree.setHeaderHidden(True)
        layout = QVBoxLayout()
        layout.addWidget(self.tree)
        self.setLayout(layout)
        self.tree.setIndentation(0)

        self.sections = []
        self.define_sections()
        self.add_sections()

    def add_sections(self):
        """adds a collapsible sections for every
        (title, widget) tuple in self.sections
        """
        for (title, widget) in self.sections:
            button1 = self.add_button(title)
            section1 = self.add_widget(button1, widget)
            button1.addChild(section1)

    def define_sections(self):
        """reimplement this to define all your sections
        and add them as (title, widget) tuples to self.sections
        """
        widget = QTextEdit(self.tree)
        title = "description"
        self.sections.append((title, widget))

    def add_button(self, title):
        """creates a QTreeWidgetItem containing a button
        to expand or collapse its section
        """
        item = QTreeWidgetItem()
        self.tree.addTopLevelItem(item)
        self.tree.setItemWidget(item, 0, SectionExpandButton(item, text=title))
        return item

    def add_widget(self, button, widget):
        """creates a QWidgetItem containing the widget,
        as child of the button-QWidgetItem
        """
        section = QTreeWidgetItem(button)
        section.setDisabled(True)
        self.tree.setItemWidget(section, 0, widget)
        return section


class CollapsibleBox(QWidget):
    # this one is from https://github.com/MichaelVoelkel/qt-collapsible-section/blob/master/Section.py

    def __init__(self, title="", animationDuration=10, parent=None):
        super().__init__(parent)
        self.animationDuration = animationDuration
        self.toggleButton = QToolButton(self)
        self.headerLine = QFrame(self)
        self.toggleAnimation = QParallelAnimationGroup(self)
        self.contentArea = QScrollArea(self)
        self.mainLayout = QGridLayout(self)

        self.toggleButton.setStyleSheet("QToolButton {border: none;}")
        self.toggleButton.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.toggleButton.setArrowType(Qt.RightArrow)
        self.toggleButton.setText(title)
        self.toggleButton.setCheckable(True)
        self.toggleButton.setChecked(False)

        self.headerLine.setFrameShape(QFrame.HLine)
        self.headerLine.setFrameShadow(QFrame.Sunken)
        self.headerLine.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)

        # self.contentArea.setLayout(wd.QHBoxLayout())
        self.contentArea.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        # start out collapsed
        self.contentArea.setMaximumHeight(0)
        self.contentArea.setMinimumHeight(0)

        # let the entire widget grow and shrink with its content
        self.toggleAnimation.addAnimation(QPropertyAnimation(self, b"minimumHeight"))
        self.toggleAnimation.addAnimation(QPropertyAnimation(self, b"maximumHeight"))
        self.toggleAnimation.addAnimation(QPropertyAnimation(self.contentArea, b"maximumHeight"))

        self.mainLayout.setVerticalSpacing(0)
        self.mainLayout.setContentsMargins(0, 0, 0, 0)

        row = 0
        self.mainLayout.addWidget(self.toggleButton, row, 0, 1, 1, Qt.AlignTop)
        self.mainLayout.addWidget(self.headerLine, row, 2, 1, 1, Qt.AlignTop)
        self.mainLayout.addWidget(self.contentArea, row + 1, 0, 1, 3, Qt.AlignTop)
        self.setLayout(self.mainLayout)

        self.toggleButton.toggled.connect(self.toggle)

    def setContentLayout(self, contentLayout):
        layout = self.contentArea.layout()
        del layout
        self.contentArea.setLayout(contentLayout)
        collapsedHeight = self.sizeHint().height() - self.contentArea.maximumHeight()
        contentHeight = contentLayout.sizeHint().height()
        for i in range(0, self.toggleAnimation.animationCount() - 1):
            SectionAnimation = self.toggleAnimation.animationAt(i)
            SectionAnimation.setDuration(self.animationDuration)
            SectionAnimation.setStartValue(collapsedHeight)
            SectionAnimation.setEndValue(collapsedHeight + contentHeight)
        contentAnimation = self.toggleAnimation.animationAt(self.toggleAnimation.animationCount() - 1)
        contentAnimation.setDuration(self.animationDuration)
        contentAnimation.setStartValue(0)
        contentAnimation.setEndValue(contentHeight)

    def setContentWidget(self, widget):
        contentLayout = QVBoxLayout()
        contentLayout.addWidget(widget)
        self.setContentLayout(contentLayout)

    def toggle(self, collapsed):
        if collapsed:
            self.toggleButton.setArrowType(Qt.DownArrow)
            self.toggleAnimation.setDirection(QAbstractAnimation.Forward)
        else:
            self.toggleButton.setArrowType(Qt.RightArrow)
            self.toggleAnimation.setDirection(QAbstractAnimation.Backward)
        self.toggleAnimation.start()


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

        # Create a top-level layout
        edit_layout = QVBoxLayout()
        # prepare the list
        self.list_widget = QListWidget()
        # setting drag drop mode
        self.list_widget.setDragDropMode(QAbstractItemView.InternalMove)
        self.fill_list(file_names)
        edit_layout.addWidget(self.list_widget)

        # Add the buttons
        button_layout = QHBoxLayout()
        self.delete_button = QPushButton("Delete File")
        self.save_button = QPushButton("Save File Order")
        self.edit_button = QPushButton("Edit Files")

        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.edit_button)
        self.edit_button.hide()

        edit_layout.addLayout(button_layout)

        self.setLayout(edit_layout)

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

    def freeze(self):
        """
        Freeze the file-list widget: doesn't allow any modifications until Edit button is pressed.
        """
        try:
            self.list_widget.setDragEnabled(False)
            self.list_widget.setEnabled(False)
            # hide the buttons
            self.delete_button.hide()
            self.save_button.hide()
            self.edit_button.show()
        except Exception as e:
            print(e)

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

        # 1. get directory box and browse button
        self.dir_location = QLineEdit()
        self.browse_button = QPushButton("Browse")
        self.edit_dir_button = QPushButton("Edit")
        main_layout.addWidget(QLabel("Enter the data directory (no spaces at the end):"))
        dir_layout = QHBoxLayout()
        dir_layout.addWidget(self.dir_location)
        dir_layout.addWidget(self.browse_button)
        dir_layout.addWidget(self.edit_dir_button)
        self.edit_dir_button.hide()
        main_layout.addLayout(dir_layout)

        # 2. get file type combo box
        self.file_types = QComboBox()
        ftype_layout = QFormLayout()
        ftype_layout.addRow("Choose file type:", self.file_types)
        # grabs the file types from vodex core.py
        self.file_types.addItems(vx.VX_SUPPORTED_TYPES.keys())
        ftype_layout.addWidget(self.file_types)
        main_layout.addLayout(ftype_layout)
        main_layout.addWidget(QLabel("* Currently only supports tiffiles.\n   "
                                     "Support for other types can be added in the future."))

        # 3. get files button
        self.files_button = QPushButton("Fetch files")
        main_layout.addWidget(self.files_button)

        # list file names
        main_layout.addWidget(QLabel("Inspect the files carefully!\nThe files appear in the order in which they will "
                                     "be read (top to bottom)!\nYou can delete unwanted files and reorder if the "
                                     "order is not correct."))
        self.list_widget = FileListDisplay([])
        main_layout.addWidget(self.list_widget)

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
        """
        Makes the field to enter the directory inactive.
        """
        self.dir_location.setEnabled(False)
        self.browse_button.hide()
        self.edit_dir_button.show()

    def unfreeze_dir(self):
        self.dir_location.setEnabled(True)
        self.browse_button.show()
        self.edit_dir_button.hide()


class VolumeTab(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Volumes Tab")
        # Create a top-level layout
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # Add volumes info layout
        self.fpv = QSpinBox()
        self.fgf = QSpinBox()
        self.fpv.setMinimum(1)
        self.fgf.setMinimum(0)
        self.fgf.setValue(0)
        volume_info_lo = QFormLayout()
        volume_info_lo.addRow("Frames per volume:", self.fpv)
        volume_info_lo.addRow("First good frame:", self.fgf)
        main_layout.addLayout(volume_info_lo)

        # get volumes button
        self.vm = None
        self.volumes_button = QPushButton("Save Volume Info")
        main_layout.addWidget(self.volumes_button)
        # change directory button
        self.edit_vol_button = QPushButton("Edit Volume Info")
        main_layout.addWidget(self.edit_vol_button)
        self.edit_vol_button.hide()

        # list file names
        self.info = QLabel("Inspect the info carefully! Is it what you expect?")
        main_layout.addWidget(self.info)
        self.volume_info_string = QTextBrowser()
        main_layout.addWidget(self.volume_info_string)

    def freeze_vm(self, do_nothing=False):
        try:
            if not do_nothing:
                # create FileManager
                self.fpv.setEnabled(False)
                self.fgf.setEnabled(False)
                self.volumes_button.hide()
                self.edit_vol_button.show()
        except Exception as e:
            print(e)

    def unfreeze_vm(self):
        try:
            self.fpv.setEnabled(True)
            self.fgf.setEnabled(True)
            self.volumes_button.show()
            self.edit_vol_button.hide()
        except Exception as e:
            print(e)


class LabelsTab(QWidget):
    """
    Widget to get the information about individual label: it's name and description.
    """

    def __init__(self):
        super().__init__()
        try:
            self.main_lo = QVBoxLayout()
            self.setLayout(self.main_lo)

            # Table
            self.ROW_HEIGHT = 30  # pixels
            self.label_table = QTableWidget()
            self.set_up_table()
            self.main_lo.addWidget(self.label_table)

            # Add/ Delete buttons
            self.add_label = QPushButton("Add label")
            self.delete_selected = QPushButton("Delete selected")
            self.add_label.clicked.connect(self.add_row)
            self.delete_selected.clicked.connect(self.delete_row)
            button_lo = QHBoxLayout()
            button_lo.addWidget(self.add_label)
            button_lo.addWidget(self.delete_selected)
            self.main_lo.addLayout(button_lo)

            # Save and Edit button
            self.save_labels = QPushButton("Save labels")
            self.edit_labels = QPushButton("Edit labels")

            self.main_lo.addWidget(self.save_labels)
            self.main_lo.addWidget(self.edit_labels)
            self.edit_labels.hide()

            # Error window
            self.msg = InputError()
        except Exception as e:
            print(e)

    def set_up_table(self):
        self.label_table.setColumnCount(2)
        self.label_table.setColumnWidth(0, 150)
        # self.label_table.verticalHeader().hide()
        self.label_table.setHorizontalHeaderLabels(["Label name", "Description (Optional)"])
        self.label_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.label_table.setSelectionMode(QAbstractItemView.SingleSelection)
        h_header = self.label_table.horizontalHeader()
        h_header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

    def add_row(self):
        n_rows = self.label_table.rowCount()
        self.label_table.insertRow(n_rows)
        self.label_table.setRowHeight(n_rows, self.ROW_HEIGHT)

        self.label_table.setItem(n_rows, 0, QTableWidgetItem("Enter Name"))
        self.label_table.setItem(n_rows, 1, QTableWidgetItem(""))

    def delete_row(self):
        try:
            # self.setParent(None)
            # self.deleteLater()
            selected_row = self.label_table.selectedItems()[0].row()
            self.label_table.removeRow(selected_row)
        except Exception as e:
            print(e)

    def get_names(self):
        n_rows = self.label_table.rowCount()
        state_names = []
        for row in range(n_rows):
            name = self.label_table.item(row, 0).text()
            if name in state_names:
                self.launch_popup("The label names must be unique!")
                return None
            else:
                state_names.append(name)
        return state_names

    def get_descriptions(self):
        n_rows = self.label_table.rowCount()
        state_info = {}
        for row in range(n_rows):
            name = self.label_table.item(row, 0).text()
            if name in state_info.keys():
                self.launch_popup("The label names must be unique!")
                return None
            else:
                state_info[name] = self.label_table.item(row, 1).text()
        return state_info

    def freeze(self):
        self.label_table.setEnabled(False)
        self.add_label.setEnabled(False)
        self.delete_selected.setEnabled(False)
        self.edit_labels.show()
        self.save_labels.hide()

    def unfreeze(self):
        self.label_table.setEnabled(True)
        self.add_label.setEnabled(True)
        self.delete_selected.setEnabled(True)
        self.edit_labels.hide()
        self.save_labels.show()

    def launch_popup(self, text):
        self.msg.setText(text)
        x = self.msg.exec_()  # this will show our messagebox


class InputError(QMessageBox):
    def __init__(self):
        super().__init__()
        # tutorial on message boxes: https://www.techwithtim.net/tutorials/pyqt5-tutorial/messageboxes/
        self.setWindowTitle("Input Error")
        self.setStandardButtons(QMessageBox.Ok)  # | QMessageBox.Cancel) if adding more buttons, separate with "|"
        self.setDefaultButton(QMessageBox.Ok)  # setting default button to Cancel
        self.buttonClicked.connect(self.popup_clicked)
        # self.msg.setInformativeText("Some informative text")

    def popup_clicked(self, i):
        print(i.text())


class ConditionTab(QWidget):
    """"

    """

    def __init__(self, labels):
        super().__init__()
        main_lo = QHBoxLayout()
        self.setLayout(main_lo)

        # Label adder

        self.add_button = QPushButton("Add")
        self.save_button = QPushButton("Save Annotation")
        self.ROW_HEIGHT = 30

        self.add_button.setFixedHeight(self.ROW_HEIGHT)
        self.save_button.setFixedHeight(self.ROW_HEIGHT)
        # I'll keep this connect here... since it's for every new object
        # How do people do it through the controller ( do they? )
        self.add_button.clicked.connect(lambda: self.add_row(labels))
        self.save_button.clicked.connect(self.get_label_name_order)

        input_lo = QVBoxLayout()
        input_lo.addWidget(self.add_button)
        input_lo.addWidget(self.save_button)
        input_lo.addStretch(42)
        main_lo.addLayout(input_lo)

        # Table
        self.label_table = QTableWidget()
        self.set_up_table()
        main_lo.addWidget(self.label_table)

    def set_up_table(self):
        self.label_table.setColumnCount(2)
        self.label_table.setColumnWidth(0, 150)
        self.label_table.setHorizontalHeaderLabels(["Label name", "Duration"])
        self.label_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.label_table.setSelectionMode(QAbstractItemView.SingleSelection)
        h_header = self.label_table.horizontalHeader()
        h_header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

    def add_row(self, labels):
        # create the elements to insert
        label_choice = QComboBox()
        duration = QSpinBox()
        label_choice.addItems(labels)
        duration.setMinimum(1)

        n_rows = self.label_table.rowCount()
        self.label_table.insertRow(n_rows)
        self.label_table.setRowHeight(n_rows, self.ROW_HEIGHT)

        self.label_table.setCellWidget(n_rows, 0, label_choice)
        self.label_table.setCellWidget(n_rows, 1, duration)

    def get_label_name_order(self):
        try:
            n_rows = self.label_table.rowCount()
            label_name_order = [self.label_table.cellWidget(row, 0).currentText() for row in range(n_rows)]
            print(label_name_order)
        except Exception as e:
            print(e)
        return label_name_order

    def get_duration(self):
        n_rows = self.label_table.rowCount()
        duration = [self.label_table.cellWidget(row, 1).value() for row in range(n_rows)]
        return duration


class TimingTab(QWidget):

    def __init__(self, labels):
        super().__init__()
        try:
            # Create a top-level layout
            main_layout = QVBoxLayout()
            self.setLayout(main_layout)

            # Create and connect the combo box to switch between annotation type pages
            self.annotation_type = QComboBox()
            self.annotation_type.addItems(["Cycle", "Timeline", "From File"])
            self.annotation_type.activated.connect(self.switchPage)

            # Create the stacked layout
            self.stackedLayout = QStackedLayout()
            self.cycle = ConditionTab(labels=labels)
            self.timeline = ConditionTab(labels=labels)
            self.file_widget = self.create_file_widget()
            self.stackedLayout.addWidget(self.cycle)
            self.stackedLayout.addWidget(self.timeline)
            self.stackedLayout.addWidget(self.file_widget)

            # Add the combo box and the stacked layout to the top-level layout
            main_layout.addWidget(self.annotation_type)
            main_layout.addLayout(self.stackedLayout)
        except Exception as e:
            print(e)

    def switchPage(self):
        """
        What to do when the annotation type is changed.
        Change the stackedLayout based on the annotation_type currentIndex.
        Switching the page keeps the information on the previous page!
        """
        self.stackedLayout.setCurrentIndex(self.annotation_type.currentIndex())

    @staticmethod
    def create_file_widget():
        from_file = QWidget()
        from_file_lo = QVBoxLayout()
        from_file_lo.addWidget(QLabel("Loading from file is not supported yet."))
        from_file.setLayout(from_file_lo)
        return from_file

    def get_timing(self):
        annotation_type = self.annotation_type.currentText()


class AnnotationPage(QWidget):

    def __init__(self):
        super().__init__()

        # Create a top-level layout
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        # create labels Tab
        self.labels = LabelsTab()
        self.timing = None
        self.splitter = QSplitter(Qt.Vertical)
        self.splitter.addWidget(self.labels)
        self.main_layout.addWidget(self.splitter)

        # connecting it here, since there might be many annotation pages
        self.labels.save_labels.clicked.connect(lambda: self.initialize_timeline(self.labels.get_names()))
        self.labels.edit_labels.clicked.connect(self.remove_timeline)

    def initialize_timeline(self, label_names):
        if label_names is not None:
            # freeze the labels tab
            self.labels.freeze()
            # create timeline
            self.timing = TimingTab(label_names)
            # add to splitter
            self.splitter.addWidget(self.timing)

    def remove_timeline(self):
        # unfreeze the labels tab
        self.labels.unfreeze()

        # remove timeline
        self.timing.hide()
        self.timing.deleteLater()

    def update_timeline(self, label_names):
        """
        Updates timeline tab with additional labels.
        """
        pass


class AnnotationTab(QWidget):

    def __init__(self):
        super().__init__()
        # Create a top-level layout
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        self.annotations = {}
        switch_lo = QHBoxLayout()
        self.add_annotation_pb = QPushButton("Add annotation")
        self.add_annotation_pb.clicked.connect(self.create_annotation)
        switch_lo.addWidget(QLabel("Annotations:"))
        switch_lo.addWidget(self.add_annotation_pb)
        main_layout.addLayout(switch_lo)
        # Create and connect the combo box to switch between annotation type pages
        self.pageCombo = QComboBox()
        self.pageCombo.activated.connect(self.switchPage)
        # Create the stacked layout
        self.stackedLayout = QStackedLayout()
        # Add the combo box and the stacked layout to the top-level layout
        main_layout.addWidget(self.pageCombo)
        main_layout.addLayout(self.stackedLayout)

    def switchPage(self):
        """
        What to do when the annotation type is changed.
        Change the stackedLayout based on the pageCombo currentIndex.
        Switching the page keeps the information on the previous page!
        """
        self.stackedLayout.setCurrentIndex(self.pageCombo.currentIndex())

    def create_annotation(self):
        annotation_name, ok = QInputDialog.getText(self, 'Enter annotation name', 'Try to choose meaningful names, '
                                                                                  'for example:\n"Light" to describe '
                                                                                  'whether the light was on or off;\n'
                                                                                  '"Drug" to set the time when you '
                                                                                  'added the drug;')
        if ok:
            try:
                annotation = AnnotationPage()
                self.annotations[annotation_name] = annotation
                self.pageCombo.addItem(annotation_name)
                # set the added item active
                self.pageCombo.setCurrentText(annotation_name)
                self.stackedLayout.addWidget(annotation)
            except Exception as e:
                print(e)


class VodexView(QWidget):
    """
    Does everything about the GUI.
    """

    def __init__(self):
        super().__init__()

        self.ft = FileTab()
        self.vt = VolumeTab()
        # self.lt = LabelsTab()
        self.at = AnnotationTab()

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        tabs = QTabWidget()

        # Create a top-level layout
        # files_layout = QVBoxLayout()
        # More on QSplitter: https://www.tutorialspoint.com/pyqt/pyqt_qsplitter_widget.htm
        splitter_data = QSplitter(Qt.Vertical)
        splitter_data.addWidget(self.ft)
        splitter_data.addWidget(self.vt)
        tabs.addTab(splitter_data, "Image Data")

        # splitter_antn = QSplitter(Qt.Vertical)
        # splitter_antn.addWidget(self.lt)
        # splitter_antn.addWidget(self.at)
        tabs.addTab(self.at, "Time Annotation")

        main_layout.addWidget(tabs)
        # self.error_dialog = QErrorMessage()


class VodexModel:
    """
    Does everything on the vodex side.
    """

    def __init__(self):
        self.fm = None
        self.vm = None
        self.annotations = None

    def crete_fm(self, data_dir, file_type, file_names=None):
        """
        Creates the FileManager.
        """
        self.fm = vx.FileManager(data_dir, file_type=file_type, file_names=file_names)

    def remove_fm(self):
        """
        Removes the FileManager.
        """
        self.annotations = None

    def create_vm(self, fpv, fgf):
        """
        Creates the VolumeManager.
        """
        self.vm = vx.VolumeManager(fpv, vx.FrameManager(self.fm), fgf=fgf)

    def remove_vm(self):
        """
        Removes the VolumeManager.
        """
        self.vm = None


class VodexController:
    """
    Controller class for the GUI (following the MVC schema).
    """

    def __init__(self, model, view):

        self._model = model
        self._view = view

        self._connectDisplaySignalsAndSlots()

    def initialize_fm(self):
        """
        Executed when [Get Files] button is pressed.
        Initialises FileManager with all the files retrieved from the data directory
        and adds the files to the list to inspect.
        """
        try:
            # create FileManager
            data_dir = self._view.ft.dir_location.text()
            file_type = self._view.ft.file_types.currentText()
            self._model.crete_fm(data_dir, file_type)

            # update list of files
            self._view.ft.list_widget.fill_list(self._model.fm.file_names)
        except Exception as e:
            self._view.error_dialog.showMessage(e)

    def update_fm(self):
        """
        Executed when [Save File Order] button is pressed.
        Updates a FileManager with the edited files.
        """
        try:
            data_dir = self._view.ft.dir_location.text()
            file_type = self._view.ft.file_types.currentText()
            file_names = self._view.ft.list_widget.get_file_names()

            # create new FileManager from updated file list
            self._model.crete_fm(data_dir, file_type, file_names=file_names)
        except Exception as e:
            self._view.error_dialog.showMessage(e)

    def remove_fm(self):
        """
        Executed when the [Change Directory] button is pressed.
        Deletes existing FileManager and clears file list.
        """
        # clear dependent managers
        self.remove_vm()
        self.remove_annotations()

        try:
            # remove FileManager from the model
            self._model.remove_fm()
            # clear files from list and make it active
            self._view.ft.list_widget.list_widget.clear()
            self._view.ft.list_widget.unfreeze()
        except Exception as e:
            self._view.error_dialog.showMessage(e)

    def initialize_vm(self):
        """
        Executed when [Save Volume Info] button is pressed.
        Initialises VolumeManager and outputs the recording summary to inspect.
        """
        try:
            if self._view.ft.list_widget.list_widget.isEnabled():
                self._view.vt.volume_info_string.setText("Save changes to the files first!")
            else:
                # create new VolumeManager from updated file list
                fpv = self._view.vt.fpv.value()
                fgf = self._view.vt.fgf.value()
                self._model.create_vm(fpv, fgf)

                # update the volume info summary
                self._view.vt.volume_info_string.setText(str(self._model.vm))
                # If ever appending anything: self.output_rd.append(str(rad_dis))
        except Exception as e:
            print(e)
            self._view.error_dialog.showMessage(e)

    def remove_vm(self):
        """
        Executed when the [Change Directory] of [Edit Volume Info] button is pressed.
        Deletes existing VolumeManager and clears file list.
        """
        self._model.remove_vm()

        # remove the volume info summary
        self._view.vt.volume_info_string.setText("")
        # sets the volume info inputs to enabled

    def remove_annotations(self):
        pass

    def initialize_at(self):
        """
        Executed when [???] button is pressed.
        Initialises ??? and outputs the recording summary to inspect.
        """
        try:
            if self._view.lt.get_label_info() is not None:
                # freeze the labels
                self._view.lt.freeze()
                # create annotation tab
                self._view.create_at()
        except Exception as e:
            print(e)
            self._view.error_dialog.showMessage(e)

    def _connectDisplaySignalsAndSlots(self):

        # 1. connect FileTab
        # _______________________________________________________________________________________________
        # [Browse] button
        self._view.ft.browse_button.clicked.connect(self._view.ft.browse)

        # [Find files] button
        self._view.ft.files_button.clicked.connect(self.initialize_fm)
        self._view.ft.files_button.clicked.connect(self._view.ft.freeze_dir)

        # [Change Directory] button
        self._view.ft.edit_dir_button.clicked.connect(self.remove_fm)
        self._view.ft.edit_dir_button.clicked.connect(self._view.ft.unfreeze_dir)

        # [Delete File] button
        self._view.ft.list_widget.delete_button.clicked.connect(self._view.ft.list_widget.delete_file)

        # [Save File Order] button
        # TODO : what to do when press Save with an empty list
        self._view.ft.list_widget.save_button.clicked.connect(self.update_fm)
        self._view.ft.list_widget.save_button.clicked.connect(self._view.ft.list_widget.freeze)
        self._view.ft.list_widget.edit_button.clicked.connect(self._view.vt.unfreeze_vm)

        # [Edit Files] button
        self._view.ft.list_widget.edit_button.clicked.connect(self._view.ft.list_widget.unfreeze)
        self._view.ft.list_widget.edit_button.clicked.connect(self.remove_vm)

        # 2. connect VolumeTab
        # _______________________________________________________________________________________________
        # [Save Volume Info] button
        # update the volume info summary
        self._view.vt.volumes_button.clicked.connect(self.initialize_vm)
        self._view.vt.volumes_button.clicked.connect(lambda: self._view.vt.freeze_vm(
            self._view.ft.list_widget.list_widget.isEnabled()))

        # [Edit Volume Info] button
        self._view.vt.edit_vol_button.clicked.connect(self.remove_vm)
        self._view.vt.edit_vol_button.clicked.connect(self._view.vt.unfreeze_vm)

        # 4. connect LabelsTab
        # _______________________________________________________________________________________________
        # [Save Labels] button
        # self._view.lt.save_labels.clicked.connect(self.initialize_at)


if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        window = VodexView()
        window.show()
        vc = VodexController(model=VodexModel(), view=window)
        sys.exit(app.exec_())
    except Exception as e:
        print(e)
