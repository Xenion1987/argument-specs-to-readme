# README

## Argument Specs to README Generator

This script automatically generates a `README.md` file based on YAML files in `./meta/` and a Jinja2 template file.

Example in- and output files:

 - [ansible-role-sudoers](https://github.com/Xenion1987/ansible-role-sudoers)
 - [ansible-role-user-management](https://github.com/Xenion1987/ansible-role-user-management)

### Requirements

- Python 3
- `jinja2` and `pyyaml` libraries (install via `pip install jinja2 pyyaml`)

### Usage

#### Standard Mode (Online)

Without additional arguments, the script fetches the Jinja2 template directly from GitHub and processes `README.md` accordingly:

```bash
curl -sL https://raw.githubusercontent.com/Xenion1987/argument-specs-to-readme/main/.ci/meta-to-doc.py | python3
```

#### Offline Mode

If the script is executed with `--offline` or `-o`, it first checks whether the template file is already available locally in `./.ci/`. If not, and the script itself is located in `./.ci/`, it will download and save the template from GitHub.

First, download the script and required files by cloning the repository:

```bash
git clone https://github.com/Xenion1987/argument-specs-to-readme.git .ci
```

Then execute the script locally:

```bash
python3 .ci/meta-to-doc.py --offline
```

### Files & Directory Structure

- `meta/argument_specs.yml` - Contains argument specifications
- `meta/main.yml` - Contains metadata for the README
- `meta/badges.yml` - (Optional) Contains badges for the README
- `.ci/README.md.j2` - Jinja2 template (required only in offline mode)
- `README.md` - The generated output

### Error Handling

If YAML files do not exist or contain errors, the script will output an appropriate error message. If the Jinja2 template cannot be fetched, the script will terminate with an error.

### License

MIT License
