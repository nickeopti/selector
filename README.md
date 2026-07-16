_Easily make experiments configurable on the command line._

`selector` makes even complex experimental setups configurable on the command line, making it easy to test and compare different designs.

You define functions and classes with typed `__init__` methods; `selector` turns everything into CLI arguments, from class selection to parameter specification, so you can compare designs without maintaining argparse boilerplate.

Consider a project where different generative architectures are to be compared.
One module defines different methodologies to compare, e.g. `models.py` containing
```python
class GenerativeModel(nn.Module):
    pass


class DiffusionModel(GenerativeModel):
    def __init__(
        self,
        timesteps: int,
        beta_start: float,
        beta_end: float,
    ): ...


class ScoreBasedModel(GenerativeModel):
    def __init__(
        self,
        num_noise_levels: int,
        sigma_min: float,
        sigma_max: float,
    ): ...


class FlowMatchingModel(GenerativeModel):
    def __init__(
        self,
        ode_steps: int,
        time_emb_dim: int,
    ): ...
```
Manually making model choice and all of their respective parameters selectable on the command line is tedious and prone to falling out of sync when definitions change. With `selector` it is as easy as
```python
import argparse
import selector
import models

parser = argparse.ArgumentParser()

model = selector.add_options_from_module(
    parser,
    'model',
    models,
    of_subclass=models.GenerativeModel,
)()
```
With this, experiments can be run with e.g.
```sh
python main.py \
    --model ScoreBasedModel \
    --num_noise_levels 10 \
    --sigma_min 1e-4 \
    --sigma_max 1e-2
```
All the defined models are automatically selectable with `--model`, and all the selected class's parameters become available as further arguments. Diffusion gets `--timesteps`, flow matching gets `--ode_steps`, and so on. No manual `if model == ...` blocks.

Adding any extra parameters to the models? Automatically added as command-line arguments. Changing default values? New defaults automatically used when omitted. Nothing extra to maintain. Just define what you need, the rest is handled.

Say you want to also experiment with the new _drifting models_; simply add their definition
```python
class DriftingModel(GenerativeModel):
    def __init__(
        self,
        temperature: float,
        num_positive_samples: int,
        num_negative_samples: int,
    ): ...
```
and `--model DriftingModel` is immediately available, along with all its parameters.

Next, parametrise the models by a backbone network, defined externally for code reuse and better separation of concerns.
Simply let the models take a backbone as parameters, exemplified by
```python
class FlowMatchingModel(GenerativeModel):
    def __init__(
        self,
        backbone: Backbone,
        ode_steps: int,
        time_emb_dim: int,
    ): ...
```
with
```python
class Backbone(nn.Module):
    pass


class UNet(Backbone):
    def __init__(
        self,
        image_size: int,
        in_channels: int,
        depth: int,
        base_channels: int,
    ): ...


class ConvNet(Backbone):
    def __init__(
        self,
        image_size: int,
        in_channels: int,
        depth: int,
        kernel_size: int,
    ): ...
```

Now the full stack can be configured as simply as
```python
backbone = selector.add_options_from_module(
    parser,
    'backbone',
    models,
    of_subclass=models.Backbone,
)()

model = selector.add_options_from_module(
    parser,
    'model',
    models,
    of_subclass=models.GenerativeModel,
)(
    backbone=backbone,
)
```
allowing configuring e.g.
```sh
python main.py \
    --backbone UNet \
    --image_size 256 --in_channels 3 --depth 4 --base_channels 64 \
    --model DriftingModel \
    --temperature 0.1 --num_positive_samples 64 --num_negative_samples 64
```
and similarly for any of the other possible configurations;
all automatically made available on the command line
for easy experimentation, comparisons, and reproductions.

> Note that `selector.add_options_from_module` returns a `functools.partial` pre-filled with the options specified on the CLI. This means values can be overridden at invocation (inside the parentheses), which allows for wiring together complex configured objects, such as passing a configured `backbone` into a model.


To explore different activation functions,
parametrise the backbone as e.g.
```python
class UNet(Backbone):
    def __init__(
        self,
        image_size: int,
        in_channels: int,
        depth: int,
        base_channels: int,
        activation_function: nn.Module,
    ): ...
```
and simply make activation function choice available by
```python
import torch.nn.modules.activation

activation_function = selector.add_options_from_module(
    parser,
    'activation_function',
    torch.nn.modules.activation,
    of_subclass=nn.Module,
)()
```
which makes all `torch`'s activation functions selectable, ready to be passed into the backbone
```python
backbone = selector.add_options_from_module(
    parser,
    'backbone',
    models,
    of_subclass=models.Backbone,
)(
    activation_function=activation_function,
)
```

In the same way datasets can just as easily be made configurable on the command line. A dataset class such as
```python
class ImageDataset(torch.utils.data.Dataset):
    def __init__(
        self,
        root_dir: str,
        image_size: int,
        augment: bool = False,
        crop_size: int = 256,
    ): ...
```
can be made configurable on the command line simply by constructing it with
```python
dataset = selector.add_arguments(parser, 'dataset', ImageDataset)()
```
in the training setup. Same goes for data loaders with
```python
dataloader = selector.add_arguments(parser, 'dataloader', torch.utils.data.DataLoader)(dataset=dataset)
```
making everything from `batch_size` and `shuffle` to `num_workers` and `pin_memory` selectable on the command line.

The full example, with fully configurable generative model choice, backbone choice, activation function, data location, and data loader settings is as simple as
```python
import argparse

import selector

import torch.utils.data
import torch.nn.modules.activation
import torch.nn as nn

import models


parser = argparse.ArgumentParser()

activation_function = selector.add_options_from_module(
    parser,
    'activation_function',
    torch.nn.modules.activation,
    of_subclass=nn.Module,
)()

backbone = selector.add_options_from_module(
    parser,
    'backbone',
    models,
    of_subclass=models.Backbone,
)(
    activation_function=activation_function,
)

model = selector.add_options_from_module(
    parser,
    'model',
    models,
    of_subclass=models.GenerativeModel,
)(
    backbone=backbone,
)

dataset = selector.add_arguments(parser, 'dataset', ImageDataset)()
dataloader = selector.add_arguments(parser, 'dataloader', torch.utils.data.DataLoader)(dataset=dataset)
```

## Installation
To get started, install `selector` with
```sh
pip install git+https://github.com/nickeopti/selector.git
```
or add
```
"selector@git+https://github.com/nickeopti/selector",
```
to your `pyproject.toml` dependencies list.


## API Reference
The above example extensively used `add_options_from_module`. A few other convenient functions are also available.

### `get_argument`
```python
def get_argument(
    argument_parser: ArgumentParser,
    name: str,
    type: Type[T],
    default: T | None = None,
    *,
    args: Sequence[str] | None = None,
) -> T: ...
```
allows for quickly obtaining a single value, nicely typed. E.g.
```python
n_experiments = selector.get_argument(parser, 'n_experiments', int, default=5)
```
makes a single parameter selectable on the command line, and returns a properly typed result.

### `add_arguments`
```python
def add_arguments(
    argument_parser: ArgumentParser, name: str, reference: Type[T] | Callable, *, args: Sequence[str] | None = None
) -> partial[T]: ...
```
makes the parameters of a function or a class's `__init__` method available on the command line. This function is the main building block of `selector`. It is useful on its own, e.g. to make a specific class configurable on the command line
```python
network = selector.add_arguments(parser, 'network', UNet)()
```
or
```python
def main(n_experiments: int, n_iterations: int, log_dir: str):
    ...

if __name__ == '__main__':
    selector.add_arguments(parser, 'main', main)()
```
useful for making scripts automatically configurable on the command line.

### `add_options`
```python
def add_options(
    argument_parser: ArgumentParser, name: str, options: Sequence[Type[T]], *, args: Sequence[str] | None = None
) -> partial[T]: ...
```
is a convenient tool for choosing between a set of options, each configurable as in `add_arguments`. Useful for fixed choices
```python
backbone = selector.add_options(parser, 'backbone', (UNet, ConvNet))()
```

### `add_options_from_module`
```python
def add_options_from_module(
    argument_parser: ArgumentParser,
    name: str,
    module: ModuleType,
    of_subclass: Type[T],
    *,
    args: Sequence[str] | None = None,
) -> partial[T]: ...
```
automatically discovers and adds all classes in the given module which are subclasses of `of_subclass`, as shown in the running example above.

> All functions take an optional keyword-only `args` argument. If specified, parse the arguments from `args`; otherwise default to using `sys.argv[1:]`, just like `argparse`. Manually specifying `args` can be useful to e.g. read parameters from a configuration file.
