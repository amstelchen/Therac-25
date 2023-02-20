[![Documentation Status](https://readthedocs.org/projects/therac-25/badge/?version=latest)](https://therac-25.readthedocs.io/en/latest/?badge=latest) [![Python package](https://github.com/amstelchen/Therac-25/actions/workflows/python-package-no-pytest.yml/badge.svg)](https://github.com/amstelchen/Therac-25/actions/workflows/python-package-no-pytest.yml)

<h1>Therac-25</h1>

### A Python port of the C implementation of the Therac-25 interface (and bugs)

#### Introduction

The imfamous *__Therac-25__*, produced by Atomic Energy of Canada Limited (AECL) in 1982 after the Therac-6 and Therac-20 units, was a computer-controlled radiation therapy machine that between 1985 and 1987, gave six patients massive overdoses of radiation, of which three of them died.

This repository holds my port of the original C [source code](http://web.mit.edu/6.033/2007/wwwdocs/assignments/therac.c) found on MIT's [Hands-on 3b of 6.033 - Computer System Engineering](http://web.mit.edu/6.033/2007/wwwdocs/assignments/handson-therac.html) onto the Python scripting language.


#### Installation

Steps assume that `python` (>= 3.8) and `pip` are already installed.

Install dependencies (see sections below)

Then, run:

    $ pip install therac-25

or from the wheel:

    $ pip install therac_25-0.1.1-py3-none-any.whl

Install directly from ``github``:

    $ pip install git+https://github.com/amstelchen/Therac-25#egg=Therac-25

When completed, run it with:

    $ therac-25

or

    $ therac

#### Quick start commands

BEAM TYPE:
- (empty)
- "X": Megavolt X-ray
- "E": Electron-beam therapy

("field light" mode was supposely not implemented in the C source code)

COMMAND: 
- "b" or "B" - Start treatment
- "q" or "Q" - Quit program

#### Dependencies

None, except curses which will come pre-installed with any Linux distro.

On Windows, you are on your own, using [UniCurses](https://pypi.org/project/UniCurses/) with [PDCurses](https://pdcurses.org/) might work (__not tested__).

#### Reporting bugs

If you encounter any bugs or incompatibilities, or deaths, __please report them [here](https://github.com/amstelchen/Therac-25/issues/new)__.

#### Screenshot

TBD

#### Future plans / TODO

TBD, (see TODO.md)

#### Changelog

- 0.1.0: initial version
- 0.1.1: removed logging

#### Licences

*Therac-25* Python port is licensed under the [MIT](LICENSE) license.

The original C implementation is licensed under the [MIT](LICENSE) license as well.
