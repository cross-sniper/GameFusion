# SimpleXML
import re
import os
import sys

def panic(*msgs):
    caller = sys._getframe(1).f_code.co_name  # Get the name of the caller function
    formatted_msg = f"[PANIC] {caller}: {' '.join(map(str, msgs))}"
    print(formatted_msg)
    exit(1)

def parse(content: str) -> dict:
    def parse_element(element: str) -> dict:
        tag_regex = r"<(\w+)>((?:.|\n)*?)</\1>"
        parsed = {}
        
        for match in re.finditer(tag_regex, element):
            tag, inner_content = match.groups()
            
            # Trim content and handle new lines
            inner_content = inner_content.strip()
            
            if re.search(tag_regex, inner_content):
                # Nested tags
                parsed[tag] = parse_element(inner_content)
            else:
                # Single level tags
                if tag in parsed:
                    if isinstance(parsed[tag], list):
                        parsed[tag].append(inner_content)
                    else:
                        parsed[tag] = [parsed[tag], inner_content]
                else:
                    parsed[tag] = inner_content
        
        # Convert multiline text into a list of entries if needed
        for tag in parsed:
            if isinstance(parsed[tag], str):
                # Split on newline and remove empty lines
                entries = [line.strip() for line in parsed[tag].splitlines() if line.strip()]
                if len(entries) > 1:
                    parsed[tag] = entries
        
        return parsed

    return parse_element(content)

def loadFile(filename: str) -> dict:
    if not os.path.isfile(filename):
        panic("not a file", filename)

    with open(filename) as f:
        return parse(f.read())

if __name__ == "__main__":
    if len(sys.argv) != 2:
        panic("Usage: script.py <filename>")
    
    filename = sys.argv[1]
    parsed_content = loadFile(filename)
    print(parsed_content)
