"""
Github flavored markdown
~~~~~~~~~~~~~~~~~~~~~~~~

https://github.github.com/gfm

Unlike other extensions, GFM provides a self-contained subclass of ``Markdown``
with parser and renderer already set.
User may also use the parser and renderer as bases for further extension.

Example usage::

    from marko.ext.gfm import GFMarkdown
    print(GFMarkdown()(text))

"""
import re
from marko import HTMLRenderer, Parser, Markdown
from . import elements


class GFMParser(Parser):

    def __init__(self, *extras):
        super(GFMParser, self).__init__(*extras)

        self.add_element(elements.Document, True)
        self.add_element(elements.Paragraph, True)
        self.add_element(elements.AutoLink, True)
        self.add_element(elements.LinkRefDef, True)
        self.add_element(elements.ListItem, True)
        self.add_element(elements.Strikethrough)
        self.add_element(elements.Table)
        self.add_element(elements.TableRow)
        self.add_element(elements.TableCell)


class GFMRenderer(HTMLRenderer):
    tagfilter = re.compile(r'<(title|texarea|style|xmp|iframe|noembed|noframes'
                           r'|script|plaintext)', flags=re.I)

    def render_paragraph(self, element):
        children = self.render_children(element)
        template = '<input{} disabled="" type="checkbox">{}'
        if hasattr(element, 'checked'):
            children = template.format(
                ' checked=""' if element.checked else '',
                children
            )
        if element._tight:
            return children
        else:
            return '<p>{}</p>\n'.format(children)

    def render_strikethrough(self, element):
        return '<del>{}</del>'.format(self.render_children(element))

    def render_html_block(self, element):
        return self.tagfilter.sub(r'&lt;\1', element.children)

    def render_table(self, element):
        (header, *body) = element.children
        theader = '<thead>\n{}</thead>'.format(self.render(header))
        tbody = ''
        if body:
            tbody = '\n<tbody>\n{}</tbody>'.format(
                ''.join(self.render(row) for row in body))
        return '<table>\n{}{}</table>'.format(theader, tbody)

    def render_table_row(self, element):
        return '<tr>\n{}</tr>\n'.format(self.render_children(element))

    def render_table_cell(self, element):
        tag = 'th' if element.header else 'td'
        align = ''
        if element.align:
            align = ' align="{}"'.format(element.align)
        return '<{tag}{align}>{children}</{tag}>\n'.format(
            tag=tag, children=self.render_children(element), align=align)


class GFMarkdown(Markdown):

    def __init__(self):
        self.parser = GFMParser()
        self.renderer = GFMRenderer()
