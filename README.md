_Easily make experiments configurable on the command line._

`selector` makes even complex experimental setups configurable on the command line, making it easy to test and compare different designs. Simple by default, flexible when needed.

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
import selector
import models

model = selector.add_options_from_module(
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
        backbone: Backbone,  # <-- added dependency
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
    'backbone',
    models,
    of_subclass=models.Backbone,
)()

model = selector.add_options_from_module(
    'model',
    models,
    of_subclass=models.GenerativeModel,
)(
    backbone=backbone,  # <-- added injection
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

> Note that `selector.add_options_from_module[T]` returns a `functools.partial[T]` pre-filled with the options specified on the CLI. This means values can be overridden at invocation (inside the parentheses), which allows for wiring together complex configured objects, such as passing a configured `backbone` into a model.
> 
> Also note that the return types follow your signatures: e.g. `model` is typed as `GenerativeModel`, and so forth – no separate config schema nor untyped namespace.


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
        activation_function: nn.Module,  # <-- added dependency
    ): ...
```
and simply make activation function choice available by
```python
import torch.nn.modules.activation

activation_function = selector.add_options_from_module(
    'activation_function',
    torch.nn.modules.activation,
    of_subclass=nn.Module,
)()
```
which makes all `torch`'s activation functions selectable, ready to be passed into the backbone
```python
backbone = selector.add_options_from_module(
    'backbone',
    models,
    of_subclass=models.Backbone,
)(
    activation_function=activation_function,  # <-- added injection
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
dataset = selector.add_arguments('dataset', ImageDataset)()
```
in the training setup. Same goes for data loaders with
```python
dataloader = selector.add_arguments('dataloader', torch.utils.data.DataLoader)(dataset=dataset)
```
making everything from `batch_size` and `shuffle` to `num_workers` and `pin_memory` selectable on the command line.

> Only parameters with supported type hints are exposed; parameters with unsupported or missing type annotations are skipped.

The full example, with fully configurable generative model choice, backbone choice, activation function, data location, and data loader settings is as simple as
```python
import selector

import torch.utils.data
import torch.nn.modules.activation
import torch.nn as nn

import models


activation_function = selector.add_options_from_module(
    'activation_function',
    torch.nn.modules.activation,
    of_subclass=nn.Module,
)()

backbone = selector.add_options_from_module(
    'backbone',
    models,
    of_subclass=models.Backbone,
)(
    activation_function=activation_function,
)

model = selector.add_options_from_module(
    'model',
    models,
    of_subclass=models.GenerativeModel,
)(
    backbone=backbone,
)

dataset = selector.add_arguments('dataset', ImageDataset)()
dataloader = selector.add_arguments('dataloader', torch.utils.data.DataLoader)(dataset=dataset)
```

## Advanced
`selector` allows flexibility in four ways.

### Manual `ArgumentParser`
`selector` is built around the built-in `argparse.ArgumentParser`, which is accessible and interchangeable. It maintains an automatically instantiated parser, which is obtainable through
```python
selector.parser.get()
```
and settable via e.g.
```python
import argparse

parser = argparse.ArgumentParser()

selector.parser.set(parser)
```
All functions also allow for optional `parser=...` arguments, which takes precedence over the default parser.

### Manual arguments
`selector` defaults to using arguments from `sys.argv`, but all functions allow for setting `args=...` to be used instead. This can be useful for injecting additional arguments, or to read arguments from a configuration file instead of from the command line.

### Converters
Types that do not have a proper default string-to-instance conversion can be instantiated via custom converters. This is exposed in `selector.converters`, which already registers special handling of booleans and enums this way.

Custom converters can be added, e.g. another boolean converter also accepting `yes` and `no`
```python
def to_bool(value: str, _: type[bool]) -> bool:
    match value.lower():
        case 'true' | 'yes':
            return True
        case 'false' | 'no':
            return False
        case _:
            raise ValueError(f'Invalid bool value: {value!r}')

selector.converters.converter.add(bool, to_bool)
```
which accepts converter callables that take two arguments; the string value and the type to be instantiated.

### Postprocessors
Postprocessing of instantiated values is also supported. This is currently used to handle e.g. sets which are created from the lists that argparse actually returns.

Custom postprocessors can be added via e.g.
```python
selector.postprocessors.postprocessor.add(frozenset, frozenset)
```

> Postprocessors run after type conversion but before being used in the `partial` invocations.


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

> Note that all functions take optional `parser` and `args` keyword-only arguments, which can be used to specify custom `ArgumentParser`s and arguments, instead of a default `ArgumentParser` and `sys.argv` input, respectively.

### `get_argument`
```python
def get_argument(
    name: str,
    type: Type[T],
    default: T | None = None,
    *,
    parser: ArgumentParser | None = None,
    args: Sequence[str] | None = None,
) -> T: ...
```
allows for quickly obtaining a single value, nicely typed. E.g.
```python
n_experiments = selector.get_argument('n_experiments', int, default=5)
```
makes a single parameter selectable on the command line, and returns a properly typed result.

### `add_arguments`
```python
def add_arguments(
    name: str,
    reference: Type[T] | Callable,
    *,
    parser: ArgumentParser | None = None,
    args: Sequence[str] | None = None,
) -> partial[T]: ...
```
makes the parameters of a function or a class's `__init__` method available on the command line. This function is the main building block of `selector`. It is useful on its own, e.g. to make a specific class configurable on the command line
```python
dataset = selector.add_arguments('dataset', ImageDataset)()
```
with `dataset` properly typed, or for a function
```python
def main(n_experiments: int, n_iterations: int, log_dir: str):
    ...

if __name__ == '__main__':
    selector.add_arguments('main', main)()
```
useful for making scripts automatically configurable on the command line.

### `add_options`
```python
def add_options(
    name: str,
    options: Sequence[Type[T]],
    *,
    parser: ArgumentParser | None = None,
    args: Sequence[str] | None = None,
) -> partial[T]: ...
```
is a convenient tool for choosing between a set of options, each configurable as in `add_arguments`. Useful for fixed choices
```python
backbone = selector.add_options('backbone', (UNet, ConvNet))()
```

### `add_options_from_module`
```python
def add_options_from_module(
    name: str,
    module: ModuleType,
    of_subclass: Type[T],
    *,
    parser: ArgumentParser | None = None,
    args: Sequence[str] | None = None,
) -> partial[T]: ...
```
automatically discovers and adds all classes in the given module which are subclasses of `of_subclass`, as shown in the running example above.
