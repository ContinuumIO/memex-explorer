import sys
import os

from jinja2 import Template
from jinja2.runtime import Context

from django.core.management.base import BaseCommand, CommandError
from polls.models import Poll

class Command(BaseCommand):
    help = 'Generate initial nginx config'

    def add_arguments(self, parser):
        parser.add_argument('source_template', nargs='+')
        parser.add_argument('nginx destination', nargs='+')

    def handle(self, *args, **options):
        raise NotImplementedError
        context = {
            'ip_addr': os.environ.get('IP_ADDR', ''),
            'hostname': os.environ.get('HOSTNAME', ''),
            'root_port': os.environ.get('ROOT_PORT', ''),
            'containers': []
        }
        with open(args[0], 'r') as f:
            template_text = f.read()
            template = Template(template_text, trim_blocks = True, lstrip_blocks = True)
            nginx_config = template.render(**context)

        with open(args[1], 'w') as f:
            f.write(nginx_config)
            f.flush() 
