import PySimpleGUI as sg

sg.theme('DarkGrey13')

search_column = [
    [
        sg.Input(size=(36, 1), enable_events=True, key="-SEARCH-", do_not_clear=True),
        sg.Button("Search"), # Search bar
        sg.Button("Clear"), # Clears the search bar and the info box
    ],
    [
        sg.Listbox(
            values=[], enable_events=True, size=(51, 20), key="-TITLE-"
        ),
    ],
    [
        sg.Multiline(size=(51, 4), key="-METRICS-")
    ],
    [
        sg.Button("Save Result"),
        sg.Push(),
        sg.Button("Exit"),
        sg.Button("Version"),
    ],
]

result_column = [
    [
        sg.Multiline(size=(95, 30), key="-INFO-")
    ],
]

layout = [
    [
        sg.Column(search_column),
        sg.VSeperator(),
        sg.Column(result_column),
    ]
]
