# import numpy as np
# import pandas as pd
# import collections
# from napari_blob_detection.measure_blobs import measure_blobs
# from napari_blob_detection.utils import diam_to_napari
# from skimage.feature import blob_log, blob_dog
# from trackpy import locate
# from napari.types import LayerDataTuple
# from napari.layers import Image
from magicgui import magic_factory
from magicgui.widgets import Container
from superqt import QCollapsible

from enum import Enum
import vodex as vx
import pandas as pd
from pandas import DataFrame
from napari_vodex.utils import *


@magic_factory(call_button="show files",
               data_dir={'widget_type': 'FileEdit', 'mode': 'd',
                         'tooltip': 'The file with the annotation'},
               message={'widget_type': 'TextEdit',
                        'tooltip': 'Info about volumes.', 'label': 'info', 'visible': False},
               layout='vertical', persist=True
               )
def file_info(data_dir, message='') -> DataFrame:
    """Creates label groups"""
    pass


@magic_factory(call_button='show volumes',
               frames_per_volume={'tooltip': 'int, First good frame of a volume. In case the recording started '
                                             'mid-volume.'},
               start_frame={'tooltip': 'int,First good frame of a volume. In case the recording started mid-volume.'},
               message={'widget_type': 'TextEdit',
                        'tooltip': 'Info about volumes.', 'label': 'info', 'visible': False},
               layout='vertical', persist=True
               )
def volume_info(frames_per_volume=0, start_frame=0, message='') -> None:
    """Creates label groups"""
    pass


@magic_factory(call_button=False,
               show_labels={'widget_type': 'PushButton',
                            'tooltip': 'add another label field'},
               group_name={'widget_type': 'LineEdit',
                           'tooltip': 'The name of the group of labels, string'},
               message={'widget_type': 'TextEdit',
                        'tooltip': 'Info about volumes.', 'label': 'info', 'visible': False},
               label_ids={'widget_type': 'LiteralEvalLineEdit',
                          'tooltip': 'contains the labels', 'visible': False},
               layout='vertical', persist=True)
def label_group_info(
        show_labels, group_name='', message='', label_ids=[]) -> None:
    """Creates label groups"""
    pass


@magic_factory(call_button=False,
               add_label={'widget_type': 'PushButton', 'label': '+',
                          'tooltip': 'add another label field'},
               del_label={'widget_type': 'PushButton', 'label': '-',
                          'tooltip': 'add another label field'},
               layout='horizontal')
def label_controls(
        add_label, del_label) -> None:
    """Creates label groups"""
    pass


@magic_factory(call_button=False,
               label_name={'widget_type': 'LineEdit',
                           'tooltip': 'The name of the label in the group, string'},
               description={'widget_type': 'LineEdit',
                            'tooltip': 'Label description, string'},
               layout='horizontal')
def label_info(
        label_name='', description='') -> None:
    """Creates label groups"""
    pass


@magic_factory(call_button="show cycles",
               label_list={'widget_type': 'LineEdit',
                           'tooltip': 'labels, use the shortcuts'},
               duration={'widget_type': 'LineEdit',
                         'tooltip': 'Duration of the labels, in frames'},
               message={'widget_type': 'TextEdit',
                        'tooltip': 'Info about cycle.', 'label': 'info', 'visible': False},
               layout='vertical')
def cycle_info(
        label_list, duration, message='') -> None:
    """Creates label groups"""
    pass


@magic_factory(call_button="show timeline",
               label_list={'widget_type': 'LineEdit',
                           'tooltip': 'labels, use the shortcuts'},
               duration={'widget_type': 'LineEdit',
                         'tooltip': 'Duration of the labels, in frames'},
               message={'widget_type': 'TextEdit',
                        'tooltip': 'Info about timeline.', 'label': 'info', 'visible': False},
               layout='vertical')
def timeline_info(
        label_list, duration, message='') -> None:
    """Creates label groups"""
    pass


ANNOTATION_MAPPING = {"annotation_from_cycle": cycle_info,
                      "annotation_from_timeline": timeline_info}


class AnnotationTypes(Enum):
    """A set of valid arithmetic operations for image_arithmetic.
    To create nice dropdown menus with magicgui, it's best
    (but not required) to use Enums.  Here we make an Enum
    class for all of the image math operations we want to
    allow.
    """
    # dropdown options for detectors
    cycle = "annotation_from_cycle"
    timeline = "annotation_from_timeline"
    file = "annotation_from_file"


@magic_factory(auto_call=True,
               layout='horizontal')
def choose_annotation_type(annotation_type: AnnotationTypes):
    pass


@magic_factory(call_button=False,
               add_annotation={'widget_type': 'PushButton',
                               'tooltip': 'add another anotation field'},
               layout="horizontal")
def annotations(add_annotation) -> None:
    """Creates label groups"""
    pass


@magic_factory(call_button=False,
               label_list={'widget_type': 'LineEdit',
                           'tooltip': 'labels to load'},
               layout="horizontal")
def choose_from_annotation(label_list) -> None:
    """Creates label groups"""
    pass


@magic_factory(call_button="Load full volumes"
               )
def load_volumes() -> None:
    """Creates label groups"""
    pass


@magic_factory(call_button="Save experiment",
               save_dir={'widget_type': 'FileEdit', 'mode': 'd',
                         'tooltip': 'Where to save the experiment'},)
def save_experiment(save_dir) -> None:
    pass


def annotation_info():
    widget = Container()

    # add group description #####################################################
    group_widget = label_group_info()
    group_widget.label = ""
    group_widget.name = 'group_widget'
    widget.append(group_widget)
    widget.group_widget.parent_changed()

    label_controls_widget = label_controls()
    label_controls_widget.label = ""
    label_controls_widget.name = 'label_controls_widget'
    widget.append(label_controls_widget)
    widget.label_controls_widget.parent_changed()

    # create the starting point where to add labels
    label_ids = []

    @widget.label_controls_widget.add_label.clicked.connect
    def _add_label():
        if not label_ids:
            new_label = len(group_widget)
        else:
            new_label = label_ids[-1] + 1

        label_widget = label_info()
        label_widget.label = ""
        label_widget.name = f'label_widget{new_label}'

        group_widget.insert(new_label, label_widget)
        label_ids.append(new_label)
        group_widget.label_ids.value = label_ids
        label_widget.parent_changed()

    @widget.label_controls_widget.del_label.clicked.connect
    def _del_label():
        if len(label_ids) == 1:
            show_info("There has to be at least one label!")
        else:
            last_label = label_ids.pop()
            group_widget.pop(last_label)
            group_widget.label_ids.value = label_ids

    @widget.group_widget.show_labels.clicked.connect
    def _show_labels():
        lbs = get_labels(group_widget)
        group_widget.message.visible = True
        group_widget.message.value = str(lbs)

    _add_label()

    # add annotation #####################################################
    annotation_type_widget = choose_annotation_type()
    annotation_type_widget.label = ""
    annotation_type_widget.name = 'annotation_type_widget'
    widget.append(annotation_type_widget)
    widget.annotation_type_widget.parent_changed()

    annotation_widget = ANNOTATION_MAPPING[annotation_type_widget.annotation_type.value.value]
    annotation_widget = annotation_widget()
    # annotation_widget.call_button.visible = False
    annotation_widget.label = ""
    annotation_widget.name = 'annotation_widget'
    widget.append(annotation_widget)
    annotation_spot = widget.index(annotation_widget)
    widget.annotation_widget.parent_changed()

    @widget.annotation_widget.call_button.clicked.connect
    def _show_annotation():
        if annotation_type_widget.annotation_type.value == AnnotationTypes.timeline:
            timeline = get_timeline(group_widget, annotation_widget)
            annotation_widget.message.visible = True
            annotation_widget.message.value = str(timeline)
        elif annotation_type_widget.annotation_type.value == AnnotationTypes.cycle:
            cycle = get_cycle(group_widget, annotation_widget)
            annotation_widget.message.visible = True
            annotation_widget.message.value = str(cycle)

    @annotation_type_widget.annotation_type.changed.connect
    def update():
        # clean the current annotation
        if hasattr(widget, 'annotation_widget'):
            widget.remove('annotation_widget')
        annotation_widget = ANNOTATION_MAPPING[annotation_type_widget.annotation_type.value.value]
        annotation_widget = annotation_widget()
        # annotation_widget.call_button.visible = False
        annotation_widget.label = ""
        annotation_widget.name = 'annotation_widget'
        widget.insert(annotation_spot, annotation_widget)
        widget.annotation_widget.parent_changed()

        # show annotation #####################################################
        @widget.annotation_widget.call_button.clicked.connect
        def _show_annotation():
            if annotation_type_widget.annotation_type.value == AnnotationTypes.timeline:
                timeline = get_timeline(group_widget, annotation_widget)
                annotation_widget.message.visible = True
                annotation_widget.message.value = str(timeline)
            elif annotation_type_widget.annotation_type.value == AnnotationTypes.cycle:
                cycle = get_cycle(group_widget, annotation_widget)
                annotation_widget.message.visible = True
                annotation_widget.message.value = str(cycle)

    choose_from_widget = choose_from_annotation()
    choose_from_widget.label = ""
    choose_from_widget.name = 'choose_from_widget'
    widget.append(choose_from_widget)
    widget.choose_from_widget.parent_changed()

    return widget
