"""
Generator Module: Renders Cisco configuration files using Jinja2 templates and YAML data.
"""
from pathlib import Path
import yaml
from jinja2 import Environment, FileSystemLoader, Undefined


class ConfigGenerator:
    def __init__(self, template_dir: str = "templates"):
        self.template_dir = Path(template_dir)
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            trim_blocks=True,
            lstrip_blocks=True,
            undefined=Undefined
        )

    def load_yaml(self, data_path: str) -> dict:
        """Loads and parses a YAML data model file."""
        with open(data_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def generate(self, template_name: str, context: dict) -> str:
        """Renders a single template with the provided context dictionary."""
        template = self.env.get_template(template_name)
        return template.render(context)

    def generate_all(self, data_path: str, output_dir: str = "output") -> list[str]:
        """
        Iterates over inventory and generates configurations for all devices.
        Returns a list of paths to generated configuration files.
        """
        data = self.load_yaml(data_path)
        out_path = Path(output_dir)
        out_path.mkdir(parents=True, exist_ok=True)
        generated_files = []

        # Generate router configs
        if "routers" in data:
            for router in data["routers"]:
                config = self.generate("cisco_router.j2", {"router": router})
                filename = out_path / f"{router['hostname']}.ios"
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(config)
                generated_files.append(str(filename))

        # Generate switch configs
        if "switches" in data:
            for switch in data["switches"]:
                config = self.generate("cisco_switch.j2", {"switch": switch})
                filename = out_path / f"{switch['hostname']}.ios"
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(config)
                generated_files.append(str(filename))

        return generated_files
