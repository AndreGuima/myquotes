from pathlib import Path

from jinja2 import Environment, FileSystemLoader

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"

env = Environment(
    loader=FileSystemLoader(TEMPLATES_DIR),
    autoescape=True,
)


def render_template(template_name: str, context: dict) -> str:
    template = env.get_template(template_name)
    return template.render(**context)
