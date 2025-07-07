# CMO CLI (Command-line interface)

## Usage

```text
Usage: smo-cli [OPTIONS] COMMAND [ARGS]...

  SMO-CLI: A command-line interface for the Synergetic Meta-Orchestrator.

Options:
  --help  Show this message and exit.

Commands:
  cluster  Commands for managing cluster information.
  graph    Commands for managing HDAGs.
  init     Initializes the SMO-CLI environment in ~/.smo/
```

### Subcommands

```text
❯ smo-cli init --help
Usage: smo-cli init [OPTIONS]

  Initializes the SMO-CLI environment in ~/.smo/

Options:
  --help  Show this message and exit.
```

```text
❯ smo-cli cluster --help
Usage: smo-cli cluster [OPTIONS] COMMAND [ARGS]...

  Commands for managing cluster information.

Options:
  --help  Show this message and exit.

Commands:
  list  Lists all clusters known to SMO-CLI from the local DB.
  sync  Fetches cluster info from Karmada and syncs with the local DB.
```

```text
❯ smo-cli graph --help
Usage: smo-cli graph [OPTIONS] COMMAND [ARGS]...

  Commands for managing HDAGs.

Options:
  --help  Show this message and exit.

Commands:
  deploy    Deploys a new HDAG from a file or OCI URL.
  describe  Shows detailed information for a specific graph.
  list      Lists all deployed graphs.
  re-place  Triggers placement optimization for a deployed graph.
  remove    Removes a graph completely from SMO and the cluster.
```

## Architecture

1.  The `smo-cli` package depends on `smo-core` for all the actual integration with the cluster(s).
2.  **CLI-Specific Scaffolding**: The package contains its own `core` directory with modules for handling CLI-specific concerns:
    *   **Configuration**: Loading settings from `~/.smo/config.yaml`.
    *   **Database**: Setting up the SQLAlchemy engine for a local **SQLite** database.
    *   **Context**: Creating the `SmoContext` object, populating it with helper instances initialized from the CLI's config, and passing it to commands.
3.  **Command Implementation (`click`)**: The `commands` directory contains the `click`-based command definitions. These command functions are the "glue" that:
    *   Parse command-line arguments.
    *   Get the `SmoContext` and a database session.
    *   Call the appropriate service function from `smo-core`.
    *   Format the results for display in the console using `rich`.

This design keeps the CLI layer thin and focused on user interaction, while all the heavy lifting is delegated to the robust, well-tested `smo-core` library.
