from flask import abort
from config import db, ma
from marshmallow import fields


class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), nullable=False)
    data = db.Column(db.BLOB, nullable=False)
    columns = db.relationship("Column", backref="file",
                              lazy=True, cascade="all,delete")

    def __repr__(self):
        return "File: " + self.name


class Column(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), nullable=False)
    file_id = db.Column(db.Integer, db.ForeignKey("file.id"), nullable=False)

    def __repr__(self):
        return self.name


def not_blank(obj):
    if not obj:
        abort(400, "Убедитесь, что файл не пустой")


def csv_format(obj):
    format = obj[len(obj) - 4:]
    if format != ".csv":
        abort(400, "Убедитесь что файл имеет формат .csv")


class FileSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = File
        load_instance = True
        sqla_session = db.session

    columns = fields.Method("show_list", dump_only=True)
    name = fields.String(validate=csv_format)
    data = fields.String(load_only=True, validate=not_blank)

    def show_list(self, obj):
        resp = []
        for column in obj.columns:
            resp.append(column.name)
        return resp


file_schema = FileSchema()
files_schema = FileSchema(many=True)
