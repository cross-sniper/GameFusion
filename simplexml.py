import re
import os
import sys


def panic(*msgs):
    """Print an error message and exit the program."""
    caller = sys._getframe(1).f_code.co_name
    formatted_msg = f"[PANIC] {caller}: {' '.join(map(str, msgs))}"
    print(formatted_msg, file=sys.stderr)
    sys.exit(1)


def parse(content: str) -> dict:
    """Parse XML content from a string and return a dictionary representation."""

    def parse_element(element: str) -> dict:
        tag_regex = r"<(\w+)>(.*?)</\1>"
        parsed = {}

        for match in re.finditer(tag_regex, element, re.DOTALL):
            tag, inner_content = match.groups()
            inner_content = inner_content.strip()

            if re.search(tag_regex, inner_content, re.DOTALL):
                parsed[tag] = parse_element(inner_content)
            else:
                if tag in parsed:
                    if isinstance(parsed[tag], list):
                        parsed[tag].append(inner_content)
                    else:
                        parsed[tag] = [parsed[tag], inner_content]
                else:
                    parsed[tag] = inner_content

        for tag, content in parsed.items():
            if isinstance(content, str):
                entries = [
                    line.strip() for line in content.splitlines() if line.strip()
                ]
                if len(entries) > 1:
                    parsed[tag] = entries

        return parsed

    return parse_element(content)


def load_file(filename: str) -> dict:
    """Load an XML file and parse its content."""
    if not os.path.isfile(filename):
        panic("File not found:", filename)

    with open(filename, "r", encoding="utf-8") as f:
        return parse(f.read())


def main():
    """Main function to handle command-line arguments and parse XML file."""
    if len(sys.argv) != 2:
        panic("Usage: script.py <filename>")

    filename = sys.argv[1]
    parsed_content = load_file(filename)
    print(parsed_content)


if __name__ == "__main__":
    main()
