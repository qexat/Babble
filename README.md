<!-- markdownlint-disable MD028-->

# Babble

**Babble** is a pretty visual noise generator TUI application.

## What is its purpose?

To be fair, none. It's more like a fun project and a proof of concept of combining [`coquille`](https://pypi.org/project/coquille) and [`outspin`](https://pypi.org/project/outspin).

## Usage

After starting **Babble**, you should see two text elements: at the top is the _header_ of the application, and at the bottom the _status bar_ with the keys and what they do when pressed.\
A huge empty space is left in the center: this is where the _window_ that you will fill up sits.

- Press `Space` to randomly fill the _pixels_ until the window is crowded.
- `Enter` is similar to `Space` but is like a "step": it only randomly fills a few _pixels_ and the process is done once.
- Pressing `r` will shuffle the _pixels_ around. It does not fill any new one.
- Pressing `s` does the opposite of `r`: it sorts the _pixels_ in a certain way.
- Press `e` to clean the _window_.
- `i` enters the _immersive mode_, which simply hides the _header_ and the _status bar_. Pressing it again exits that mode.
- Finally, you can press `q` to quit **Babble**. Alternatively, you can also use `esc`.

> [!IMPORTANT]
> Space: You can interrupt the process by pressing `Ctrl` + `C`. The pixels already filled keep their state.

> [!NOTE]
> The sorting algorithm will be configurable in the future.

## How to run it?

Once you have installed **Babble** locally, simply type `babble` in the terminal and press `Enter`.

## Installation

1. First, clone the repository and move to the directory:

   ```sh
   git clone git@github.com:qexat/babble
   cd babble
   ```

2. (Optional, but highly recommended) Create a virtual environment and activate it:

   ```sh
   virtualenv .venv -ppython311
   source .venv/bin/activate
   ```

   > [!WARNING]
   > If your shell is not `bash`, the activation script might have a slightly different name.

3. Install **Babble**:

   ```sh
   # the dot means "the project of the current directory"
   pip install .
   ```

4. You are set up! You can now run **Babble**:

   ```sh
   babble
   ```

Once you are in **Babble**, press `q` or `esc` to quit the program.

All the commands above at once:

```sh
git clone git@github.com:qexat/babble; cd babble
virtualenv .venv -ppython311; source .venv/bin/activate
pip install .
babble
```

## Configuration

Some of **Babble**'s behavior can be configured.

- `--randomize-at-launch`: (default: `False`) pretends that you pressed `Space` at startup.
- `--immersive`: (default: `False`) activates the immersive mode by default.
- `--pixels-per-step`: (default: `1000`) changes the number of pixels generated at each step (e.g. when pressing `Enter`)

---

I hope you like it ❤️

Encountered a problem? Want to request a feature? Open an [issue](https://github.com/qexat/babble/issues/new)!\
A question? Find me on [X/Twitter](https://twitter.com/notqexat)!
