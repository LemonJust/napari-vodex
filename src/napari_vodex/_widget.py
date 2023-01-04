"""
This module is an example of a barebones QWidget plugin for napari

For Widget specification see: https://napari.org/stable/plugins/guides.html?#widgets

"""
from typing import TYPE_CHECKING, List, Union
from pathlib import Path

from magicgui import magic_factory
from qtpy.QtWidgets import \
    QHBoxLayout, QPushButton, QWidget

if TYPE_CHECKING:
    import napari


# imports info: https://napari.org/stable/plugins/best_practices.html :
# Don’t import from PyQt5 or PySide2 in your plugin: use qtpy. If you use from PyQt5 import QtCore (or similar) in
# your plugin, but the end-user has chosen to use PySide2 for their Qt backend — or vice versa — then your plugin
# will fail to import. Instead use from qtpy import   QtCore. qtpy is a Qt compatibility layer that will import from
# whatever backend is installed in the environment.


from pathlib import Path
from typing import Union

from qtpy.QtCore import Qt, QRegExp, QModelIndex
from qtpy.QtGui import QRegExpValidator
from qtpy.QtWidgets import (

    QAbstractItemView,
    QComboBox,
    QSpinBox,
    QSplitter,
    QTextBrowser,
    QTabWidget,
    QTableWidget,
    QListWidget,
    QListWidgetItem,
    QFormLayout,
    QLineEdit,
    QStackedLayout,
    QWidget,
    QFileDialog,
    QMessageBox,
    QTableWidgetItem,
    QHeaderView,
    QInputDialog,
    QStyledItemDelegate,
    QStyle,
    QCheckBox,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QLabel,
    QApplication
)

import vodex as vx
import napari


# _______________________________________________________________________________
# Collapsable implementation can be also found
# https://stackoverflow.com/questions/52615115/how-to-create-collapsible-box-in-pyqt

def horizontal_line():
    line = QFrame()
    # line.setGeometry(QRect(60, 110, 751, 20))
    line.setFrameShape(QFrame.HLine)
    line.setFrameShadow(QFrame.Sunken)
    return line


def clear_layout(layout, keep=0):
    # from https://stackoverflow.com/questions/4528347/clear-all-widgets-in-a-layout-in-pyqt
    while layout.count() - keep:
        child = layout.takeAt(0)
        if child.widget():
            child.widget().deleteLater()


class InputError(QMessageBox):
    def __init__(self, title="Input Error"):
        super().__init__()
        # tutorial on message boxes: https://www.techwithtim.net/tutorials/pyqt5-tutorial/messageboxes/
        self.setWindowTitle(title)
        self.setStandardButtons(QMessageBox.Ok)  # | QMessageBox.Cancel) if adding more buttons, separate with "|"
        self.setDefaultButton(QMessageBox.Ok)  # setting default button to Cancel
        self.buttonClicked.connect(self.popup_clicked)

    def popup_clicked(self, i):
        return i.text()


class UserWarning(QMessageBox):
    def __init__(self, detailed_text):
        super().__init__()
        # tutorial on message boxes: https://www.techwithtim.net/tutorials/pyqt5-tutorial/messageboxes/
        self.setWindowTitle("Warning!")
        self.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)  # if adding more buttons, separate with "|"
        self.setDefaultButton(QMessageBox.Cancel)  # setting default button to Cancel
        self.setText(detailed_text)
        self.buttonClicked.connect(self.popup_clicked)

    def popup_clicked(self, i):
        return i.text()


class LabelCheckBox(QCheckBox):
    """
    Saves the group information and sets the text to name.
    """

    def __init__(self, group: str, name: str):
        super().__init__()
        self.label_info = (group, name)
        self.setText(name)

    def get_label_info(self):
        return self.label_info


class ReadOnlyDelegate(QStyledItemDelegate):
    """
    Overwrites QStyledItemDelegateto turn off editing.
    """

    def createEditor(self, parent: QWidget, option: 'QStyleOptionViewItem', index: QModelIndex) -> None:
        return None


class FileListDisplay(QWidget):
    """
    Shows files in the folder. Allows editing.
    """

    def __init__(self, file_names=[]):
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
        self.list_widget.setDragEnabled(False)
        self.list_widget.setEnabled(False)
        # hide the buttons
        self.delete_button.hide()
        self.save_button.hide()
        self.edit_button.show()

    def unfreeze(self):
        """
        Unfreeze the file-list widget: doesn't allow any modifications until Edit button is pressed.
        """
        self.list_widget.setDragEnabled(True)
        self.list_widget.setEnabled(True)
        # hide a button
        self.edit_button.hide()
        # show the buttons
        self.delete_button.show()
        self.save_button.show()

    def get_file_names(self):
        """
        Returns the list of files in the order as they appear in the list.
        """
        all_items = [self.list_widget.item(i).text() for i in range(self.list_widget.count())]
        return all_items


class LoadExperimentTab(QWidget):
    def __init__(self):
        super().__init__()

        # Create a top-level layout
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        self.load_db_l = QLabel("Load Existing Experiment:")
        self.db_location = QLineEdit()
        self.load_db_pb = QPushButton("Load")
        load_layout = QHBoxLayout()
        load_layout.addWidget(self.db_location)
        load_layout.addWidget(self.load_db_pb)

        main_layout.addWidget(self.load_db_l)
        main_layout.addLayout(load_layout)

        # File Manager Info
        self.info_fm = QLabel("File manager information:")
        main_layout.addWidget(self.info_fm)
        self.fm_info_string = QTextBrowser()
        main_layout.addWidget(self.fm_info_string)

        # Volume Manager Info
        self.info_vm = QLabel("Volume manager information:")
        main_layout.addWidget(self.info_vm)
        self.vm_info_string = QTextBrowser()
        main_layout.addWidget(self.vm_info_string)

    def browse(self):
        start_dir = str(Path().absolute())

        db_location = self.db_location.text().strip()
        if Path(db_location).is_dir():
            start_dir = db_location
        if Path(db_location).is_file():
            start_dir = Path(db_location).parent

        selected_db, ok = QFileDialog.getOpenFileName(caption='Load Database',
                                                      directory=start_dir, filter="Database Files (*.db)")
        self.db_location.setText(selected_db)


class NewExperimentTab(QWidget):
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
        main_layout.addWidget(QLabel("Enter the data directory"))
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

        # 3. fetch files button
        self.files_button = QPushButton("Fetch files")
        main_layout.addWidget(self.files_button)

        # list file names
        main_layout.addWidget(QLabel("Inspect the files carefully!\nThe files appear in the order in which they will "
                                     "be read (top to bottom)!\nYou can delete unwanted files and reorder if the "
                                     "order is not correct."))
        self.list_widget = FileListDisplay([])
        main_layout.addWidget(self.list_widget)

    def browse(self):
        start_dir = str(Path().absolute())
        if Path(self.dir_location.text().strip()).is_dir():
            start_dir = self.dir_location.text()

        selected_dir = QFileDialog.getExistingDirectory(caption='Choose Directory', directory=start_dir)
        self.dir_location.setText(selected_dir)

    def freeze_dir(self):
        """
        Makes the field to enter the directory inactive.
        """
        self.dir_location.setEnabled(False)
        self.browse_button.hide()
        self.edit_dir_button.show()
        self.files_button.setEnabled(False)

    def unfreeze_dir(self):
        self.dir_location.setEnabled(True)
        self.browse_button.show()
        self.edit_dir_button.hide()
        self.files_button.setEnabled(True)


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
        self.fpv.setRange(1, 100000000)  # if range is not set, the maximum is 100, which can be not enough,
        self.fgf.setRange(0, 100000000)  # 100000000 is well within integer range, and hopefully is enough for anyone
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

        # list data info
        self.info = QLabel("Inspect the info carefully! Is it what you expect?")
        main_layout.addWidget(self.info)
        self.volume_info_string = QTextBrowser()
        main_layout.addWidget(self.volume_info_string)

    def freeze_vm(self, do_nothing=False):
        if not do_nothing:
            # create FileManager
            self.fpv.setEnabled(False)
            self.fgf.setEnabled(False)
            self.volumes_button.hide()
            self.edit_vol_button.show()

    def unfreeze_vm(self):
        self.fpv.setEnabled(True)
        self.fgf.setEnabled(True)
        self.volumes_button.show()
        self.edit_vol_button.hide()


class SaveTab(QWidget):

    def __init__(self):
        super().__init__()
        # 1. save FileTab and VolumeTab into a database)
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        main_layout.addWidget(horizontal_line())

        self.save_pb = QPushButton("Save")
        self.save_le = QLineEdit()
        self.info_label = QLabel("Save experiment to a database file:")
        main_layout.addWidget(self.info_label)
        main_layout.addWidget(self.save_le)
        main_layout.addWidget(self.save_pb)

    def get_save_filename(self):
        """
        Returns a filename to save the database or None.
        """
        # from here: https://pythonprogramming.net/file-saving-pyqt-tutorial/

        save_name = self.save_le.text()
        save_directory = Path(save_name).parent
        if save_name.endswith('.db') and save_directory.is_dir():
            file_name = save_name
        else:
            dialog = QFileDialog(self, 'Save File ( data base file format, *.db )')
            dialog.setDefaultSuffix('.db')
            if save_directory.is_dir():
                dialog.setDirectory(save_directory.as_posix())
            file_name, ok = dialog.getSaveFileName()
            if ok:
                if not file_name.endswith('.db'):
                    file_name += ".db"
                self.save_le.setText(file_name)
            else:
                file_name = None
        return file_name


class InitialiseTab(QWidget):
    def __init__(self):
        super().__init__()
        # 1. save FileTab and VolumeTab into a database)
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        # next step
        self.create_experiment = QPushButton("Create Experiment")
        self.edit_experiment = QPushButton("Edit Experiment")
        self.next_step = QLabel("NEXT STEPS: You can save the experiment to disk\n"
                                "or load individual volumes on the [Load/Save Data] tab\n"
                                "or add time annotations on the [Time Annotation]\n")
        main_layout.addWidget(self.create_experiment)
        main_layout.addWidget(self.edit_experiment)
        main_layout.addWidget(self.next_step)

        self.edit_experiment.hide()
        self.next_step.hide()


class LabelsTab(QWidget):
    """
    Widget to get the information about individual label: it's name and description.
    """

    def __init__(self):
        super().__init__()
        self.label_names = []

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

        button_lo = QHBoxLayout()
        button_lo.addWidget(self.add_label)
        button_lo.addWidget(self.delete_selected)
        self.main_lo.addLayout(button_lo)

        # Error window
        self.msg = InputError()

    def set_up_table(self):
        self.label_table.setColumnCount(2)
        self.label_table.setColumnWidth(0, 150)
        # self.label_table.verticalHeader().hide()
        self.label_table.setHorizontalHeaderLabels(["Label name", "Description (Optional)"])
        self.label_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.label_table.setSelectionMode(QAbstractItemView.SingleSelection)
        h_header = self.label_table.horizontalHeader()
        h_header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

        # turn off editing for the first column
        delegate = ReadOnlyDelegate(self.label_table)
        self.label_table.setItemDelegateForColumn(0, delegate)

    def get_label_name(self):
        """
        Receives a label name from the user, checks if the new label name is unique.
        If it is unique, returns the label name, if not, or if the name is empty returns none.
        """
        label_name, ok = QInputDialog.getText(self, 'Enter label name',
                                              'Try to choose meaningful names, \n'
                                              'for example: in an annotation called"Light" \nthe labels could be '
                                              '"on" and "off" \nto describe when the light was on or off.')

        if ok:
            # check that all the names are unique
            if label_name in self.label_names:
                self.launch_popup("The label names must be unique!")
                label_name = None
            # check that it is not empty
            if not label_name:
                label_name = None
        else:
            label_name = None

        # add to the list of labels
        if label_name is not None:
            self.label_names.append(label_name)

        return label_name

    def add_row(self, label_name=None, description=""):
        """
        Adds the label name to the table.
        If the label_name is not provided, triggers the pop-up to ask for the label name.
        """

        if label_name is not None:
            self.label_names.append(label_name)
        else:
            label_name = self.get_label_name()

        if label_name is not None:
            # add to the table
            n_rows = self.label_table.rowCount()
            self.label_table.insertRow(n_rows)
            self.label_table.setRowHeight(n_rows, self.ROW_HEIGHT)

            self.label_table.setItem(n_rows, 0, QTableWidgetItem(label_name))
            self.label_table.setItem(n_rows, 1, QTableWidgetItem(description))

    def delete_row(self, in_use: bool):
        """
        in_use: indicates if the label is in use. If in use, it will not be deleted.
        """
        if not in_use:
            selected_row = self.label_table.currentRow()
            name = self.label_table.item(selected_row, 0).text()
            self.label_names.remove(name)
            self.label_table.removeRow(selected_row)

    def get_selected_name(self):
        """
        Returns the label name on the selected row.
        """
        selected_row = self.label_table.currentRow()
        name = self.label_table.item(selected_row, 0).text()
        return name

    def get_names(self):
        """
        Returns all the names in the table.
        """
        n_rows = self.label_table.rowCount()
        state_names = []
        for row in range(n_rows):
            name = self.label_table.item(row, 0).text()
            state_names.append(name)
        return state_names

    def get_descriptions(self):
        """
        Returns all the descriptions in the table.
        """
        n_rows = self.label_table.rowCount()
        state_info = {}
        for row in range(n_rows):
            name = self.label_table.item(row, 0).text()
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


class TimingTab(QWidget):
    """
    Contains the information about the timing of the conditions.
    """

    def __init__(self):
        super().__init__()
        # Create a top-level layout
        main_lo = QVBoxLayout()
        self.setLayout(main_lo)

        # Create and connect the combo box to switch between annotation type pages
        self.annotation_type = QComboBox()
        self.annotation_type.addItems(["Cycle", "Timeline"])
        main_lo.addWidget(self.annotation_type)

        table_lo = QHBoxLayout()
        # Label adder
        self.add_button = QPushButton("Add condition")
        self.del_button = QPushButton("Delete condition")
        self.ROW_HEIGHT = 30
        self.add_button.setFixedHeight(self.ROW_HEIGHT)

        input_lo = QVBoxLayout()
        input_lo.addWidget(self.add_button)
        input_lo.addWidget(self.del_button)
        input_lo.addStretch(42)
        table_lo.addLayout(input_lo)

        # Table
        self.table = QTableWidget()
        self.set_up_table()
        table_lo.addWidget(self.table)
        main_lo.addLayout(table_lo)

        self.msg = InputError()

    def set_up_table(self):
        self.table.setColumnCount(2)
        self.table.setColumnWidth(0, 150)
        self.table.setHorizontalHeaderLabels(["Label name", "Duration"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        h_header = self.table.horizontalHeader()
        h_header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

    def add_row(self, labels: List[str], label_name: str = None, duration: int = None):
        """
        Adds a row to the table and sets the widgets in the cells.

        Args:
            labels: available label names to add to the combo box.
            label_name: the name of the label to set for the row
            duration: the duration to set for the row
        Learning Resources:
            Instead of setting widgets for each cell,
            a better way would be to use a delegate https://forum.qt.io/topic/88486/dropdown-in-qtablewdget
        """
        # create the elements to insert
        label_choice = QComboBox()
        label_duration = QSpinBox()
        label_choice.addItems(labels)
        label_duration.setMinimum(1)

        n_rows = self.table.rowCount()
        self.table.insertRow(n_rows)
        self.table.setRowHeight(n_rows, self.ROW_HEIGHT)

        self.table.setCellWidget(n_rows, 0, label_choice)
        self.table.setCellWidget(n_rows, 1, label_duration)

        # set the values if provided
        if label_name is not None:
            label_choice.setCurrentText(label_name)
        if duration is not None:
            label_duration.setValue(duration)

    def delete_row(self):
        selected_row = self.table.currentRow()
        self.table.removeRow(selected_row)

    def update_choices(self, labels):
        """
        Updates the labels on all the combo boxes.
        Assumes that all the chosen labels are present in the new labels.
        """
        n_rows = self.table.rowCount()
        for row in range(n_rows):
            chosen_label = self.table.cellWidget(row, 0).currentText()
            assert chosen_label in labels, f"A label {chosen_label} is chosen, " \
                                           f"but it is missing from the labels: {labels}"
            self.table.cellWidget(row, 0).clear()
            self.table.cellWidget(row, 0).addItems(labels)
            self.table.cellWidget(row, 0).setCurrentText(chosen_label)

    def check_in_use(self, label_name: str) -> bool:
        """
        Checks if a given label name has been chosen.
        """
        chosen_names = self.get_names_sequence()
        in_use = label_name in chosen_names
        if in_use:
            self.launch_popup(f"Label {label_name} is in use!")
        return in_use

    def get_names_sequence(self) -> List[str]:
        n_rows = self.table.rowCount()
        label_name_order = [self.table.cellWidget(row, 0).currentText() for row in range(n_rows)]
        return label_name_order

    def get_duration_sequence(self):
        n_rows = self.table.rowCount()
        duration = [self.table.cellWidget(row, 1).value() for row in range(n_rows)]
        return duration

    def launch_popup(self, text):
        self.msg.setText(text)
        x = self.msg.exec_()


class AnnotationPage(QWidget):

    def __init__(self):
        super().__init__()

        # Create a top-level layout
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        # create labels Tab
        self.labels = LabelsTab()
        self.timing = TimingTab()
        self.splitter = QSplitter(Qt.Vertical)
        self.splitter.addWidget(self.labels)
        self.splitter.addWidget(self.timing)
        self.main_layout.addWidget(self.splitter)

        self.add_pb = QPushButton("Add annotation to the experiment")
        self.edit_pb = QPushButton("Edit annotation")
        self.delete_pb = QPushButton("Delete annotation")
        self.main_layout.addWidget(self.add_pb)
        buttons_lo = QHBoxLayout()
        buttons_lo.addWidget(self.edit_pb)
        buttons_lo.addWidget(self.delete_pb)
        self.main_layout.addLayout(buttons_lo)
        self.edit_pb.hide()
        self.delete_pb.hide()

    def freeze(self):
        self.add_pb.hide()
        self.edit_pb.show()
        self.delete_pb.show()

        self.labels.setEnabled(False)
        self.timing.setEnabled(False)

    def unfreeze(self):
        self.add_pb.show()
        self.edit_pb.hide()
        self.delete_pb.hide()

        self.labels.setEnabled(True)
        self.timing.setEnabled(True)


class AnnotationTab(QWidget):

    def __init__(self):
        super().__init__()
        # Create a top-level layout
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self.annotations = {}
        self.add_annotation_pb = QPushButton("Add annotation")
        self.main_layout.addWidget(self.add_annotation_pb)

        self.pageCombo = None
        self.stackedLayout = None

        self.msg = InputError()

    def switchPage(self):
        """
        What to do when the annotation is changed.
        Change the stackedLayout based on the pageCombo currentIndex.
        """
        self.stackedLayout.setCurrentIndex(self.pageCombo.currentIndex())

    def initialize_annotation_list(self):
        switch_lo = QHBoxLayout()
        switch_lo.addWidget(QLabel("Available annotations:"))

        # Create and connect the combo box to switch between annotation type pages
        self.pageCombo = QComboBox()
        switch_lo.addWidget(self.pageCombo)

        # Create the stacked layout
        self.stackedLayout = QStackedLayout()

        # Add the combo box and the stacked layout to the top-level layout
        self.main_layout.addLayout(switch_lo)
        self.main_layout.addLayout(self.stackedLayout)

    def create_ap(self, annotation_name):
        """
        Creates an Annotation page and adds it to the Annotation tab
        """
        # add information about the annotations
        annotation = AnnotationPage()
        self.annotations[annotation_name] = annotation
        self.pageCombo.addItem(annotation_name)
        self.stackedLayout.addWidget(annotation)

        # set the added item active
        self.pageCombo.setCurrentText(annotation_name)
        self.switchPage()

    def get_annotation_name(self):
        annotation_name, ok = QInputDialog.getText(self, 'Enter annotation name',
                                                   'Try to choose meaningful names, '
                                                   'for example:\n"Light" to describe '
                                                   'whether the light was on or off;\n'
                                                   '"Drug" to set the time when you '
                                                   'added the drug;')
        if ok:
            # check that all the names are unique
            if annotation_name in self.annotations.keys():
                self.launch_popup("The annotation names must be unique!")
                annotation_name = None
            # check that the name is not empty
            if not annotation_name:
                self.launch_popup("The annotation name can not be empty!")
                annotation_name = None
        else:
            annotation_name = None
        return annotation_name

    def launch_popup(self, text):
        self.msg.setText(text)
        x = self.msg.exec_()


class AnnotationCheckboxes(QWidget):
    def __init__(self, annotation_name: str, label_names: List[str]):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.group = annotation_name
        self.group_label = QLabel(annotation_name)
        self.layout.addWidget(self.group_label)

        self.checkboxes = {}
        self.update_labels(label_names)

    def remove_unused(self, label_names: List[str]):
        for name in self.checkboxes.keys():
            if name not in label_names:
                child = self.layout.takeAt(self.checkboxes[name])
                self.checkboxes.pop(name)
                if child.widget():
                    child.widget().deleteLater()

    def add_new(self, label_names: List[str]):
        for name in label_names:
            if name not in self.checkboxes.keys():
                i_name = self.layout.count()
                self.checkboxes[name] = i_name
                self.layout.insertWidget(i_name, LabelCheckBox(self.group, name))

    def update_labels(self, label_names: List[str]):
        self.remove_unused(label_names)
        self.add_new(label_names)

    def get_checked_conditions(self):
        conditions = []
        for i_checkbox in self.checkboxes.values():
            checkbox = self.layout.itemAt(i_checkbox).widget()
            if checkbox.isChecked():
                conditions.append(checkbox.get_label_info())
        return conditions


class DataReaderWriterTab(QWidget):
    """
    Loads and saves volumes.
    """

    def __init__(self, napari_viewer):
        super().__init__()

        self.labels = {}
        self._napari = napari_viewer

        self.ROW_HEIGHT = 30
        # Create a top-level layout
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        # 1. Individual volumes
        self.v_info_pb = QPushButton("")
        self.v_info_pb.setIcon(self.style().standardIcon(getattr(QStyle, "SP_MessageBoxInformation")))
        self.v_info_pb.clicked.connect(self.how_to_volumes)
        v_label = QLabel("Volumes: ")
        self.volumes = QLineEdit()
        # Regex explanation :
        # this allows integers separated by , and slices : .
        # For example: 12, 34, 4:56 , 72  : 34 is a valid input
        # (although slice 72:34 is invalid, it will be filtered out later)
        # but this: 4, 5, 6:7 : 8 is invalid because of two consecutive ":"
        reg_ex = QRegExp(r"^ *(\d{1,}|\d{1,} *: *\d{1,})( *|, *\d{1,}|, *\d{1,} *: *\d{1,}| *)*$")
        input_validator = QRegExpValidator(reg_ex, self.volumes)
        self.volumes.setValidator(input_validator)

        volume_lo = QHBoxLayout()
        volume_lo.addWidget(v_label)
        volume_lo.addWidget(self.volumes)
        volume_lo.addWidget(self.v_info_pb)
        self.main_layout.addLayout(volume_lo)
        self.load_volumes_pb = QPushButton("Load")
        self.main_layout.addWidget(self.load_volumes_pb)
        self.main_layout.addWidget(horizontal_line())

        # 2. Annotation list
        self.annotations = {}
        condition_lo = QHBoxLayout()

        self.checkbox_lo = QVBoxLayout()
        self.checkboxes = []
        self.info_text = QLabel("Add time annotation to the experiment\nto see the options.")
        self.checkbox_lo.addWidget(self.info_text)
        self.checkbox_lo.addStretch(42)
        condition_lo.addLayout(self.checkbox_lo)

        buttons_lo = QVBoxLayout()
        logic_label = QLabel("Use logic: ")
        self.logic_box = QComboBox()
        self.logic_box.addItems(["or", "and"])
        self.find_volumes = QPushButton("Find volumes")
        self.volumes_label = QLabel("Volumes that satisfy the conditions:")
        self.volumes_info = QTextBrowser()
        self.load_conditions_pb = QPushButton("Load")

        buttons_lo.addWidget(logic_label)
        buttons_lo.addWidget(self.logic_box)
        buttons_lo.addWidget(self.find_volumes)
        buttons_lo.addWidget(self.volumes_label)
        buttons_lo.addWidget(self.volumes_info)
        buttons_lo.addWidget(self.load_conditions_pb)

        buttons_lo.addStretch(42)
        condition_lo.addLayout(buttons_lo)

        self.main_layout.addLayout(condition_lo)
        self.main_layout.addWidget(horizontal_line())

        # self.main_layout.addStretch(42)
        self.msg = InputError("Info")

    def launch_popup(self, text):
        self.msg.setText(text)
        x = self.msg.exec_()

    def update_labels(self, labels: dict):
        self.info_text.hide()
        # remove unused
        # use use list to force a copy of the keys to be made
        for annotation_name in list(self.annotations):
            if annotation_name not in labels:
                widget = self.annotations.pop(annotation_name)
                widget.setParent(None)
                widget.deleteLater()

        # add new
        for annotation_name, label_names in labels.items():
            if annotation_name not in self.annotations:
                self.annotations[annotation_name] = AnnotationCheckboxes(annotation_name, label_names)
                self.checkbox_lo.addWidget(self.annotations[annotation_name])
            else:
                self.annotations[annotation_name].update_labels(label_names)

    def how_to_volumes(self):
        text = "Enter the indeces for the volumes you would like to load.\nValid inputs are individual indexes, " \
               "separated by a comma:\n2, 4  , 6, (all spaces are ignored)\nor slices, to load volumes 9, 10, 11, " \
               "12 one can write:\n9:12 (Important! Volume number 12 WILL BE LOADED) \nAny combination of these two " \
               "inputs will work:\n2, 4, 6, 9:12, 19 (loads volumes 2, 4, 6, 9, 10, 11, 12 and 19 ) "
        self.launch_popup(text=text)

    def get_volumes(self):
        """
        Gets volumes from text.
        """
        requested_volumes = self.volumes.text()
        volumes = []
        for vol in requested_volumes.split(","):
            if ":" in vol:
                start, end = vol.split(":")
                assert start < end, f"The slice start {start} must be smaller than the end {end}"
                volumes.extend(range(int(start.strip()), (int(end.strip()) + 1)))
            else:
                volumes.append(int(vol.strip()))
        # TODO: check for repeats ?
        return volumes, requested_volumes


class VodexView(QWidget):
    """
    Does everything about the GUI View.
    """

    def __init__(self, viewer):
        super().__init__()

        self.nt = NewExperimentTab()
        self.lt = LoadExperimentTab()

        self.vt = VolumeTab()
        self.st = SaveTab()
        self.it = InitialiseTab()
        self.at = AnnotationTab()
        self.dt = DataReaderWriterTab(viewer)
        self.napari = viewer

        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self.nt_pb = QPushButton("Create New Experiment")
        self.lt_pb = QPushButton("Load Saved Experiment")
        self.main_layout.addWidget(self.lt_pb)
        self.main_layout.addWidget(self.nt_pb)

    def initialize_new_experiment(self):
        self.nt_pb.hide()
        self.lt_pb.hide()

        tabs = QTabWidget()
        # 1. New Experiment Tab
        # More on QSplitter:
        # https://www.tutorialspoint.com/pyqt/pyqt_qsplitter_widget.htm
        splitter_1 = QSplitter(Qt.Vertical)
        splitter_1.addWidget(self.nt)
        splitter_1.addWidget(self.vt)
        splitter_1.addWidget(self.it)
        tabs.addTab(splitter_1, "Image Data")
        self.it.hide()

        # 2. Time Annotation Tab
        tabs.addTab(self.at, "Time Annotation")

        # 3. Load/Save Tab
        splitter_3 = QSplitter(Qt.Vertical)
        splitter_3.addWidget(self.dt)
        splitter_3.addWidget(self.st)
        tabs.addTab(splitter_3, "Load/Save Data")

        self.main_layout.addWidget(tabs)

        # disable until called for the first time
        self.nt.list_widget.setEnabled(False)
        self.vt.setEnabled(False)
        self.st.setEnabled(False)

    def initialize_load_experiment(self):
        self.nt_pb.hide()
        self.lt_pb.hide()

        tabs = QTabWidget()

        # 2. Load Experiment Tab
        tabs.addTab(self.lt, "Image Data")

        # 2. Time Annotation Tab
        tabs.addTab(self.at, "Time Annotation")

        # 3. Load/Save Tab
        splitter_3 = QSplitter(Qt.Vertical)
        splitter_3.addWidget(self.dt)
        splitter_3.addWidget(self.st)
        tabs.addTab(splitter_3, "Load/Save Data")

        self.main_layout.addWidget(tabs)


class VodexModel:
    """
    Does everything on the vodex side.
    """

    def __init__(self):

        self.fm = None
        self.vm = None

        self.annotations = {}
        self.labels = {}
        self.cycles = {}
        self.timelines = {}

        self.experiment = None
        self.experiment_saved = False

    def crete_fm(self, data_dir, file_type, file_names=None):
        """
        Creates the FileManager.
        """
        self.fm = vx.FileManager(data_dir, file_type=file_type, file_names=file_names)

    def remove_fm(self):
        """
        Removes the FileManager.
        """
        self.annotations = {}

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

    def create_annotation(self, group: str, state_names: List[str], state_info: dict,
                          labels_order: List[str], duration: List[int], an_type: str):
        """
        Creates an annotation.

        Args:
            group: Group name ( the same as annotation name)
            state_names: a list of unique label names used to create the annotation
            state_info: description of the state_names
            labels_order: label names in the order as they follow in the annotation
            duration: duration of the labels in the order as they follow in the annotation
            an_type: whether annotation os created from Cycle or from Timeline
        """
        n_frames = self.vm.n_frames
        self.labels[group] = vx.Labels(group, state_names, state_info=state_info)
        label_order = [vx.TimeLabel(name, description=state_info[name], group=group) for name in labels_order]

        if an_type == 'Timeline':
            self.timelines[group] = vx.Timeline(label_order, duration)
            annotation = vx.Annotation.from_timeline(n_frames, self.labels[group], self.timelines[group], info=None)
        elif an_type == 'Cycle':
            self.cycles[group] = vx.Cycle(label_order, duration)
            annotation = vx.Annotation.from_cycle(n_frames, self.labels[group], self.cycles[group], info=None)
        else:
            annotation = None
        self.annotations[group] = annotation

        # add to the experiment
        self.experiment.add_annotations([annotation])

        # indicate that there are some unsaved changes
        self.experiment_saved = False

    def remove_annotation(self, group):
        """
        Removes an annotation from the experiment and from the model.
        """
        self.labels.pop(group)
        self.cycles.pop(group, None)
        self.timelines.pop(group, None)
        self.annotations.pop(group)

        # finally, remove from the experiment
        self.experiment.db.delete_annotation(group)
        # indicate that there are some unsaved changes
        self.experiment_saved = False

    def create_experiment(self):
        """
        Initialises the experiment from VolumeManager, no annotations added at this point.
        """
        # check that the vm is not empty ( no creating empty tables )
        self.experiment = vx.Experiment.create(self.vm, [])

    def remove_experiment(self):
        """
        Removes experiment from the model,
        also resets annotations, labels, cycles and timelines.
        Setting the model into the initial state.
        """

        self.annotations = {}
        self.labels = {}
        self.cycles = {}
        self.timelines = {}

        self.experiment = None
        self.experiment_saved = False

    def save_experiment(self, file_name: str):
        """
        Saves experiment to file.
        """
        self.experiment.save(file_name)
        self.experiment_saved = True

    def load_experiment(self, file_name: str):
        """
        Loads experiment to file.
        """
        # this makes sure annotations and all the managers
        # are already in experiment
        self.experiment = vx.Experiment.load(file_name)
        self.experiment_saved = True

        # populate the model to reflect the experiment
        db_exporter = vx.DbExporter(self.experiment.db)
        self.fm = db_exporter.reconstruct_file_manager()
        self.vm = db_exporter.reconstruct_volume_manager()
        self.load_annotation_info(db_exporter)

    def load_annotation_info(self, db_exporter):
        """
        Creates annotations, cycles, timelines and labels from the database records.
        """
        # get the names of all the available annotations from the db
        annotation_names = self.experiment.db.get_Names_from_AnnotationTypes()

        # get the total number of frames in the recording
        n_frames = self.vm.n_frames

        for group in annotation_names:
            # reconstruct Labels for the group
            labels = db_exporter.reconstruct_labels(group)
            self.labels[group] = labels

            # create the annotation based on the annotation type
            cycle = db_exporter.reconstruct_cycle(group)
            if cycle is not None:
                self.cycles[group] = cycle
                self.annotations[group] = vx.Annotation.from_cycle(n_frames, labels, cycle)
            else:
                timeline = db_exporter.reconstruct_timeline(group, labels)
                self.timelines[group] = timeline
                self.annotations[group] = vx.Annotation.from_timeline(n_frames, labels, timeline)

    def choose_volumes(self, conditions: Union[tuple, List[tuple]], logic: str):
        """
        Selects only full volumes that correspond to specified conditions;
        Uses "or" or "and" between the conditions depending on logic.
        To load the selected volumes, use load_volumes()

        Args:
            conditions: a list of conditions on the annotation labels
                in a form [(group, name),(group, name), ...] where group is a string for the annotation type
                and name is the name of the label of that annotation type. For example [('light', 'on'), ('shape','c')]
            logic: "and" or "or" , default is "and".
        Returns:
            list of volumes and list of frame ids that were chosen.
            Remember that frame numbers start at 1, but volumes start at 0.
        """
        volume_list = self.experiment.choose_volumes(conditions, logic)
        return volume_list

    def load_volumes(self, volumes: List[int]):
        """
        Loads volumes.
        """
        assert self.experiment is not None, "Error when loading volumes: " \
                                            "experiment is not initialized."
        volumes_img = self.experiment.load_volumes(volumes)
        return volumes_img

    def save_volumes(self, volumes_img: List[int]):
        pass


class VodexController:
    """
    Controller class for the GUI (following the MVC schema).
    """

    def __init__(self, model, view):

        self._model = model
        self._view = view

        self._connectDisplaySignalsAndSlots()
        self.msg = InputError(title="Error!")

    def launch_popup(self, text):
        self.msg.setText(text)
        x = self.msg.exec_()

    def initialize_fm(self):
        """
        Executed when [Get Files] button is pressed.
        Initialises FileManager with all the files retrieved from the data directory
        and adds the files to the list to inspect.
        """
        data_dir_str = self._view.nt.dir_location.text()
        if data_dir_str == "":
            self.launch_popup(f"Enter directory!")
        else:
            data_dir = Path(data_dir_str)
            # check that the location is a directory
            if data_dir.is_dir():
                try:
                    # create FileManager
                    file_type = self._view.nt.file_types.currentText()
                    self._model.crete_fm(data_dir, file_type)
                    # update list of files
                    self._view.nt.list_widget.fill_list(self._model.fm.file_names)
                    # freeze dir
                    self._view.nt.freeze_dir()
                    # unfreeze file list
                    self._view.nt.list_widget.setEnabled(True)
                except Exception as initialize_fm_exception:
                    self.launch_popup(str(initialize_fm_exception))
                    self._model.remove_fm()
                # # if file names are not empty
                # if self._model.fm is not None:
                #     # update list of files
                #     self._view.ft.list_widget.fill_list(self._model.fm.file_names)
                #     # freeze dir
                #     self._view.ft.freeze_dir()
                #     # unfreeze file list
                #     self._view.ft.list_widget.setEnabled(True)
            else:
                self.launch_popup(f"Directory {data_dir} does not exist!")

    def update_and_freeze_fm(self):
        """
        Executed when [Save File Order] button is pressed.
        Updates a FileManager with the edited files and freezes it.
        Unfreezes the volue manager step.
        """
        try:
            data_dir = self._view.nt.dir_location.text()
            file_type = self._view.nt.file_types.currentText()
            file_names = self._view.nt.list_widget.get_file_names()
            # if file names are empty
            if file_names:
                # create new FileManager from updated file list
                self._model.crete_fm(data_dir, file_type, file_names=file_names)
                # freeze files list
                self._view.nt.list_widget.freeze()
                # unfreeze vm
                self._view.vt.setEnabled(True)
                self._view.vt.unfreeze_vm()
            else:
                self.launch_popup("File names are empty!\n"
                                  "To repopulate the files, press Fetch files again!")

        except Exception as e:
            self.launch_popup(e)

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
            self._view.nt.list_widget.list_widget.clear()
            self._view.nt.list_widget.unfreeze()
        except Exception as e:
            self._view.error_dialog.showMessage(e)

    def initialize_vm(self):
        """
        Executed when [Save Volume Info] button is pressed.
        Initialises VolumeManager and outputs the recording summary to inspect.
        """

        # must save files before adding vm
        if self._view.nt.list_widget.list_widget.isEnabled():
            self._view.vt.volume_info_string.setText("Save changes to the files first!")
        else:
            # create new VolumeManager from updated file list
            fpv = self._view.vt.fpv.value()
            fgf = self._view.vt.fgf.value()
            try:
                self._model.create_vm(fpv, fgf)
                # freeze vm
                self._view.vt.freeze_vm()
                # update the volume info summary
                self._view.vt.volume_info_string.setText(str(self._model.vm))

                # show the info for the next step
                self._view.it.show()

            except Exception as vm_e:
                self.launch_popup(vm_e)

    def create_experiment(self):
        """
        Executed when [Create Experiment] button is pressed.
        Initialises Experiment and freezes the first tab.
        """
        if self._model.vm is None:
            self.launch_popup("Save volume information first!")
        else:
            self._model.create_experiment()

            # swap the button to edit
            self._view.it.create_experiment.hide()
            self._view.it.edit_experiment.show()
            self._view.it.next_step.show()

            # freeze all the first tab
            self._view.nt.setEnabled(False)
            self._view.vt.setEnabled(False)

            # allow to save ( on the Load/Save tab ):
            self._view.st.setEnabled(True)

    def edit_experiment(self):

        self._model.remove_experiment()

        # unfreeze all the first tab
        self._view.nt.setEnabled(True)
        self._view.vt.setEnabled(True)

        # swap the button to show
        self._view.it.create_experiment.show()
        self._view.it.edit_experiment.hide()
        self._view.it.next_step.hide()

    def remove_vm(self):
        """
        Executed when the [Change Directory] of [Edit Volume Info] button is pressed.
        Deletes existing VolumeManager and clears file list.
        """
        self._model.remove_vm()

        # remove the volume info summary
        self._view.vt.volume_info_string.setText("")

        # sets the volume info inputs to enabled

        # remove the save button:
        self._view.st.hide()

    def add_annotation(self, annotation_name):

        # get information to create annotation
        group = annotation_name
        state_names = self._view.at.annotations[annotation_name].labels.get_names()
        state_info = self._view.at.annotations[annotation_name].labels.get_descriptions()
        labels_order = self._view.at.annotations[annotation_name].timing.get_names_sequence()
        duration = self._view.at.annotations[annotation_name].timing.get_duration_sequence()
        an_type = self._view.at.annotations[annotation_name].timing.annotation_type.currentText()

        if an_type == "Timeline" and sum(duration) != self._model.vm.n_frames :
            self.launch_popup("The number of frames in a Timeline "
                              "must exactly match the total number of frames in the recording.")
        elif an_type == "Cycle" and sum(duration) > self._model.vm.n_frames :
            self.launch_popup("The number of frames in a Cycle "
                              "must be less or equal to the total number of frames in the recording.")
        else:
            # change the tab view
            self._view.at.annotations[annotation_name].freeze()

            # create annotation and add it to the experiment
            self._model.create_annotation(group, state_names, state_info, labels_order, duration, an_type)

            # update the Load/Save Tab
            self._view.dt.update_labels(self._get_label_names())


    def remove_annotation(self, annotation_name):
        # remove the tab from view
        self._view.at.annotations[annotation_name].setParent(None)
        self._view.at.annotations[annotation_name].deleteLater()
        self._view.at.pageCombo.removeItem(self._view.at.pageCombo.currentIndex())

        # remove annotation from model and from experiment
        self._model.remove_annotation(annotation_name)

        # update the Load/Save Tab
        self._view.dt.update_labels(self._get_label_names())

    def edit_annotation(self, annotation_name):
        # change the tab view
        self._view.at.annotations[annotation_name].unfreeze()

        # remove annotation from model and from experiment
        self._model.remove_annotation(annotation_name)

        # update the Load/Save Tab
        self._view.dt.update_labels(self._get_label_names())

    def initialize_at(self):
        """
        Executed when [Add annotation] button is pressed.
        Initialises the annotation tab.
        """
        if self._view.at.pageCombo is None:
            self._view.at.initialize_annotation_list()
            self._view.at.pageCombo.activated.connect(self._view.at.switchPage)

    def initialize_ap(self, annotation_name=None):
        """
        Executed when [Add annotation] button is pressed.
        Initialises the annotation page and adds it to the annotation tab.
        """
        if annotation_name is None:
            # check if the name is unique
            annotation_name = self._view.at.get_annotation_name()
        # create ap
        if annotation_name is not None:
            self._view.at.create_ap(annotation_name)
            self._connectAnnotationPageSignalsAndSlots(annotation_name)

    def save_experiment(self):
        """
        Executed when [Load volumes] button is pressed.
        Initialises the experiment.
        """
        # launch a pop-up that the db will be created and saved.
        file_name = self._view.st.get_save_filename()
        if file_name is not None:
            # attempt to save
            self._model.save_experiment(file_name)

    def load_volumes(self):
        """
        Executed when [Load volumes] is pressed.
        """
        # check that experiment has been saved:
        if self._model.experiment is not None:
            # get volume indeces
            volumes, requested_volumes = self._view.dt.get_volumes()
            # load images
            volumes_img = self._model.load_volumes(volumes)
            # finally add loaded data to napari viewer
            self._view.napari.add_image(volumes_img, name=requested_volumes)
        else:
            self.launch_popup("You must create the experiment to load the volumes.\n"
                              "See Image Data tab.")

    def load_volumes_for_conditions(self):
        """
        Executed when [Load volumes] is pressed.
        """
        # rerun the choosing part in case anything changed
        # TODO : make sure nothing can change from choosing to loading
        conditions, logic, volumes = self._find_volumes()
        if volumes:
            # construct the name
            name = f"_{logic}_".join(f"{condition[0]}-{condition[1]}" for condition in conditions)

            # load images
            volumes_img = self._model.load_volumes(volumes)
            # finally add loaded data to napari viewer
            self._view.napari.add_image(volumes_img, name=name)

    def load_experiment(self):
        # browse for the db
        self._view.lt.browse()
        db_name = self._view.lt.db_location.text()
        self._model.load_experiment(db_name)

        # update the info about the fm and vm
        self._view.lt.fm_info_string.setText(str(self._model.fm))
        self._view.lt.vm_info_string.setText(str(self._model.vm))
        self._view.lt.setEnabled(False)
        self._load_annotations()

    def _get_label_names(self):
        """
        Replaces Labels in the _model.labels to their names.
        Such that the resulting dictionary is annotation names as keys, label names as values.
        """
        label_names = {}
        for annotation_name, labels in self._model.labels.items():
            label_names[annotation_name] = labels.state_names
        return label_names

    def _load_annotations(self):
        """
        create the annotation tab and annotation pages and fill out
        """
        self.initialize_at()
        for annotation_name in self._model.annotations.keys():
            self.initialize_ap(annotation_name=annotation_name)
            self._load_labels(annotation_name)
            self._load_timing(annotation_name)

            self._view.at.annotations[annotation_name].freeze()

        # update the Load/Save Tab
        self._view.dt.update_labels(self._get_label_names())

    def _load_labels(self, annotation_name):
        # TODO: test with empty labels in the db ? Is it possible?
        labels = self._model.labels[annotation_name]
        for label in labels.states:
            self._view.at.annotations[annotation_name].labels.add_row(label_name=label.name,
                                                                      description=label.description)

    def _load_timing(self, annotation_name):
        labels = self._view.at.annotations[annotation_name].labels.label_names
        # decide if it's a cycle or a timeline
        if annotation_name in self._model.cycles.keys():
            self._view.at.annotations[annotation_name].timing.annotation_type.setCurrentText("Cycle")
            timing = self._model.cycles[annotation_name]
        elif annotation_name in self._model.timelines.keys():
            self._view.at.annotations[annotation_name].timing.annotation_type.setCurrentText("Timeline")
            timing = self._model.timelines[annotation_name]
        # fill out the table
        for label, duration in zip(timing.label_order, timing.duration):
            self._view.at.annotations[annotation_name].timing.add_row(labels,
                                                                      label_name=label.name,
                                                                      duration=duration)

    def _find_volumes(self):
        # collect conditions info
        conditions = []
        for annotation in self._view.dt.annotations.values():
            an_conditions = annotation.get_checked_conditions()
            if an_conditions:
                conditions.extend(annotation.get_checked_conditions())
        logic = self._view.dt.logic_box.currentText()

        # get volumes
        volumes_ids = self._model.experiment.choose_volumes(conditions, logic=logic)

        # print volumes to text field
        if volumes_ids:
            self._view.dt.volumes_info.setText(','.join(str(volume) for volume in volumes_ids))
        else:
            self._view.dt.volumes_info.setText("No full volumes satisfy the conditions.")

        return conditions, logic, volumes_ids

    def _connectAnnotationPageSignalsAndSlots(self, annotation_name):
        # 0. Connect tab controls
        # [Add annotation] button
        self._view.at.annotations[annotation_name].add_pb.clicked.connect(lambda:
                                                                          self.add_annotation(annotation_name))
        # [Delete annotation] button
        self._view.at.annotations[annotation_name].delete_pb.clicked.connect(lambda:
                                                                             self.remove_annotation(annotation_name))
        # [Edit annotation] button
        self._view.at.annotations[annotation_name].edit_pb.clicked.connect(lambda:
                                                                           self.edit_annotation(annotation_name))
        # 1. connect LabelsTab
        # [Add label] button:
        # add a new label and update the choices in conditions tab
        self._view.at.annotations[annotation_name].labels.add_label.clicked.connect(
            lambda: self._view.at.annotations[annotation_name].labels.add_row())
        self._view.at.annotations[annotation_name].labels.add_label.clicked.connect(
            lambda: self._view.at.annotations[annotation_name].timing.update_choices(
                self._view.at.annotations[annotation_name].labels.label_names
            ))
        # [Delete selected] button:
        # if selected label is not used in the conditions tab delete selected row from the table
        self._view.at.annotations[annotation_name].labels.delete_selected.clicked.connect(
            lambda: self._view.at.annotations[annotation_name].labels.delete_row(
                self._view.at.annotations[annotation_name].timing.check_in_use(
                    self._view.at.annotations[annotation_name].labels.get_selected_name()
                )))
        self._view.at.annotations[annotation_name].labels.delete_selected.clicked.connect(
            lambda: self._view.at.annotations[annotation_name].timing.update_choices(
                self._view.at.annotations[annotation_name].labels.label_names
            ))
        # 2. connect TimingTab
        self._view.at.annotations[annotation_name].timing.add_button.clicked.connect(
            lambda: self._view.at.annotations[annotation_name].timing.add_row(
                self._view.at.annotations[annotation_name].labels.get_names()))
        self._view.at.annotations[annotation_name].timing.del_button.clicked.connect(
            self._view.at.annotations[annotation_name].timing.delete_row)

    def _connectFirstTabSignalsAndSlots(self):
        # 1. connect FileTab
        # _______________________________________________________________________________________________
        # [Browse] button in New Experiment
        self._view.nt.browse_button.clicked.connect(self._view.nt.browse)
        # [Load] button in Load Experiment
        self._view.lt.load_db_pb.clicked.connect(self.load_experiment)

        # [Fetch files] button
        self._view.nt.files_button.clicked.connect(self.initialize_fm)

        # [Edit] button
        self._view.nt.edit_dir_button.clicked.connect(self.remove_fm)
        self._view.nt.edit_dir_button.clicked.connect(self._view.nt.unfreeze_dir)

        # [Delete File] button
        self._view.nt.list_widget.delete_button.clicked.connect(self._view.nt.list_widget.delete_file)

        # [Save File Order] button
        self._view.nt.list_widget.save_button.clicked.connect(self.update_and_freeze_fm)

        # [Edit Files] button
        self._view.nt.list_widget.edit_button.clicked.connect(self._view.nt.list_widget.unfreeze)
        self._view.nt.list_widget.edit_button.clicked.connect(self.remove_vm)

        # 2. connect VolumeTab
        # _______________________________________________________________________________________________
        # [Save Volume Info] button
        # update the volume info summary
        self._view.vt.volumes_button.clicked.connect(self.initialize_vm)

        # [Edit Volume Info] button
        self._view.vt.edit_vol_button.clicked.connect(self.remove_vm)
        self._view.vt.edit_vol_button.clicked.connect(self._view.vt.unfreeze_vm)

        # 3. connect InitialiseTab
        self._view.it.create_experiment.clicked.connect(self.create_experiment)
        self._view.it.edit_experiment.clicked.connect(self.edit_experiment)

    def _connectDisplaySignalsAndSlots(self):

        # 0. Connect intro Tab
        # _______________________________________________________________________________________________
        self._view.nt_pb.clicked.connect(self._view.initialize_new_experiment)
        self._view.lt_pb.clicked.connect(self._view.initialize_load_experiment)

        self._connectFirstTabSignalsAndSlots()

        # 3. connect SaveTab
        # _______________________________________________________________________________________________
        # [Save] button
        self._view.st.save_pb.clicked.connect(self.save_experiment)

        # 4. connect AnnotationTab
        # _______________________________________________________________________________________________
        # [Add Annotation] button
        self._view.at.add_annotation_pb.clicked.connect(self.initialize_at)
        # initialize_ap connects all the buttons for the individual pages
        self._view.at.add_annotation_pb.clicked.connect(lambda: self.initialize_ap())

        # 5. connect DataReaderWriterTab
        # _______________________________________________________________________________________________
        # [Load volumes] button
        self._view.dt.load_volumes_pb.clicked.connect(self.load_volumes)
        self._view.dt.find_volumes.clicked.connect(self._find_volumes)
        self._view.dt.load_conditions_pb.clicked.connect(self.load_volumes_for_conditions)


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

