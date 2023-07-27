from flask import make_response, request
from sqlalchemy import desc, text
from config import db
from models import File, Column, file_schema, files_schema
import pandas as pd
import io
import json


def display_all():
    name_filter = request.args.get("name")
    file_query = File.query.order_by(desc(File.id))

    if name_filter:
        file_query = file_query.filter(File.name.ilike(f"%{name_filter}%"))

    return files_schema.dump(file_query.all()), 200


def upload_file(file):
    new_file = file_schema.load(file, session=db.session)
    df = pd.read_csv(io.StringIO(file["data"]), sep=None, engine="python")
    new_file.data = bytes(file["data"], "UTF-8")
    lst = df.columns.to_list()

    columns = []
    for column in lst:
        columns.append(Column(name=column.lower(), file=new_file))

    db.session.add(new_file)
    db.session.add_all(columns)
    db.session.commit()

    return file_schema.dump(new_file), 201


def read_file(file_id):
    file = File.query.get_or_404(file_id)

    df = pd.read_csv(
        io.BytesIO(file.data),
        sep=None,
        engine="python",
    )
    df.to_sql(f"{file.name[:len(file.name) - 4]}{file_id}", con=db.engine)

    args = []
    for arg in request.args:
        column = Column.query.filter_by(
            file_id=file.id, name=arg
        ).one_or_none()
        if column:
            args.append(arg)

    query = ""
    for el in args:
        query += f" {el} LIKE '%{request.args.get(el)}%' AND"
    if args:
        query = " WHERE" + query[:len(query)-4]
    query = f"SELECT * FROM '{file.name[:len(file.name)-4]}{file_id}'" + query

    with db.engine.connect() as conn:
        resp = conn.execute(text(query)).fetchall()
        conn.execute(
            text(f"DROP TABLE '{file.name[:len(file.name) - 4]}{file_id}'")
        )

    parsed = json.dumps([dict(row._mapping) for row in resp])
    return json.loads(parsed), 200


def delete_file(file_id):
    file = File.query.get_or_404(file_id)

    db.session.delete(file)
    db.session.commit()

    return make_response(f"Файл {file.id} '{file.name}' успешно удалён", 200)
