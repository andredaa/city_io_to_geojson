def get_color_for_cell_type(cell_type):
    # some cells have the type -1 - which means something like undefined?
    if cell_type == -1:
        return '#000000'
    # handle cell_type = -1
    colors_for_type = {
        0: '#373f51',  # street
        1: '#002dd5',  # residential low
        2: '#008dd5',  # residential high
        3: '#e43f0f',  # working low
        4: '#f51476',  # working high
        5: '#000000',  # unknown
        6: '#000000',  # unknown
    }

    return colors_for_type[cell_type]


def get_height_for_cell_type(cell_type):
    # some cells have the type -1 - which means something like undefined?
    if cell_type == -1:
        return 0

    heights_for_type = {
        0: 0,  # street
        1: 20,  # residential low
        2: 40,  # residential high
        3: 30,  # working low
        4: 50,  # working high
        5: 0,  # unknown
        6: 0,  # unknown
    }

    return heights_for_type[cell_type]


def get_base_height_for_cell_type(cell_type):
    # some cells have the type -1 - which means something like undefined?
    if cell_type == -1:
        return 0

    base_heigt_for_type = {
        0: 0,  # street
        1: 0,  # residential low
        2: 0,  # residential high
        3: 0,  # working low
        4: 0,  # working high
        5: 0,  # unknown
        6: 0,  # unknown
    }

    return base_heigt_for_type[cell_type]
