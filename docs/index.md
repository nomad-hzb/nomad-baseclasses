# Welcome to the Documentation for Nomad Baseclasses at HZB

## Introduction

This is a nomad plugin, see [Nomad Plugins](https://nomad-lab/prod/v1/staging/docs/plugins.html) on how to use them.

## About the Plugin

At the core of this plugin are deposition techniques as they are used in perovskite solar cells, characterization methods for these solar cells, and electrochemical techniques, such as those involving a potentiostat. The plugin offers a structured approach to manage and analyze data related to these techniques, facilitating a deeper understanding and innovation in solar cell and electrocatalysis research.

## Using Nomad Plugins

For general information on how to use Nomad plugins, refer to the [Nomad Plugins documentation](https://nomad-lab/prod/v1/staging/docs/plugins.html). This will provide you with the foundational knowledge needed to effectively utilize our plugin.

## Baseclasses Folder

The `baseclasses` folder is the heart of this plugin, containing several Nomad schemas developed at Helmoltz-Zentrum Berlin (HZB). These schemas are critical for organizing and interpreting experimental data. Further explanations and details can be found in the `docs` folder of this repository.

## Application Plugins and Parsers

The schemas and techniques provided by this plugin can be used to derive application-specific plugins and parsers. Here are some examples of how our baseclasses have been utilized in different contexts:
- [HZB Solar Cells](https://github.com/RoteKekse/nomad-hysprint)
- [HZB Electro Catalysis](https://github.com/RoteKekse/nomad-chemical-energy)
- [KIT Solar Cells](https://github.com/RoteKekse/nomad-perotf)
