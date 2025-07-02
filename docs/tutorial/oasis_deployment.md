# Configuring and deploying NOMAD OASIS

The `nomad-baseclasses` package is intended to be used within NOMAD OASIS - any service that uses NOMAD software independently from the central [NOMAD](https://nomad-lab.eu/prod/v1/gui/search/entries). Below are the basic instructions on how to customize and deploy your own NOMAD OASIS. For deployment, a system with at least 4 CPU cores, 16 GB RAM and 30 GB disk space is recommended. For more details, see [NOMAD documentation](https://nomad-lab.eu/prod/v1/docs/howto/oasis/configure.html). 

## NOMAD OASIS distribution template

A simple single-machine setup with docker-compose is sufficient in many cases. [nomad-distro-template](https://github.com/FAIRmat-NFDI/nomad-distro-template) GitHub repository provides a template for the creation of NOMAD OASIS distribution image. The `README.md` file of this repository describes the process in detail; here we provide a short version.

Begin with `Use this template` in the upper right corner, which would create a new GitHub repository using the template. You will need to fill in the information for the repository, as well as choose between either private or public type (the public is recommended). An automated GitHub actions will run on creation; wait until all workflows finish (this might take tens of minutes). You can see the status of the workflows under `Actions` tab.

After this, return to the main page of the repository and refresh the tab. The top-most part of the README message should disappear (so you should see `<github username>'s NOMAD Oasis Distribution` instead of `NOMAD Oasis Distribution Template` at the top of `README.md`). If this did not happen, navigate to `Actions` tab, choose `Template Repository Initialisation` workflow and trigger it manually by clicking `Run workflow`.

## Plugins and NOMAD OASIS customization

NOMAD OASIS can be customized for specific application by various plugins. For detailed explanation of the NOMAD plugin system, see [the official documentation](https://nomad-lab.eu/prod/v1/docs/explanation/plugin_system.html). If you would like to test the OASIS with the default set of plugins, you can skip this paragraph and continue directly with deployment. Otherwise, the list of plugins can be modified in `pyproject.toml` by adding or removing lines in the plugin table:

```toml
[project.optional-dependencies]
plugins = [
    ...
]
```

Plugins can be specified in several ways. If it is distributed via PyPI, you can choose a version or a range of versions, for example.:

```toml
    "nomad-measurements>=1.2.0",
```

If it is availbale form GitHub repository, you can choose a tag:

```toml
    "nomad-measurements @ git+https://github.com/FAIRmat-NFDI/nomad-measurements.git@v0.0.4",
```

or a specific commit hash:

```toml
    "nomad-measurements @ git+https://github.com/FAIRmat-NFDI/nomad-measurements.git@71b7e8c9bb376ce9e8610aba9a20be0b5bce6775",
```

Note that `nomad-baseclasses` should not itself be on the list of plugins for your OASIS. Instead, it is imported as a python dependancy for plugins utilizing the base classes (for example, [nomad-hysprint](https://github.com/nomad-hzb/nomad-hysprint)).

Every time changes are commited to the main branch of the repository, the action generating docker image will be run automatically. When these workflows are finished, the OASIS can be deployed.

### Example: SE HZB OASIS plugin list

NOMAD OASIS at Helmoltz-Zentrum Berlin (HZB) uses the following plugins for organizing and interpreting experimental data:

- [nomad-perovskite-solar-cells-database](https://github.com/FAIRmat-NFDI/nomad-perovskite-solar-cells-database)
- [nomad-material-processing](https://github.com/FAIRmat-NFDI/nomad-material-processing)
- [nomad-measurements](https://github.com/FAIRmat-NFDI/nomad-measurements)
- [pynxtools](https://github.com/FAIRmat-NFDI/pynxtools)
- [pynxtools-xps](https://github.com/FAIRmat-NFDI/pynxtools-xps)
- [nomad-schema-plugin-simulation-workflow](https://github.com/nomad-coe/nomad-schema-plugin-simulation-workflow)
- [nomad-schema-plugin-run](https://github.com/nomad-coe/nomad-schema-plugin-run)
- [nomad-hysprint](https://github.com/nomad-hzb/nomad-hysprint)
- [hzb-combinatorial-libraries-plugin](https://github.com/nomad-hzb/hzb-combinatorial-libraries-plugin)
- [nomad-chemical-energy](https://github.com/nomad-hzb/nomad-chemical-energy)
- [nomad-pvcomb](https://codebase.helmholtz.cloud/pvcomb/nomad-pvcomb)

You can see this list with the specific versions at the bottom of the information tab of [SE HZB OASIS](https://nomad-hzb-se.de/nomad-oasis/gui/about/information#).

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

Pull the images specified in `docker-compose.yaml` file:

```
docker compose pull
```

Next choose if you will use HTTP or HTTPS protocols for communication. The former is set up by default and works well for testing. The latter is secure, but requires a TLS certificate, which must be renewed periodically. If you have a domain name, you can acquire a free certificate from [Let's Encrypt](https://letsencrypt.org/). Follow their tutorials to generate a certificate, then update configuration in `docker-compose.yml` by replacing

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

Finally, run `docker-compose` in detached mode (this might take several minutes):

```
docker compose up -d
```

NOMAD OASIS graphic inteface should now be accessible via browser at [http://localhost/nomad-oasis](http://localhost/nomad-oasis).

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

For simple tests, NOMAD OASIS can be deployed in GitHub Codespaces; this will use resources from GitHub and therefore will work even if your local computer lacks sufficient RAM. Most of the instruction above remain applicable, with the necessary changes described below:

1. Instead of cloning the repository created from the template locally, create Codespaces on main branch of the repository by selecting `Code` -> `Codespaces` -> `...` -> `new with options`, then chose an option with 16 GB RAM.

2. Use HTTP protocol for communication

3. To open GUI, instead of using `http://localhost/nomad-oasis` go to `https://<...>-80.app.github.dev/nomad-oasis/gui/about/information` in the new tab of your browser; here `https://<...>.github.dev/` is the address of the Codespaces.


