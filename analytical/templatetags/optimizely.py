"""
Optimizely template tags and filters.
"""

from __future__ import absolute_import

import re

from django.template import Library, Node, TemplateSyntaxError

from analytical.utils import is_internal_ip, disable_html, validate_setting, \
        get_required_setting


ACCOUNT_NUMBER_RE = re.compile(r'^\d{7}$')
SETUP_CODE = """<script src="//cdn.optimizely.com/js/%(account_number)s.js"></script>"""


register = Library()


@register.tag
def optimizely(parser, token):
    """
    Optimizely template tag.

    Renders Javascript code to set-up A/B testing.  You must supply
    your Optimizely account number in the ``OPTIMIZELY_ACCOUNT_NUMBER``
    setting.
    """
    bits = token.split_contents()
    if len(bits) > 1:
        raise TemplateSyntaxError("'%s' takes no arguments" % bits[0])
    return OptimizelyNode()

class OptimizelyNode(Node):
    def __init__(self):
        self.account_number = get_required_setting(
                'OPTIMIZELY_ACCOUNT_NUMBER', ACCOUNT_NUMBER_RE,
                "must be a string containing an seven-digit number")

    def render(self, context):
        html = SETUP_CODE % {'account_number': self.account_number}
        if is_internal_ip(context, 'OPTIMIZELY'):
            html = disable_html(html, self.name)
        return html


def contribute_to_analytical(add_node):
    validate_setting('OPTIMIZELY_ACCOUNT_NUMBER', ACCOUNT_NUMBER_RE,
                "must be a string containing an seven-digit number")
    add_node('head_top', OptimizelyNode)
