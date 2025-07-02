# Configuring and deploying NOMAD OASIS

The `nomad-baseclasses` package is intended to be used within NOMAD OASIS - any service that uses NOMAD software independently from the central [NOMAD](https://nomad-lab.eu/prod/v1/gui/search/entries). Below are basic instructions for customizing and deploying your own NOMAD OASIS. For deployment, a system with at least 4 CPU cores, 16 GB RAM and 30 GB disk space is recommended. For more details, see [NOMAD documentation](https://nomad-lab.eu/prod/v1/docs/howto/oasis/configure.html). 

## NOMAD OASIS distribution template

A simple single-machine setup with docker-compose is sufficient in many cases. [nomad-distro-template](https://github.com/FAIRmat-NFDI/nomad-distro-template) GitHub repository provides a template for the creation of NOMAD OASIS distribution image. The `README.md` file of this repository describes the process in detail; here we provide a short version.

Begin with `Use this template` in the upper right corner, which would create a new GitHub repository using the template. You will need to fill in the information for the repository, as well as choose between either private or public type (the public is recommended). An automated GitHub Actions workflow will run upon creation; wait until all workflows finish (this may take tens of minutes). You can see the status of the workflows under `Actions` tab.

After this, return to the main page of the repository and refresh the tab. The top-most part of the README message should disappear (so you should see `<github username>'s NOMAD Oasis Distribution` instead of `NOMAD Oasis Distribution Template` at the top of `README.md`). If this did not happen, navigate to `Actions` tab, choose `Template Repository Initialisation` workflow and trigger it manually by clicking `Run workflow`.

## Plugins and NOMAD OASIS customization

NOMAD OASIS can be customized for specific application by various plugins. For detailed explanation of the NOMAD plugin system, see [the official documentation](https://nomad-lab.eu/prod/v1/docs/explanation/plugin_system.html). If you would like to test the OASIS with the default set of plugins, you can skip this section and continue directly with deployment. Otherwise, the list of plugins can be modified in `pyproject.toml` by adding or removing lines in the plugin table:

```toml
[project.optional-dependencies]
plugins = [
    ...
]
```

Plugins can be specified in several ways. If it is distributed via PyPI, you can choose a version or a range of versions, for example:

```toml
    "nomad-measurements>=1.2.0",
```

If it is available from GitHub repository, you can choose a tag:

```toml
    "nomad-measurements @ git+https://github.com/FAIRmat-NFDI/nomad-measurements.git@v0.0.4",
```

or a specific commit hash:

```toml
    "nomad-measurements @ git+https://github.com/FAIRmat-NFDI/nomad-measurements.git@71b7e8c9bb376ce9e8610aba9a20be0b5bce6775",
```

Note that `nomad-baseclasses` does not have to be included directly in the plugin list for your OASIS. Instead, it can be imported as a python dependency for plugins utilizing the base classes (for example, [nomad-hysprint](https://github.com/nomad-hzb/nomad-hysprint)).

Every time changes are commited to the main branch of the repository, the action generating docker image will be run automatically. When these workflows are finished, the OASIS can be deployed.

### Example plugin lists
<!-- Example: SE HZB OASIS plugin list -->

List of plugins installed in a given NOMAD OASIS can be found under the `About` -> `Information` page of this OASIS (scroll to the bottom of the page). The `plugin packages` gives the general list of plugins, and specific entry points for apps, parsers, schemas etc are given below. Click on any item in these lists to view more detailed information, such as a short description and specific plugin version.

Examples:

- NOMAD OASIS at Helmholtz-Zentrum Berlin: [SE HZB OASIS](https://nomad-hzb-se.de/nomad-oasis/gui/about/information)

- Central NOMAD deployment: [NOMAD](https://nomad-lab.eu/prod/v1/gui/about/information)

- Central example OASIS: [Example OASIS](https://nomad-lab.eu/prod/v1/oasis/gui/about/information)

## Deploying NOMAD OASIS

Make sure you have `docker` installed. Then clone the repository created from the template:

```
git clone https://github.com/<github username>/test-oasis-for-workshop.git
cd test-oasis-for-workshop
```

On Linux systems only, recursively change the owner of the `.volumes` directory to the nomad user (1000):

```
sudo chown -R 1000 .volumes
```

Pull the images specified in the `docker-compose.yaml` file:

```
docker compose pull
```

Next choose if you will use HTTP or HTTPS protocols for communication. HTTP is set up by default and is suitable for testing. HTTPS is more secure, but requires a TLS certificate, which must be renewed periodically. If you have a domain name, you can acquire a free certificate from [Let's Encrypt](https://letsencrypt.org/). Follow their tutorials to generate a certificate, then update configuration in `docker-compose.yaml` by replacing

```
# HTTP
- ./configs/nginx_http.conf:/etc/nginx/conf.d/default.conf:ro
```

with

```
# HTTPS
- ./configs/nginx_https.conf:/etc/nginx/conf.d/default.conf:ro
- ./ssl:/etc/nginx/ssl:ro  # Your certificate files
```

Finally, run `docker-compose` in detached mode (this may take a few minutes):

```
docker compose up -d
```

NOMAD OASIS graphic interface should now be accessible via browser at [http://localhost/nomad-oasis](http://localhost/nomad-oasis).

The OASIS can be stopped by using

```
docker compose down
```

and updated by repeating

```
docker compose pull
docker compose up -d
```

### Test deployment using GitHub Codespaces

For simple tests, NOMAD OASIS can be deployed in GitHub Codespaces; this will use resources from GitHub and therefore will work even if your local computer lacks sufficient RAM. Most of the instructions above remain applicable, with the necessary changes described below:

1. Instead of cloning the repository created from the template locally, create Codespaces on main branch of the repository by selecting `Code` -> `Codespaces` -> `...` -> `new with options`, then choose an option with 16 GB RAM.

2. Use the HTTP protocol for communication

3. To open GUI, instead of using `http://localhost/nomad-oasis` go to `https://<...>-80.app.github.dev/nomad-oasis/gui/about/information` in a new browser tab; here `https://<...>.github.dev/` is the address of the Codespaces.


