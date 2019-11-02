import json
import shutil
from pathlib import Path


def extract_from_annotations_file(annotations_file_path, folder, wanted_categories_id,
                                  destination_images, destination_annotation):
    print(annotations_file_path)
    print(folder)
    with open(annotations_file_path, 'r') as annotations_file:
        data = json.load(annotations_file)
        new_data = {'images': [], "annotations": [],  "categories": []}

        useful_images_to_labels = {}
        for annotation in data['annotations']:
            if annotation['category_id'] in wanted_categories_id:
                image_id = annotation['id']
                if image_id not in useful_images_to_labels:
                    useful_images_to_labels[image_id] = []
                useful_images_to_labels[image_id].append(annotation)

        image_id_to_image_file_name = {}
        image_id_to_image_info = {}
        for image in data['images']:
            image_id_to_image_file_name[image['id']] = image['file_name']
            image_id_to_image_info[image['id']] = image

        print(len(image_id_to_image_file_name))

        for image_id, annotation in useful_images_to_labels.items():
            print(image_id)
            print(image_id_to_image_file_name[image_id])
            print(folder / image_id_to_image_file_name[image_id])
            print(destination_images / image_id_to_image_info[image_id]['file_name'])
            shutil.move(folder / image_id_to_image_file_name[image_id],
                        destination_images / image_id_to_image_info[image_id]['file_name'])
            new_data['images'].append(image_id_to_image_info[image_id])
            new_data['annotations'].append(useful_images_to_labels[image_id])

        for category in data['categories']:
            if category['id'] in wanted_categories_id:
                new_data['categories'].append(category)

        with open(destination_annotation, 'w') as outfile:
            json.dump(new_data, outfile)


# path = sys.argv[1]
path = Path('C:\\Users\\Andrei Popovici\\Desktop\\COCO')
destination = Path('C:\\Users\\Andrei Popovici\\Desktop\\COCO_new')

wanted_categories_id = [1, 2]

train_annotations_path = path / 'annotations' / 'instances_train2017.json'
train_folder_path = path / 'train2017'
train_annotations_path_destionation = destination / 'annotations' / 'instances_train2017.json'
train_folder_path_destination = destination / 'train2017'
extract_from_annotations_file(train_annotations_path, train_folder_path, wanted_categories_id,
                              train_annotations_path_destionation, train_folder_path_destination)

val_annotations_path = path / 'annotations' / 'instances_val2017.json'
val_folder_path = path / 'val2017'
val_annotations_path_destionation = destination / 'annotations' / 'instances_train2017.json'
val_folder_path_destination = destination / 'train2017'
extract_from_annotations_file(val_annotations_path, val_folder_path, wanted_categories_id,
                              val_annotations_path_destionation, val_folder_path_destination)
