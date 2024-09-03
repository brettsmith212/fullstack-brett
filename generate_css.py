import sys
import json

def class_name_mapping(original_name):
    mapping = {
        'Keyword': 'kw',
        'ControlFlow': 'cf',
        'Function': 'fn',
        'String': 'st',
        'BuiltIn': 'bu',
        'Operator': 'op',
        'Variable': 'va',
        'Number': 'dv',  # Assuming 'dv' stands for 'decimal value'
        'Comment': 'co',
        'CommentVar': 'cv',
        'Constant': 'cn',
        'SpecialChar': 'sc',
        'DecVal': 'dv',
        'BaseN': 'bn',
        'Float': 'fl',
        'Char': 'ch',
        'VerbatimString': 'vs',
        'Alert': 'al',
        'Error': 'er',
        'Warning': 'wa',
        'Information': 'in',
        'Annotation': 'an'
    }
    return mapping.get(original_name, original_name.lower())

def generate_css(json_input):
    data = json.load(json_input)
    css = []
    for class_name, styles in data['text-styles'].items():
        mapped_class_name = class_name_mapping(class_name)
        css_properties = []
        for property_name, value in styles.items():
            if value is not None:
                if property_name == 'text-color':
                    css_properties.append(f'color: {value}')
                elif property_name == 'background-color':
                    css_properties.append(f'background-color: {value}')
                elif property_name == 'bold' and value:
                    css_properties.append('font-weight: bold')
                elif property_name == 'italic' and value:
                    css_properties.append('font-style: italic')
                elif property_name == 'underline' and value:
                    css_properties.append('text-decoration: underline')
        if css_properties:
            css.append(f'.sourceCode .{mapped_class_name} {{ {"; ".join(css_properties)}; }}')

    # Add general code block styles
    css.extend([
        'pre.sourceCode, pre:not([class]), pre > code {',
        '    background-color: #f5f5f5;',
        '    padding: 1em 1em 2em 1em;',
        '    border-radius: 4px;',
        '    font-family: "APL386", monospace;',
        '    font-size: 14px;',
        '    line-height: 1.2;',
        '    max-width: 100%;',
        '    overflow-x: auto;',
        '    white-space: pre;',
        '    word-wrap: normal;',
        '    color: #333;',
        '    margin-bottom: 1em;',
        '}',
        '',
        'pre.sourceCode, pre:not([class]), pre > code {',
        '    max-width: 100%;',
        '    overflow-x: auto;',
        '    white-space: pre-wrap;',
        '    word-wrap: break-word;',
        '}',
        '',
        '.sourceCode {',
        '    max-width: 100%;',
        '    overflow-x: auto;',
        '}',
        '',
        '.sourceCode pre {',
        '    white-space: pre-wrap;',
        '    word-wrap: break-word;',
        '}',
        'code.sourceCode, pre:not([class]) > code {',
        '    display: block;',
        '    padding: 0;',
        '    background-color: transparent;',
        '}',
        '',
        '.sourceCode .sourceLine, pre:not([class]) > code > span {',
        '    display: inline-block;',
        '    width: auto;',  # Change from 100% to auto
        '    min-width: 100%;', # Ensure it's at least as wide as the container
        '    margin: 0;',
        '    padding: 0;',
        '}',
        '',
        '/* Inline code styling */',
        'code:not([class]):not(pre > *) {',
        '    background-color: #f5f5f5;',
        '    padding: 2px 4px;',
        '    border-radius: 3px;',
        '    font-family: "APL386", monospace;',
        '    font-size: 0.9em;',
        '    color: #d14;',
        '}',
        '',
        '@media (prefers-color-scheme: dark) {',
        '    pre.sourceCode, pre:not([class]), pre > code {',
        '        background-color: #2a2a2a;',
        '        color: #f8f8f2;',
        '    }',
        '    code:not([class]):not(pre > *) {',
        '        background-color: #2a2a2a;',
        '        color: #e6db74;',
        '    }',
        '}'
    ])



    return '\n'.join(css)

if __name__ == '__main__':
    print(generate_css(sys.stdin))
