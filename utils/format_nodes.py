from collections import defaultdict
from datetime import datetime
from utils.position_matrix import get_position_matrix


def str_to_date(date: str) -> datetime:
    """Convert a string to a datetime object"""
    return datetime.strptime(date, "%d/%m/%Y")


def add_info_to_connected_nodes(dates: list) -> list:
    """Add the info to the connected nodes"""
    info = []
    dates = sorted(dates, key=lambda x: x[0])

    # Remember the minimum and maximum dates
    min_date = str_to_date(dates[0][1])
    max_date = str_to_date(dates[0][2])

    for idx, start_date, end_date in dates:
        # Get the minimum and maximum dates in this list
        if str_to_date(start_date) < min_date:
            min_date = str_to_date(start_date)
        if str_to_date(end_date) > max_date:
            max_date = str_to_date(end_date)

        # If it's a single day, make it worth like 1 day
        number_of_days = get_date_range_in_days(start_date, end_date)
        if number_of_days == 0:
            number_of_days = 1

        info.append(
            {
                "start_date": start_date,
                "end_date": end_date,
                "idx": int(idx) - 1,
                "days": number_of_days,
            }
        )
    return info


def find_conected_nodes(matrix: list) -> dict:
    """Find the nodes that are connected to each other in the matrix"""
    # Create a dictionary to store the nodes
    connected_nodes = defaultdict(list)
    # Iterate over the matrix
    for row_number, row in enumerate(matrix):
        connected_nodes[row_number].append(row_number)
        for column_number, value in enumerate(row):
            if int(value) == 0:
                continue
            connected_nodes[row_number].append(column_number)

    return connected_nodes


def cytoscape_format_edges(connected_nodes: dict) -> list:
    """
    Format the connected nodes into a list of dictionaries,
    in a format accepted by elements from Cytoscape
    """
    formated_nodes = []
    for key in connected_nodes:
        for idx in connected_nodes[key][1:]:
            formated_nodes.append(
                {
                    "data": {
                        "source": key,
                        "target": idx,
                        "id": f"{key}-{idx}",
                    },
                    "group": "edges",
                }
            )

    return formated_nodes


def cytoscape_format_nodes(rotated_matrix: list) -> list:
    """
    Format the nodes into a list of dictionaries,
    in a format accepted by elements from Cytoscape
    """
    formatted_nodes = []
    for y, row in enumerate(rotated_matrix):
        for x, cell in enumerate(row):
            if cell.node and cell.node.origin:

                # Somehow this is still creating a reference
                # new_item = dict(DEFAULT_CYTOSCAPE_NODE.copy())
                # So I have to do this
                new_item = {
                    "data": {"id": 0},
                    "position": {"x": 0, "y": 0},
                    "group": "default",
                    "removed": False,
                    "selected": False,
                    "selectable": True,
                    "locked": False,
                    "grabbed": False,
                    "grabbable": False,
                    "classes": "",
                }
                new_item["data"]["id"] = cell.node.idx
                new_item["data"]["start_date"] = cell.node.start_date
                new_item["data"]["end_date"] = cell.node.end_date
                new_item["data"]["days"] = cell.node.days

                width = (cell.node.days * 100) - 20
                new_item["data"]["width"] = width
                new_item["position"]["x"] = x * 100 + width / 2
                new_item["position"]["y"] = y * 100
                new_item["group"] = "nodes"

                formatted_nodes.append(new_item)

    return formatted_nodes


# ---------------------------- AFTER ---------------------------- #


def get_date_range_in_days(start_date: str, end_date: str) -> int:
    """Get the day count between the start and end date"""

    start_date = str_to_date(start_date)
    end_date = str_to_date(end_date)
    days = (end_date - start_date).days

    return days


def group_nodes_by_dates(info_nodes: list) -> dict:
    """Group the nodes by their dates"""
    grouped_nodes = defaultdict(list)

    for node in info_nodes:
        grouped_nodes[node["start_date"]].append(node)
    grouped_nodes = [grouped_nodes[key] for key in grouped_nodes]

    return grouped_nodes


# The important method!
def format_nodes(
    raw_adjacency_matrix: list, raw_dates_matrix: list
) -> list:
    """
    It's supposed to get the data from already created lists
    1: Matrix of connections (adjacency matrix)
    2: Dates (idx, start_date, end_date)
    """

    connected_nodes = find_conected_nodes(raw_adjacency_matrix)
    cytoscape_edges = cytoscape_format_edges(connected_nodes)

    info_nodes = add_info_to_connected_nodes(raw_dates_matrix)
    nodes_by_dates = group_nodes_by_dates(info_nodes)

    position_matrix = get_position_matrix(nodes_by_dates)
    cytoscape_nodes = cytoscape_format_nodes(position_matrix)

    return cytoscape_nodes + cytoscape_edges
