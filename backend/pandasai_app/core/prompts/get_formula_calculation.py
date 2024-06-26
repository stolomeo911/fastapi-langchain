import jinja2
import os
from pathlib import Path


class PromptGenerator:
    def __init__(self, agent, template_path='prompt_template.html'):
        self.agent = agent
        self.template_path = template_path
        current_dir_path = Path(__file__).parent
        path_to_template = os.path.join(current_dir_path, "templates")
        self.template_env = jinja2.Environment(loader=jinja2.FileSystemLoader(path_to_template))

    def create_prompt(self, context, template):
        template = self.template_env.get_template(template)
        prompt_html = template.render(context)
        return prompt_html