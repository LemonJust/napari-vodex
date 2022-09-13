"""
This module is an example of a barebones QWidget plugin for napari

It implements the Widget specification.
see: https://napari.org/plugins/stable/guides.html#widgets

Replace code below according to your needs.
"""
from napari.utils.notifications import show_info
from magicgui import magic_factory
from napari import Viewer

from napari_vodex.utils import *
from napari_vodex.widgets import *

ANNOTATION_MAPPING = {"annotation_from_cycle": cycle_info,
                      "annotation_from_timeline": timeline_info}


def main_init(widget):
    widget.call_button.visible = False

    # add files description #####################################################
    file_widget = file_info()
    file_widget.label = ""
    file_widget.name = 'file_widget'
    widget.append(file_widget)
    widget.file_widget.parent_changed()

    @widget.file_widget.call_button.clicked.connect
    def _show_files():
        fm = get_file_manager(file_widget)
        # df = pd.DataFrame({"File Names": fm.file_names, "N Frames": fm.num_frames})
        file_widget.message.visible = True
        file_widget.message.value = str(fm)

    # add volume description #####################################################
    volume_widget = volume_info()
    volume_widget.label = ""
    volume_widget.name = 'volume_widget'
    widget.append(volume_widget)
    widget.volume_widget.parent_changed()

    @widget.volume_widget.call_button.clicked.connect
    def _show_volumes():
        vm = get_volume_manager(file_widget, volume_widget)
        volume_widget.message.visible = True
        volume_widget.message.value = str(vm)

    # add annotation ###############################################################
    annotations_widget = annotations()
    annotations_widget.label = ""
    annotations_widget.name = 'annotations_widget'
    widget.append(annotations_widget)
    widget.annotations_widget.parent_changed()

    # create the starting point where to add annotations
    annotations_ids = []

    @widget.annotations_widget.add_annotation.clicked.connect
    def _add_annotation():
        if not annotations_ids:
            new_annotation = len(annotations_widget)
            annotations_ids.append(new_annotation)
            # add load button ##################################################
            load_widget = load_volumes()
            load_widget.label = ""
            load_widget.name = 'load_widget'
            widget.append(load_widget)
            widget.load_widget.parent_changed()

            @widget.load_widget.call_button.clicked.connect
            def _make_experiment_and_load():
                volumes, volume_group = load_volumes_from_file(file_widget, volume_widget, annotations_widget,
                                                               annotations_ids)
                if volumes is None:
                    show_info("No full volumes satisfy the conditions")
                else:
                    widget.viewer.value.add_image(volumes, name=volume_group)

            # add load button ##################################################
            save_widget = save_experiment()
            save_widget.label = ""
            save_widget.name = 'save_widget'
            widget.append(save_widget)
            widget.save_widget.parent_changed()

            @widget.save_widget.call_button.clicked.connect
            def _save_experiment():
                save_experiment_to_file(save_widget, file_widget, volume_widget,
                                annotations_widget,annotations_ids)
                show_info(f"Experiment saved at {save_widget.save_dir.value}")

        else:
            new_annotation = annotations_ids[-1] + 1
            annotations_ids.append(new_annotation)
        annotation_widget = annotation_info()
        annotation_widget.label = ""
        annotation_widget.name = 'annotation_widget'
        annotations_widget.insert(new_annotation, annotation_widget)
        annotations_widget.annotation_widget.parent_changed()


@magic_factory(widget_init=main_init)
def new_experiment(viewer: Viewer):
    pass


# TODO : load experiment is just a placeholder for now ...
@magic_factory(call_button=False,
               message={'widget_type': 'TextEdit',
                        'tooltip': 'Info about volumes.', 'label': 'info',
                        'value':'Loading an experiment is not implemented yet, sorry. Coming soon!'})
def load_experiment(message):
    pass
