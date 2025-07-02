# Development environment for the NOMAD plugins

NOMAD OASIS can be customized using NOMAD plugins - either already existing ones or the newly created or modified for specific purpose. However, developing plugins within a standard OASIS deployment is inconvenient and unnecesserily time-consuming: the docker images will have to be generated and deployed anew after each correction to the plugin code. Instead, a local development environment can be utilized to develop multiple plugins (as well as cenrtral NOMAD package) in a consistent, centralized and much easier way. This can be done using [`nomad-distro-dev`](https://github.com/FAIRmat-NFDI/nomad-distro-dev) repository on GitHub. The development environment is designed to natively work with Linux and macOS; it is still possible to run it on Windows systems, however the environment can potentially run slower or require more resources. Below we describe these two cases separately.

## Setting up `nomad-distro-dev` on Linux or macOS

Start with forking [`nomad-distro-dev`](https://github.com/FAIRmat-NFDI/nomad-distro-dev) repository (`Fork` -> `Create a new fork` in the upper right part of the page). You will also need following software installed on your system:

- [docker](https://docs.docker.com/engine/install/) - generally, only `docker-compose` functionality will be needed

- [uv](https://docs.astral.sh/uv/getting-started/installation/) python package manager, version 0.5.14 or above

- [node.js](https://nodejs.org/en) version 20 or above and [yarn](https://classic.yarnpkg.com/en/docs/install) version 1.22 or above are necessary to run the GUI

- [git](https://github.com/git-guides/install-git) for version control and interaction with GitHub

- Some IDE for plugin development, such as [VS Code](https://code.visualstudio.com/docs/setup/linux)

Clone the forked repostory from GitHub:

```
git clone https://github.com/<your-username>/nomad-distro-dev.git
cd nomad-distro-dev
```

And run docker containers in detached mode:

```
docker compose up -d
```

If you wish to stop the containers, use from the same folder

```
docker compose down
```

After that follow the `Step-by-Step Setup` manual in the `nomad-distro-dev` readme file.

If the plugin you are developing has its own sub-plugins (or any other submodules), such as [pynxtools](https://github.com/FAIRmat-NFDI/pynxtools), you will need to repeat submodules initialization after adding the plugin by running again:

```
git submodule update --init --recursive
```

Note that the plugins added to the repository are each also git repositories, so you can choose to work on a specific branch and push or pull changes as usual by using `git` commands from the corresponding folder, for example:

```
cd packages/<plugin-name>
git checkout -b New-feature-branch
```

## Setting up `nomad-distro-dev` on Windows

Start with forking [`nomad-distro-dev`](https://github.com/FAIRmat-NFDI/nomad-distro-dev) repository (`Fork` -> `Create a new fork` in the upper right part of the page). You will also need following software installed on your system:

- [Docker desktop](https://docs.docker.com/desktop/setup/install/windows-install/) - choose the default option with WSL. On the first start docker will require to create an account and update version of WSL installed on your system; proceed according to the instructions provided by docker.

- [VS Code](https://code.visualstudio.com/docs/setup/linux) for plugin development

- `Dev Containers` extension for VS Code. In order to install it, start VS Code, go to the `Extensions` tab on the left side (also `Ctrl + Shift + X` by default) and type `Dev Containers` into the search. Install the official extension from Microsoft with this name.

- [git](https://github.com/git-guides/install-git) for version control and interaction with GitHub

Clone the forked repostory from GitHub:

```
git clone https://github.com/<your-username>/nomad-distro-dev.git
```

Make sure docker desktop is running, then open the folder with the cloned repository in the VS Code. A notification that the folder contains a Dev Container configuration file should appear; click `Reopen in Container`. This step might take minutes, depending on the system; you can see the log while waiting. `uv` will be automatically installed during this step.

Next, open a new terminal within VS Code (`+` on the upper right of the existing terminal, or via drop-down menu `Terminal` on the top of the main window) and continue with the setup:

```
docker compose up -d
git submodule update --init --recursive
```

Add desired plugins as described in the readme file of `nomad-distro-dev` (this step is the same for all OS):

```
git submodule add https://github.com/<user_name>/<package_name>.git packages/<package_name>
uv add packages/<package_name>
```

For example, in order to add `nomad-perovskite-solar-cells-database` plugin, run:

```
git submodule add https://github.com/FAIRmat-NFDI/nomad-perovskite-solar-cells-database.git packages/nomad-perovskite-solar-cells-database
uv add packages/nomad-perovskite-solar-cells-database/
```

If the plugin you are developing has its own sub-plugins (or any other submodules), such as [pynxtools](https://github.com/FAIRmat-NFDI/pynxtools), you will need to repeat submodules initialization after adding the plugin by running again:

```
git submodule update --init --recursive
```

Note that the plugins added to the repository are each also git repositories, so you can choose to work on a specific branch and push or pull changes as usual by using `git` commands from the corresponding folder, for example:

```
cd packages/<plugin-name>
git checkout -b New-feature-branch
```

Next, update the environment and install all the necessary dependencies:

```
uv run poe setup
```

This step might take significant time on the first run, 30 minutes is not unusual.

Finally, start the NOMAD API app and NOMAD GUI:

```
uv run poe start
```

```
uv run poe gui start
```

Either command will occupy the terminal, so run these two in separate terminals.

## Additional information

If you modified the plugin code and would like to restart the NOMAD, in most cases stopping and restarting NOMAD API app is sufficient (`Ctrl + C` in the corresponding terminal, then `uv run poe start`). In some cases, GUI also has to be restarted.

In order to stop local NOMAD, interrupt both API app and GUI with `Ctrl + C`, then stop docker images:

```
docker compose down
```
