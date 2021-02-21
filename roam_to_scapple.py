import argparse


DEFAULT_FONT_SIZE = 12
DEFAULT_WIDTH = 500
DEFAULT_Y_SPACING = 40
NOTE = """\
        <Note ID="{id}" FontSize="{font_size}" Position="{position}" Width="{width}">  # noqa
            <Appearance>
                <Alignment>Left</Alignment>
            </Appearance>
            <String>{string}</String>
        </Note>\
"""


parser = argparse.ArgumentParser()
parser.add_argument("input")
args = parser.parse_args()


with open(args.input) as f:
    data = [l.strip() for l in f.readlines()]

notes = []
for id, string in enumerate(data, start=0):
    y = id * DEFAULT_Y_SPACING
    note = NOTE.format(
        id=id,
        font_size=DEFAULT_FONT_SIZE,
        position=f"{0},{y}",
        width=DEFAULT_WIDTH,
        string=string,
    )
    notes.append(note)

with open("scapple_template.xml") as f:
    template = f.read()

output = template.format(notes="\n".join(notes))
print(output)
