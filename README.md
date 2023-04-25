Make arguments selectable on the command line

In a script, specify e.g.
```python
import argparse
import selector

parser = argparse.ArgumentParser()

dataset_train = arguments.add_arguments(parser, "dataset", data.Box)(
    split_partition="train"
)
dataset_val = arguments.add_arguments(parser, "dataset", data.Box)(
    split_partition="val"
)
activation_function = arguments.add_options_from_module(
    parser, "activation", torch.nn.modules.activation, torch.nn.Module
)
model = arguments.add_arguments(
    parser, "model", CMBClassifier
)(activation_function=activation_function)
```
automatically making arguments selectable as e.g.
```sh
python train.py --data_dir precomputed/ --split_file split.yaml --size 20 --threshold 0.2 --input_type image --activation ReLU --model_depth 8 --learning_rate 0.0003```
