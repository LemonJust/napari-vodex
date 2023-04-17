from typing import List
from pathlib import Path

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
    QLabel
)

import vodex as vx


# _______________________________________________________________________________
# Collapsable implementation can be also found
# https://stackoverflow.com/questions/52615115/how-to-create-collapsible-box-in-pyqt


def horizontal_line():
    line = QFrame()
    # line.setGeometry(QRect(60, 110, 751, 20))
    line.setFrameShape(QFrame.HLine)
    # line.setFrameShadow(QFrame.Sunken)
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
        # self.setTextFormat(Qt.RichText)
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
        self.fpv.setRange(1, 1000000000)  # if range is not set, the maximum is 100, which can be not enough,
        self.fgf.setRange(0, 1000000000)  # 100000000 is well within integer range, and hopefully is enough for anyone
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
        self.info_label = QLabel("[SAVE] Save experiment to a database file:")
        main_layout.addWidget(QLabel("____________________________________________________"))
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
        self.table.setHorizontalHeaderLabels(["Label name", "Duration (in frames!)"])
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
        label_duration.setRange(1, 1000000000)
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
        section1_title = QLabel("[LOAD OPTION 1] Load based on volumes/slices IDs")
        self.main_layout.addWidget(QLabel("____________________________________________________"))
        self.main_layout.addWidget(section1_title)

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

        #    slice input
        #    TODO: add check if the slices are valid for the current dataset (use Signals?) (low priority)
        self.s_info_pb = QPushButton("")
        self.s_info_pb.setIcon(self.style().standardIcon(getattr(QStyle, "SP_MessageBoxInformation")))
        self.s_info_pb.clicked.connect(self.how_to_slices)
        s_label = QLabel("Slices: ")
        self.slices = QLineEdit()
        self.slices.setValidator(input_validator)

        volume_lo = QHBoxLayout()
        volume_lo.addWidget(v_label)
        volume_lo.addWidget(self.volumes)
        volume_lo.addWidget(self.v_info_pb)
        slice_lo = QHBoxLayout()
        slice_lo.addWidget(s_label)
        slice_lo.addWidget(self.slices)
        slice_lo.addWidget(self.s_info_pb)
        volume_slice_lo = QVBoxLayout()
        volume_slice_lo.addLayout(volume_lo)
        volume_slice_lo.addLayout(slice_lo)

        # 2 checkboxes whether to consider the head and the tail of the dataset
        self.head_cb = QCheckBox("Head")
        self.tail_cb = QCheckBox("Tail")
        head_tail_lo = QVBoxLayout()
        head_tail_lo.addWidget(self.head_cb)
        head_tail_lo.addWidget(self.tail_cb)

        volume_slice_checkbox_lo = QHBoxLayout()
        volume_slice_checkbox_lo.addLayout(volume_slice_lo)
        volume_slice_checkbox_lo.addLayout(head_tail_lo)

        self.main_layout.addLayout(volume_slice_checkbox_lo)
        self.load_volumes_pb = QPushButton("Load")
        self.main_layout.addWidget(self.load_volumes_pb)
        self.main_layout.addWidget(horizontal_line())

        # 2. Annotation list
        self.main_layout.addWidget(QLabel("____________________________________________________"))
        section2_title = QLabel("[LOAD OPTION 2] Load based on experimental conditions")
        self.a_info_pb = QPushButton("")
        self.a_info_pb.setIcon(self.style().standardIcon(getattr(QStyle, "SP_MessageBoxInformation")))
        self.a_info_pb.clicked.connect(self.how_to_annotations)
        intro_lo = QHBoxLayout()
        intro_lo.addWidget(section2_title)
        intro_lo.addWidget(self.a_info_pb)
        self.main_layout.addLayout(intro_lo)

        self.annotations = {}

        self.checkbox_lo = QHBoxLayout()
        self.checkboxes = []
        self.info_text = QLabel("Add time annotation to the experiment\nto see the options.")
        self.checkbox_lo.addWidget(self.info_text)

        self.main_layout.addLayout(self.checkbox_lo)

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

        self.main_layout.addLayout(buttons_lo)
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
        text = "Enter the indices for the volumes you would like to load. " \
               "Valid inputs include individual indices, comma-separated lists, or ranges using a colon. " \
               "Spaces are ignored. The volumes are loaded in ascending order. For example:\n" \
               "• Individual indices: 0, 4, 6\n" \
               "• Ranges: 9:12 (note that volume 12 will be loaded)\n" \
               "• Combined inputs: 2, 4, 6, 9:12, 19 (loads volumes 2, 4, 6, 9, 10, 11, 12, and 19)\n" \
               "Use the examples shown to specify the desired volumes to load.\n\n" \
               "If slices to load are specified, you can leave the volumes empty. " \
               "Then the specified slices will be loaded for all volumes.\n\n" \
               "If the dataset has unfilled volumes at the beginning or end of the recording, " \
               "you can include/exclude them by checking the Head and Tail checkboxes. " \
               "This might be important if you are trying to load a set of slices that " \
               "are not present in the Head or Tail of the dataset."

        self.launch_popup(text=text)

    def how_to_slices(self):
        text = "Enter the indices for the slices you would like to load. " \
               "Valid inputs include individual slices, " \
               "comma-separated, or ranges using a colon. Spaces are ignored. " \
               "ORDER IS IGNORED ( loaded in ascending order! ) " \
               "For example:\n" \
               "• Individual slices: 0, 2, 5\n" \
               "• Ranges: 0:5 (note that volume 5 WILL BE LOADED)\n" \
               "• Combined inputs: 0, 2, 5:7, 9 (loads slices 0, 2, 5, 6, 7, 9)\n" \
               "Use the format shown in the examples to specify the desired slices to load.\n\n" \
               "If slices to volumes are specified, you can leave the slices empty. " \
               "Then all the slices will be loaded for the specified volumes.\n\n" \
               "If the dataset has unfilled volumes at the beginning or end of the recording, " \
               "you can include/exclude them by checking the Head and Tail checkboxes." \
               "This might be important if you are trying to load a set of slices that " \
               "are not present in the Head or Tail of the dataset."

        self.launch_popup(text=text)

    def how_to_annotations(self):
        text = "If you have added time annotations to the experiment, you will see the annotation's names and labels. " \
               "Check the checkboxes by the labels for which you want to get the volumes, " \
               "and choose how to combine them with a logical OR or a logical AND. " \
               "Then, click the 'Find volumes' button to get a list of volume IDs that " \
               "correspond to the chosen conditions or 'Load' to load all such volumes into napari.\n\n" \
               "When you are choosing 'OR', all the conditions you picked will be combined with a logical OR." \
               " This means that vodex will pick volumes with slices that correspond " \
               "to at least one of the conditions " \
               "that you picked. It does not mean that the whole volume corresponds to one of the conditions. " \
               "Half of the slices in the volume can correspond to one condition and the other half to another.\n\n" \
               "When you are choosing 'AND', vodex will pick volumes with slices that correspond to all the " \
               "conditions that you picked at the same time. If at least one slice in a volume does not correspond" \
               " to all the conditions, such volume will not be picked."

        self.launch_popup(text=text)

    def get_volumes(self):
        """
        Gets volumes from text.
        """
        requested_volumes = self.volumes.text()
        volumes = []
        if requested_volumes:
            for vol in requested_volumes.split(","):
                if ":" in vol:
                    start, end = vol.split(":")
                    assert start < end, f"The slice start {start} must be smaller than the end {end}"
                    volumes.extend(range(int(start.strip()), (int(end.strip()) + 1)))
                else:
                    volumes.append(int(vol.strip()))
            # TODO: check for repeats ?
        return volumes, requested_volumes

    def get_slices(self):
        """
        Gets slices from text.
        """
        requested_slices = self.slices.text()
        slices = []
        if requested_slices:
            for sl in requested_slices.split(","):
                if ":" in sl:
                    start, end = sl.split(":")
                    assert start < end, f"The slice start {start} must be smaller than the end {end}"
                    slices.extend(range(int(start.strip()), (int(end.strip()) + 1)))
                else:
                    slices.append(int(sl.strip()))
        return slices, requested_slices


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
        # self.it.hide()

        # 2. Time Annotation Tab
        tabs.addTab(self.at, "Time Annotation")

        # 3. Load/Save Tab
        splitter_3 = QSplitter(Qt.Vertical)
        splitter_3.addWidget(self.dt)
        splitter_3.addWidget(self.st)
        tabs.addTab(splitter_3, "Load/Save Data")

        self.main_layout.addWidget(tabs, alignment=Qt.AlignTop)

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
