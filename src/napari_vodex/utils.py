import vodex as vx
from napari.utils.notifications import show_info


def get_file_manager(file_widget):
    data_dir = file_widget.data_dir.value
    fm = vx.FileManager(data_dir)
    return fm


def get_volume_manager(file_widget, volume_widget):
    data_dir = file_widget.data_dir.value
    fpv = volume_widget.frames_per_volume.value
    fgf = volume_widget.start_frame.value
    vm = vx.VolumeManager.from_dir(data_dir, fpv, fgf=fgf)
    return vm


def get_labels(group_widget):
    """
    labels: list of indices of label widgets
    """
    group_name = group_widget.group_name.value

    state_info = {group_widget[idx].label_name.value: group_widget[idx].description.value
                  for idx in group_widget.label_ids.value}
    state_names = state_info.keys()

    labels = vx.Labels(group_name, state_names, state_info=state_info)
    return labels


def get_label_order_and_duration(group_widget, annotation_widget):
    label_list = annotation_widget.label_list.value.split(',')
    labels = get_labels(group_widget)
    label_order = [getattr(labels, label_name.strip()) for label_name in label_list]

    duration_list = annotation_widget.duration.value.split(',')
    duration = [int(d) for d in duration_list]
    return label_order, duration


def get_timeline(group_widget, timeline_widget):
    """
    labels: list of indices of label widgets
    """
    label_order, duration = get_label_order_and_duration(group_widget, timeline_widget)
    timeline = vx.Timeline(label_order, duration)
    return timeline


def get_cycle(group_widget, cycle_widget):
    """
    labels: list of indices of label widgets
    """
    label_order, duration = get_label_order_and_duration(group_widget, cycle_widget)
    cycle = vx.Cycle(label_order, duration)
    return cycle


def get_annotations_list(n_frames, annotations_widget, annotations_ids):
    annotations = []
    for aid in annotations_ids:
        group_widget = annotations_widget[aid]['group_widget']
        annotation_type_widget = annotations_widget[aid]['annotation_type_widget']
        annotation_widget = annotations_widget[aid]['annotation_widget']
        labels = get_labels(group_widget)
        if annotation_type_widget.annotation_type.value.value == "annotation_from_cycle":
            cycle = get_cycle(group_widget, annotation_widget)
            annotations.append(vx.Annotation.from_cycle(n_frames, labels, cycle))
        elif annotation_type_widget.annotation_type.value.value == "annotation_from_timeline":
            timeline = get_timeline(group_widget, annotation_widget)
            annotations.append(vx.Annotation.from_timeline(n_frames, labels, timeline))
    return annotations


def get_experiment(file_widget, volume_widget, annotations_widget, annotations_ids):
    vm = get_volume_manager(file_widget, volume_widget)
    n_frames = vm.n_frames
    annotations = get_annotations_list(n_frames, annotations_widget, annotations_ids)
    experiment = vx.Experiment.create(vm, annotations)
    return experiment


def get_conditions_list(annotations_widget, annotations_ids):
    conditions = []
    for aid in annotations_ids:
        group_widget = annotations_widget[aid]['group_widget']
        choose_from_widget = annotations_widget[aid]['choose_from_widget']
        group_name = group_widget.group_name.value
        if choose_from_widget.label_list.value:
            print(choose_from_widget.label_list.value)
            label_list = [l.strip() for l in choose_from_widget.label_list.value.split(',')]
        else:
            label_list = []
        for l in label_list:
            conditions.append((group_name, l))
    return conditions


def load_volumes_from_file(file_widget, volume_widget, annotations_widget, annotations_ids):
    ex = get_experiment(file_widget, volume_widget, annotations_widget, annotations_ids)
    conditions = get_conditions_list(annotations_widget, annotations_ids)
    volumes = ex.choose_volumes(conditions)
    volumes_img = None
    if volumes:
        volumes_img = ex.load_volumes(volumes)
    return volumes_img, str(conditions)


def save_experiment_to_file(save_widget, file_widget, volume_widget,
                    annotations_widget, annotations_ids):
    ex = get_experiment(file_widget, volume_widget, annotations_widget, annotations_ids)
    save_file = save_widget.save_dir.value
    # TODO : do I need to close connection?
    ex.save(save_file)


