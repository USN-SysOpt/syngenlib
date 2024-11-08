# SynGenLib

**SynGenLib** is an object-oriented Python library that establishes a framework for defining dataclasses of synchronous generators and their respective step-up transformers. Using these dataclasses, one can define objects that help calculate the power losses of synchronous machines according to the method presented in [1]. Additionally, the library provides functionalities for defining generator capability diagrams based on the system of equations established in [2], with the purpose of calculating reactive power limits.

## Directory Organization

The SynGenLib code resides in the `src` folder and is divided into five parts:

- **archive**: Contains old and deprecated code. This folder is not accessible when using the library but is retained for potential future reference.
- **core**: Holds custom exceptions. Currently, this folder is empty.
- **data**: Defines the dataclasses used for storing parameters and result data.
- **models**: Contains calculation models for the generator, transformer, and capability diagram.
- **utils**: Intended for common helper functions and other utility classes. This folder is currently empty.

The `examples` folder contains sample generator and transformer dataclasses, along with scripts demonstrating how to get started with and use SynGenLib.

The `tests` folder includes unit tests for various calculation classes. This is a work in progress.

## Getting Started

To get started with SynGenLib, clone the repository to your local machine using `git` or by downloading the main branch from **GitHub**. Navigate to the repository folder and install the library using:

```bash
pip install .
```

These instructions will set up a local copy of the project for development and testing purposes. See the deployment section for notes on how to deploy the project in a live environment.

### Prerequisites

SynGenLib doesn't depend on any external Python libraries; only the standard **math** and **dataclasses** modules are used in the `src` folder. If you run examples, you may need **matplotlib** and **numpy**.

## Authors

- **Emil G. Melfald**, University of South-Eastern Norway

## License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.

## Acknowledgments

This library is inspired by the work presented in references [1] and [2].

## Citation

- [1] E. d. C. Bortoni, R. T. Siniscalchi, S. Vaschetto, M. A. Darmani, and A. Cavagnino, “Efficiency mapping and weighted average efficiency for large hydrogenerators,” IEEE Open J. Ind. Appl., vol. 2, pp. 11–20, 2021.
- [2] J. Machowski, Z. Lubosny, J. W. Bialek, and J. R. Bumby, *Power System Dynamics: Stability and Control*, Third Edition. Wiley, 2020.
