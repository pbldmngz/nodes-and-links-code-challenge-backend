from dataclasses import dataclass
from defaultlist import defaultlist
from collections import defaultdict


@dataclass
class Node:
    start_date: str = None
    end_date: str = None
    idx: int = None
    days: int = 0
    origin: str = True
    connected_nodes: list = None


def _transform_array_to_objects(matrix: list) -> list:
    """
    Transform the array of dicts into an array of objects

    :param array: The array of list of dicts
    :return: The array of objects
    """
    new_matrix = []
    for array in matrix:
        new_matrix.append([Node(**node) for node in array])
    return new_matrix


# This will elongate the influence on a Node's debt
# [300, -250, -200, -150, -100, -50, 0]
# If the debt is 0, then the cell is not in debt and it can be assigned a node
@dataclass
class Cell:
    node: Node = None
    debt: int = 0


def _generate_position_matrix(
    input_matrix: list, tutorial_mode: bool = False
) -> list:
    """
    Create a matrix that calculates the space used by a node based on it's days
    and "reserves" it so that no other node can be placed
    there (to avoid overlapping).

    This is done using a "debt" system, so the space is "reserved" by the
    node and "pays" back for the next column until it's debt is 0.

    :return: The matrix
    """

    unlimited_matrix = defaultlist(lambda: defaultlist(lambda: Cell()))
    matrix = _transform_array_to_objects(input_matrix)

    for day_idx, day_nodes in enumerate(matrix):
        # This could maybe be replaced by a dict or a set for eficiency
        skipped_rows = set()

        for node_idx, node in enumerate(day_nodes):
            # If the cell is in debt, then we skip it
            free_cell_idx = 0
            while free_cell_idx in skipped_rows:
                free_cell_idx += 1

            cell_debt = unlimited_matrix[day_idx][node_idx].debt
            node_debt = -node.days

            if cell_debt < 0:
                # This is just the "shadow" of the debt
                # It can be considered as reserved space
                unlimited_matrix[day_idx][free_cell_idx] = Cell(
                    debt=cell_debt, node=Node(origin=False)
                )
                skipped_rows.add(node_idx)
                day_nodes.append(node)
                if tutorial_mode:
                    print(
                        f"Debt of {cell_debt} on ({day_idx, node_idx}) - Added node {node.days} on ({day_idx}, {free_cell_idx})"
                    )
                    print(
                        f" - Returned NEW node back to queue in position ({day_idx, len(day_nodes)})"
                    )
                continue

            extra_column_count = 0

            if node_debt < 0:
                if tutorial_mode:
                    print(" * Currently skipped rows:", skipped_rows)

                if cell_debt == -1:
                    unlimited_matrix[day_idx][free_cell_idx] = Cell(
                        node=node
                    )

                    skipped_rows.add(free_cell_idx)

                while node_debt < 0:
                    # Project the "shadow" of the debt to the next
                    # affected Cells - horizontally
                    tmp_column_idx = day_idx + extra_column_count

                    # This is just the "shadow" of the debt
                    # It can be considered as reserved space
                    if extra_column_count > 0:
                        test_node = Node(
                            idx=node.idx,
                            days=node.days,
                            start_date=node.start_date,
                            end_date=node.end_date,
                            origin=False,
                        )
                    else:
                        test_node = node

                    extra_column_count += 1
                    new_cell = Cell(node=test_node, debt=node_debt)
                    unlimited_matrix[tmp_column_idx][node_idx] = new_cell
                    skipped_rows.add(node_idx)

                    if tutorial_mode:
                        print(
                            f"Debt of {node_debt} on ({day_idx, node_idx}) - Added node {node.days} on ({tmp_column_idx}, {node_idx})"
                        )
                    node_debt = node_debt + 1
            else:
                if tutorial_mode:
                    print(
                        f"\n > No debt on ({day_idx}, {node_idx}), "
                        "currently skipped rows: {skipped_rows}"
                    )
                unlimited_matrix[day_idx][free_cell_idx] = Cell()
                skipped_rows.add(free_cell_idx)
            if tutorial_mode:
                # print(f"\nDEBT MATRIX ON ({day_idx, node_idx}):")
                # get_debt_matrix(unlimited_matrix)

                print(f"\nDAYS MATRIX ON ({day_idx, node_idx}):")
                get_attribute_matrix(unlimited_matrix, "idx")

                print("-" * 50)
        if tutorial_mode:
            print("=" * 75)
            print(f"END OF ROW {day_idx}")
            print("=" * 75)

    return unlimited_matrix


def _filter_only_shadow_nodes(matrix: list) -> list:
    """
    Filter the matrix to only show the shadow nodes

    :param matrix: The matrix to filter
    :return: The filtered matrix
    """
    new_matrix = defaultlist(lambda: defaultlist(lambda: Cell()))
    delete_list = []
    for idx_row, row in enumerate(matrix):
        for idx_cell, cell in enumerate(row):
            if cell.node and cell.node.origin:
                new_matrix[idx_row][idx_cell] = cell
            else:
                new_matrix[idx_row][idx_cell] = Cell()
        if not any([ce.node for ce in new_matrix[idx_row]]):
            delete_list.append(idx_row)

    for idx in delete_list[::-1]:
        new_matrix.pop(idx)

    return new_matrix


def _rotate_matrix(matrix: list) -> list:
    """
    Rotate the matrix by 90 degrees

    :param matrix: The matrix to rotate
    :return: The rotated matrix
    """
    return [
        [row[i] for row in matrix] for i in range(max(map(len, matrix)))
    ]


def group_nodes_by_dates(info_nodes: list) -> dict:
    """Group the nodes by their dates"""

    grouped_nodes = defaultdict(list)
    grouped_nodes_days = defaultdict(list)

    for node in info_nodes:
        grouped_nodes[node["start_date"]].append(node)
        grouped_nodes_days[node["start_date"]].append(node["days"])

    grouped_nodes = [grouped_nodes[key] for key in grouped_nodes]
    grouped_nodes_days = [
        grouped_nodes_days[key] for key in grouped_nodes_days
    ]

    return grouped_nodes, grouped_nodes_days


def get_position_matrix(matrix: list) -> list:
    """
    Get the base position of the nodes in the matrix

    :param matrix: Matrix of nodes grouped (in list) by day
    :return: The base position matrix
    """
    unlimited_matrix = _generate_position_matrix(matrix)
    filtered_matrix = _filter_only_shadow_nodes(unlimited_matrix)
    rotated_matrix = _rotate_matrix(filtered_matrix)

    return rotated_matrix


# ---------------------------- VISUALS --------------------------------


def get_debt_matrix(matrix: list) -> list:
    for row in matrix:
        for cell in row:
            print(cell.debt, end=(" " * (5 - len(str(cell.debt)))))
        print()
    print()


def get_attribute_matrix(matrix: list, property: str = "days") -> list:
    for row in matrix:
        for cell in row:
            if cell.node:
                print(
                    getattr(cell.node, property),
                    end=(
                        " " * (5 - len(str(getattr(cell.node, property))))
                    ),
                )
            else:
                print(" " * 5, end="")
        print()
