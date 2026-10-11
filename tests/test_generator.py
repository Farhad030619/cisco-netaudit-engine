"""Unit tests for ConfigGenerator verifying YAML loading and Jinja2 rendering."""
from pathlib import Path
from core.generator import ConfigGenerator


def test_load_yaml_valid_inventory():
    generator = ConfigGenerator(template_dir="templates")
    data = generator.load_yaml("data/inventory.yaml")

    assert "routers" in data
    assert "switches" in data
    assert len(data["routers"]) >= 1
    assert len(data["switches"]) >= 1


def test_render_router_template():
    generator = ConfigGenerator(template_dir="templates")
    data = generator.load_yaml("data/inventory.yaml")
    router_data = data["routers"][0]

    config = generator.generate("cisco_router.j2", {"router": router_data})

    assert f"hostname {router_data['hostname']}" in config
    assert "service password-encryption" in config
    assert "ip ssh version 2" in config
    assert "router ospf" in config


def test_render_switch_template():
    generator = ConfigGenerator(template_dir="templates")
    data = generator.load_yaml("data/inventory.yaml")
    switch_data = data["switches"][0]

    config = generator.generate("cisco_switch.j2", {"switch": switch_data})

    assert f"hostname {switch_data['hostname']}" in config
    assert "spanning-tree mode rapid-pvst" in config
    assert "spanning-tree portfast default" in config


def test_generate_all_outputs(tmp_path):
    generator = ConfigGenerator(template_dir="templates")
    output_files = generator.generate_all("data/inventory.yaml", output_dir=str(tmp_path))

    assert len(output_files) >= 2
    for file_path in output_files:
        assert Path(file_path).exists()
        assert Path(file_path).stat().st_size > 0
