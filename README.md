# Homebrew Tap

Homebrew formulae maintained by [kzzzld](https://github.com/kzzzld).

## hckr

A Hacker News terminal app written in C, with keyboard and mouse navigation, threaded discussions, and configurable INI themes.

```sh
brew tap kzzzld/tap
brew install --HEAD kzzzld/tap/hckr
brew test kzzzld/tap/hckr
```

The formula builds the current `main` branch; no tagged release is available yet.

To update:

```sh
brew update
brew upgrade --fetch-HEAD kzzzld/tap/hckr
```

Project documentation and source: [kzzzld/hckr](https://github.com/kzzzld/hckr).
