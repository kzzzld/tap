# Homebrew Tap

Homebrew formulae maintained by [kzzzld](https://github.com/kzzzld).

## hckr

A Hacker News terminal app written in C, with keyboard and mouse navigation, threaded discussions, and configurable INI themes.

```sh
brew tap kzzzld/tap https://github.com/kzzzld/tap
brew install --HEAD kzzzld/tap/hckr
brew test kzzzld/tap/hckr
```

If Homebrew asks you to trust the formula, run `brew trust --formula kzzzld/tap/hckr`, then retry installation.

The formula builds the current `main` branch; no tagged release is available yet.

To update:

```sh
brew update
brew upgrade --fetch-HEAD kzzzld/tap/hckr
```

Project documentation and source: [kzzzld/hckr](https://github.com/kzzzld/hckr).

## Stable releases

The `Update hckr` action checks [hckr releases](https://github.com/kzzzld/hckr/releases) hourly. It verifies the source archive against the published SHA256SUMS file and updates the stable formula URL and checksum. Development `--HEAD` installs remain available. Before the first release, the updater makes no changes.

For an immediate check after a release finishes:

```sh
gh workflow run update-hckr.yml --repo kzzzld/tap
```

After the first stable release, install with `brew install kzzzld/tap/hckr`. To switch an existing development install to stable, run `brew reinstall kzzzld/tap/hckr`.

Keep build instructions and dependencies synchronized with the development template in the hckr repository. The updater only changes the stable source URL and checksum. Never replace a published version's assets; publish a new version for corrections.
