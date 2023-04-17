from typing import List
from typing import Union
import vodex as vx


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
        self.experiment.delete_annotations([group])
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
                timeline = db_exporter.reconstruct_timeline(group)
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

    def load_volumes(self, volumes: List[int], slices: List[int], load_head: bool, load_tail: bool):
        """
        Loads volumes.
        """
        assert self.experiment is not None, "Error when loading volumes: " \
                                            "experiment is not initialized."

        # if slices are empty, load all slices
        if not slices:
            slices = [s for s in range(self.vm.fpv)]

        # if volumes are empty, load all volumes
        if not volumes:
            volumes = []
            volumes.extend([s for s in range(self.vm.full_volumes)])

        # add head and tail volumes if needed
        if load_head and self.vm.n_head > 0:
            volumes.insert(0, -1)
        if load_tail and self.vm.n_tail > 0:
            volumes.append(-2)

        img = None
        try:
            img = self.experiment.load_slices(slices, volumes, skip_missing=False)
        except Exception as e:
            if str(e) == "Can't have different number of frames per volume!":
                raise ValueError("Uncheck Head or Tail or specify slices: " +
                                 "not all of the selected volumes have the same number of selected slices.")
            else:
                raise e

        return img
