import os
from itertools import chain

from engine import OUTPUT_DIR
from engine.structure import create_file

from config.templates import assoc_table_template, model_template, models_import_template

def create_model_file(project_name, class_name, class_code, output_dir="models"):
    model_dir = os.path.join(os.getcwd(), OUTPUT_DIR, project_name, output_dir)
    if not os.path.exists(model_dir):
        os.makedirs(model_dir, exist_ok=True)
    file_path = os.path.join(model_dir, f"{class_name.lower()}.py")
    with open(file_path, "w") as f:
        f.write(class_code)


def sa_type(dataType, dataTypeSize):
    match [dataType, dataTypeSize]:
        case ["int", ("" | None)]:
            return "Integer"
        case ["float", ("" | None)]:
            return "Float"
        case [("charn" | "varcharn"), size]:
            return f"String({size})"
        case ["date", ("" | None)]:
            return "Date"
        case ["custom", sqlType]:
            return sqlType
        case _:
            return None


def type_case(s: str):
    return "".join(w.capitalize() for w in s.split("_"))


def generate_class_code(table_id, attributes, relationships, tables_by_id, assoc=False):
    table = tables_by_id[table_id]
    table_name = table["name"]
    if assoc:
        attr_types = (
            sa_type(attr["dataType"], attr["dataTypeSize"]) for attr in attributes
        )
        attr_types = sorted(
            set(t[: t.find("(")] if "(" in t else t for t in attr_types)
        )

        table_name = table_name.replace("-", "_")
        other_name = lambda attr: tables_by_id[attr["references"][0]["tableId"]]["name"]
        return assoc_table_template.format(imported_types=', '.join(attr_types), table_name=table_name, attrs=',\n    '.join(f'''Column('{attr["names"][0]}', {sa_type(attr["dataType"], attr["dataTypeSize"])}, ForeignKey('{other_name(attr)}.id', onupdate='CASCADE', ondelete='CASCADE'), primary_key=True)''' for attr in attributes if attr["fk"]))
    attr_types = set()
    columns = []
    foreign_keys = []
    assoc_tables = []
    deffered_rels = set()
    for attr in attributes:
        attr_name = attr["names"][0]
        if attr_name == "id":
            continue
        attr_type = sa_type(attr["dataType"], attr["dataTypeSize"])
        bracket_at = attr_type.find("(")
        attr_types.add(attr_type[:bracket_at] if bracket_at != -1 else attr_type)
        if attr["fk"]:
            foreign_keys.append(
                f"    {attr_name} = Column({attr_type}, ForeignKey('{tables_by_id[attr["references"][0]["tableId"]]["name"]}.id'), nullable={attr["optional"]})"
            )
        else:
            columns.append(
                f"""    {attr_name} = Column({attr_type}{
                ', primary_key=True' if attr['pkMember'] else ''}{
                f', nullable={attr["optional"]}'}{
                ', unique=True' if attr['soloUnique'] else ''})"""
            )

    columns.append("")
    columns.extend(foreign_keys)

    if relationships[table_id]:
        columns.append("")
    for rel in relationships[table_id]:
        from_table = tables_by_id[rel["from"]["tableId"]]["name"]
        to_table = tables_by_id[rel["to"]["tableId"]]["name"]
        match rel["type"]:
            case "oo":
                columns.append(
                    f"    {to_table} = relationship('{type_case(to_table)}', back_populates='{from_table}s', cascade='all, delete-orphan', unique=True)"
                )
            case "mo":
                columns.append(
                    f"    {to_table}s = relationship('{type_case(to_table)}', back_populates='{from_table}', cascade='all, delete-orphan')"
                )
                if rel["from"]["tableId"] == table_id:
                    to_name = rel["to"]["name"]
                    deffered_rels.add(
                        f"""from models.{to_name} import {type_case(to_name)}
{type_case(to_name)}.{table_name} = relationship('{type_case(table_name)}', back_populates='{to_name}s')"""
                    )
            case "om":
                if rel["to"]["tableId"] == table_id:
                    columns.append(
                        f"    {to_table} = relationship('{type_case(to_table)}', back_populates='{from_table}s')"
                    )
                else:
                    columns.append(f"    {to_table} = None")
            case "mm":
                assoc_tables.append((from_table, to_table))
                is_parent = from_table == table_name
                if rel["from"]["tableId"] == table_id:
                    columns.append(
                        f"""    {to_table if is_parent else from_table}s = relationship('{type_case(to_table if is_parent else from_table)}', viewonly=False, secondary={from_table}_{to_table}, back_populates='{from_table if is_parent else to_table}s')"""
                    )
                else:
                    columns.append(
                        f"""    {to_table if is_parent else from_table}s = None"""
                    )

    for rel in relationships[table_id]:
        if rel["type"] == "mm" and rel["from"]["tableId"] == table_id:
            to_name = rel["to"]["name"]

            deffered_rels.add(
                f"""from models.{to_name} import {type_case(to_name)}
{type_case(to_name)}.{table_name}s = relationship('{type_case(table_name)}', viewonly=False, secondary={table_name}_{to_name}, back_populates='{to_name}s')"""
            )
    required_attrs = [
        attr["names"][0]
        for attr in attributes
        if attr["names"][0] != "id" and not attr["optional"]
    ]
    optional_attrs = [attr["names"][0] for attr in attributes if attr["optional"]]

    ctor_args = f"{''.join(attr+', ' for attr in required_attrs)}{''.join(attr+'=None, ' for attr in optional_attrs)}"

    model_code = model_template.format(imported_types=', '.join(sorted(attr_types)), imported_models='\n'.join(f'from models.{ft}_{tt} import {ft}_{tt}' for ft, tt in assoc_tables), class_name=type_case(table_name), table_name=table_name, ctor_args=ctor_args, attrs=', '.join(f'{attr}={attr}' for attr in chain(required_attrs, optional_attrs)),columns='\n'.join(columns), deffered_rels='\n\n'.join(sorted(deffered_rels)))
    return model_code


def generate_models(project_name, data):
    tables_by_id = {}
    relationships = {}
    for shape in data["shapes"]:
        if shape["type"] == "Table":
            table = shape["details"]
            tables_by_id[table["id"]] = table
            relationships[table["id"]] = []

    for shape in data["shapes"]:
        if shape["type"] == "Table":
            table = shape["details"]
            attributes = table["attributes"]

            if table["name"].count("-") == 2:
                parts = table["name"].split("-")
                table["name"] = "-".join(parts[:-1])
                attributes = [attr for attr in attributes if attr["fk"]]
                attr1, attr2 = attributes[0], attributes[1]
                assert attr1["fk"] and attr2["fk"]
                table_id1 = attr1["references"][0]["tableId"]
                table_id2 = attr2["references"][0]["tableId"]

                if parts[0] != tables_by_id[table_id1]["name"]:
                    table_id1, table_id2 = table_id2, table_id1

                rel = {
                    "type": parts[-1],
                    "from": {
                        "tableId": table_id1,
                        "name": tables_by_id[table_id1]["name"],
                        "attributeId": attr["id"],
                    },
                    "to": {
                        "tableId": table_id2,
                        "name": tables_by_id[table_id2]["name"],
                        "attributeId": attr["id"],
                    },
                }
                relationships[rel["from"]["tableId"]].append(rel)
                relationships[rel["to"]["tableId"]].append(rel)
                continue

            for attr in attributes:
                if table["name"].count("-") == 2:
                    secs = table["name"].split("-")
                    table["name"] = "-".join(secs[:-1])
                    rel_type = secs[:-1]
                else:
                    rel_type = "mo"
                if attr["fk"]:
                    table_id = attr["references"][0]["tableId"]
                    rel = {
                        "type": rel_type,
                        "from": attr["references"][0],
                        "to": {"tableId": table["id"], "attributeId": attr["id"]},
                    }
                    if rel_type == "mm":
                        if relationships.get(rel["to"]["tableId"], False):
                            relationships[rel["to"]["tableId"]] = []
                        relationships[rel["to"]["tableId"]].append(rel)
                    elif rel_type == "mo":
                        attr["references"][0]["name"] = tables_by_id[
                            attr["references"][0]["tableId"]
                        ]["name"]
                        relationships[table_id].append(
                            {
                                "type": "mo",
                                "from": attr["references"][0],
                                "to": {
                                    "tableId": table["id"],
                                    "name": tables_by_id[table["id"]]["name"],
                                    "attributeId": attr["id"],
                                },
                            }
                        )
                        relationships[table["id"]].append(
                            {
                                "type": "om",
                                "from": {
                                    "tableId": table["id"],
                                    "name": tables_by_id[table["id"]]["name"],
                                    "attributeId": attr["id"],
                                },
                                "to": attr["references"][0],
                            }
                        )

    for shape in data["shapes"]:
        if shape["type"] == "Table":
            table_id = shape["details"]["id"]
            table_name = shape["details"]["name"]
            attributes = shape["details"]["attributes"]
            class_code = generate_class_code(
                table_id, attributes, relationships, tables_by_id, "-" in table_name
            )
            create_model_file(project_name, table_name.replace("-", "_"), class_code)

    create_models_init_file(
        project_name,
        [
            shape["details"]["name"]
            for shape in data["shapes"]
            if shape["type"] == "Table"
        ],
    )


def create_models_init_file(project_name, table_names):
    classes = [name for name in table_names if "-" not in name]
    model_init_file = models_import_template.format(classes=', '.join(f'"{cls}": {type_case(cls)}' for cls in classes), models_import='\n'.join(f'from models.{name.replace('-', '_')} import {type_case(name) if '-' not in name else name.replace('-', '_')}' for name in table_names))

    create_file(
        os.path.join(os.getcwd(), OUTPUT_DIR, project_name, "models", "__init__.py"),
        model_init_file,
    )
