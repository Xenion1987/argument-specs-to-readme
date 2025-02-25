#!/usr/bin/env python3

from jinja2 import Environment, FileSystemLoader
import os
import yaml
import argparse
import requests
from io import StringIO

argspecs_file_path = "./meta/argument_specs.yml"
badges_file_path = "./meta/badges.yml"
meta_file_path = "./meta/main.yml"
template_file_path = "./.ci"
template_file_name = "README.md.j2"
output_file_path = "README.md"
template_url = "https://raw.githubusercontent.com/Xenion1987/argument-specs-to-readme/main/.ci/README.md.j2"

def download_template(url):
    """Downloads the template file from the given URL as a string."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        print(f"Successfully fetched template from {url}")
        return response.text
    except requests.RequestException as e:
        print(f"Error downloading template: {e}")
        return None

def save_template_to_file(template_content, destination):
    """Saves the template content to a file."""
    try:
        with open(destination, "w", encoding="UTF-8") as file:
            file.write(template_content)
        print(f"Successfully saved template to {destination}")
    except Exception as e:
        print(f"Error saving template: {e}")

def parse_yaml_file(yaml_file):
    if not os.path.isfile(yaml_file):
        raise FileNotFoundError(f"YAML file {yaml_file} does not exist.")

    with open(yaml_file, 'r') as f:
        try:
            data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"Error parsing YAML file: {e}")
    return data

def parse_options(options, parent_key=""):
    """Recursively parses the `options` structure and converts it into Markdown."""
    if not isinstance(options, dict):
        return ""
    
    section = ""
    for key, value in options.items():
        full_key = f"{parent_key}.{key}" if parent_key else key
        md_line = f"| `{full_key}` "
        
        for field in ['type', 'required', 'choices', 'default', 'description']:
            if field in value:
                if field == 'type':
                    md_line += f"| `{value[field]}` ".lower()
                elif field == 'choices':
                    choices = [str(choice).lower() if isinstance(choice, bool) else str(choice) for choice in value[field]]
                    md_line += f"| `{'`, `'.join(choices)}` "
                elif field == 'description':
                    description = ' <br />'.join(value[field]) if isinstance(value[field], list) else value[field]
                    md_line += f"| {description} "
                else:
                    md_line += f"| `{str(value[field]).lower()}` " if isinstance(value[field], bool) else f"| `{value[field]}` "
            else:
                md_line += "| "
        
        section += f"{md_line}|\n"
        
        # If nested `options` exist, process them recursively
        if 'options' in value and isinstance(value['options'], dict):
            section += parse_options(value['options'], full_key)
    
    return section

def generate_argspecs_variables(specs):
    """Generates Markdown documentation based on argument specifications."""
    section_variables = ""
    for category, arguments in specs.items():
        section_variables += f"{category}\n---\n\n"
        section_variables += "| Variable | Type | Required | Choices | Default | Description |\n"
        section_variables += "| --- | --- | --- | --- | --- | --- |\n"
        if isinstance(arguments, dict) and 'options' in arguments and isinstance(arguments['options'], dict):
            section_variables += parse_options(arguments['options'])
        section_variables += "\n"
    return section_variables

def get_template_from_string(template_string):
    """Loads a Jinja2 template from a string."""
    try:
        env = Environment()
        return env.from_string(template_string)
    except Exception as e:
        print(f"Error loading template: {e}")
        return None

def render_template(template, context, output_file):
    try:
        rendered_output = template.render(context)
        with open(output_file, "w", encoding="UTF-8") as file:
            file.write(rendered_output)
        print(f"Successfully rendered and wrote {output_file}")
    except Exception as e:
        print(f"Error rendering template or writing file: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--offline", action="store_true", help="Use local template file instead of downloading")
    args = parser.parse_args()
    
    template_content = None
    if args.offline:
        if os.path.isfile(os.path.join(template_file_path, template_file_name)):
            with open(os.path.join(template_file_path, template_file_name), "r", encoding="UTF-8") as file:
                template_content = file.read()
        else:
            if os.path.isdir(template_file_path) and __file__.startswith(template_file_path):
                os.makedirs(template_file_path, exist_ok=True)
                template_content = download_template(template_url)
                if template_content:
                    save_template_to_file(template_content, os.path.join(template_file_path, template_file_name))
    else:
        template_content = download_template(template_url)
    
    if not template_content:
        print("Error: Could not load template.")
        exit(1)
    
    template = get_template_from_string(template_content)
    
    argspecs_data = parse_yaml_file(argspecs_file_path)
    arg_specs = generate_argspecs_variables(argspecs_data.get('argument_specs', {}))
    meta = parse_yaml_file(meta_file_path)
    badges = parse_yaml_file(badges_file_path) if os.path.isfile(badges_file_path) else ''
    
    context = {
        'arg_specs': arg_specs,
        'badges': badges,
        'meta': meta
    }
    
    if template:
        render_template(template, context, output_file_path)
