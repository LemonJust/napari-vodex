from pathlib import Path
from ._view import InputError


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

            # disable/enable checkboxes if there are no head or tail frames
            if self._model.vm.n_head == 0:
                self._view.dt.head_cb.setEnabled(False)
            else:
                self._view.dt.head_cb.setEnabled(True)

            if self._model.vm.n_tail == 0:
                self._view.dt.tail_cb.setEnabled(False)
            else:
                self._view.dt.tail_cb.setEnabled(True)

    def edit_experiment(self):

        # switch all annotations into "in edit" mode
        for annotation in list(self._model.annotations.keys()):
            self.edit_annotation(annotation)

        # remove experiment
        self._model.remove_experiment()

        # unfreeze all the first tab
        self._view.nt.setEnabled(True)
        self._view.vt.setEnabled(True)

        # swap the button to show on the first tab
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
        if self._model.experiment is None:
            self.launch_popup("Create Experiment First!")
        else:
            # get information to create annotation
            group = annotation_name
            state_names = self._view.at.annotations[annotation_name].labels.get_names()
            state_info = self._view.at.annotations[annotation_name].labels.get_descriptions()
            labels_order = self._view.at.annotations[annotation_name].timing.get_names_sequence()
            duration = self._view.at.annotations[annotation_name].timing.get_duration_sequence()
            an_type = self._view.at.annotations[annotation_name].timing.annotation_type.currentText()

            if an_type == "Timeline" and sum(duration) != self._model.vm.n_frames:
                self.launch_popup("The number of frames in a Timeline "
                                  "must exactly match the total number of frames in the recording.")
            elif an_type == "Cycle" and sum(duration) > self._model.vm.n_frames:
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
        if self._model.experiment is None:
            self.launch_popup("Create Experiment first!")
        else:
            if self._view.at.pageCombo is None:
                self._view.at.initialize_annotation_list()
                self._view.at.pageCombo.activated.connect(self._view.at.switchPage)

    def initialize_ap(self, annotation_name=None):
        """
        Executed when [Add annotation] button is pressed.
        Initialises the annotation page and adds it to the annotation tab.
        """
        if self._model.experiment is not None:
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

            # get volume and slices indeces
            volumes, requested_volumes = self._view.dt.get_volumes()
            slices, requested_slices = self._view.dt.get_slices()

            load_head = self._view.dt.head_cb.isChecked()
            load_tail = self._view.dt.tail_cb.isChecked()

            name = ""
            if not requested_slices == "":
                name = "[S " + requested_slices + "] "

            if requested_volumes == "":
                requested_volumes = "All"

            if load_head:
                requested_volumes += " (head)"
            else:
                requested_volumes += " (no head)"

            if load_tail:
                requested_volumes += " (tail)"
            else:
                requested_volumes += " (no tail)"

            name += "[V " + requested_volumes + "]"

            if volumes or slices:
                # load images
                volumes_img = self._model.load_volumes(volumes, slices, load_head, load_tail)
                # finally add loaded data to napari viewer
                self._view.napari.add_image(volumes_img, name=name)
            else:
                self.launch_popup("Enter the IDs of volumes or slices to load!")

        else:
            self.launch_popup("You must create the experiment to load the volumes.\n"
                              "See Image Data tab.")

    def load_volumes_for_conditions(self):
        """
        Executed when [Load volumes] is pressed.
        """
        # rerun the choosing part in case anything changed
        # TODO : make sure nothing can change from choosing to loading
        search_results = self._find_volumes()
        # will be none if experiment is not defined or no annotations added
        if search_results is not None:
            conditions, logic, volumes = search_results
            if volumes:
                # construct the name
                name = f"_{logic}_".join(f"{condition[0]}-{condition[1]}" for condition in conditions)

                # load images
                volumes_img = self._model.load_volumes(volumes, [], False, False)
                # finally add loaded data to napari viewer
                self._view.napari.add_image(volumes_img, name=name)

    def load_experiment(self):
        # browse for the db
        self._view.lt.browse()
        db_name = self._view.lt.db_location.text()
        if db_name != "":
            self._model.load_experiment(db_name)

            # update the info about the fm and vm
            self._view.lt.fm_info_string.setText(str(self._model.fm))
            self._view.lt.vm_info_string.setText(str(self._model.vm))
            self._view.lt.setEnabled(False)
            self._load_annotations()

            # disable/enable checkboxes if there are no head or tail frames
            if self._model.vm.n_head == 0:
                # uncheck
                self._view.dt.head_cb.setChecked(False)
                self._view.dt.head_cb.setEnabled(False)
            else:
                self._view.dt.head_cb.setChecked(True)
                self._view.dt.head_cb.setEnabled(True)

            if self._model.vm.n_tail == 0:
                self._view.dt.tail_cb.setChecked(False)
                self._view.dt.tail_cb.setEnabled(False)
            else:
                self._view.dt.tail_cb.setChecked(True)
                self._view.dt.tail_cb.setEnabled(True)

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
        if self._model.experiment is None:
            self.launch_popup("Create Experiment First!")
            return
        elif not self._model.annotations:
            self.launch_popup("Add an Annotation to Experiment First!")
            return
        else:
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
