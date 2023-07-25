from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc, text
import pandas as pd
import io


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///files.db'
db = SQLAlchemy(app)


class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    columns = db.Column(db.String(200), nullable=False)
    data = db.Column(db.BLOB, nullable=False)

    def __repr__(self):
        return "File: " + self.name


@app.route('/', methods=['GET'])
@app.route('/files')
def files():
    files = File.query.order_by(desc(File.id)).all()
    return render_template("index.html", files=files)


@app.route('/files/upload', methods=['POST', 'GET'])
def upload_file():
    empty = False
    is_csv = False

    if request.method == "POST":
        uploaded_file = request.files['file']

        if uploaded_file:
            filename = uploaded_file.filename
            content = uploaded_file.read()
            format = filename[len(filename)-4:]

            if not content:
                empty = True

            if format != ".csv":
                is_csv = True

            if empty or is_csv:
                return render_template(
                    "upload.html", empty=empty, is_csv=is_csv
                )

            uploaded_file.stream.seek(0)
            raw_data = pd.read_csv(uploaded_file, sep=None, engine='python')
            columns = raw_data.columns.to_list()
            file = File(
                name=filename,
                columns="; ".join(columns),
                data=content
            )

            try:
                db.session.add(file)
                db.session.commit()
                return redirect('/files')
            except Exception:
                return render_template("upload.html", empty=True, is_csv=True)

    return render_template("upload.html", empty=empty, is_csv=is_csv)


@app.route('/files/<int:id>/delete')
def delete_file(id):
    file = db.session.get(File, id)

    try:
        db.session.delete(file)
        db.session.commit()
        return redirect('/files')
    except Exception:
        return render_template("index.html", err=True)


@app.route('/files/search', methods=['GET'])
def search():
    name = request.values.get('file')

    with db.engine.connect() as conn:
        query = conn.execute(text(
            f"SELECT * FROM file WHERE name LIKE '%{name}%' ORDER BY id DESC"
        )).fetchall()

    return render_template("index.html", files=query)


@app.route('/files/search/<int:id>', methods=['GET'])
def search_file(id=None):
    file = db.session.get(File, id)
    col = file.columns.split("; ")
    df = pd.read_csv(
        io.BytesIO(file.data),
        encoding='utf8',
        sep=None,
        engine='python'
    )
    df.to_sql(f'{file.name[:len(file.name) - 4]}{id}', con=db.engine)

    with db.engine.connect() as conn:
        query = conn.execute(
            text(f"SELECT * FROM '{file.name[:len(file.name) - 4]}{id}'")
        ).fetchall()
        conn.execute(
            text(f"DROP TABLE '{file.name[:len(file.name) - 4]}{id}'"))

    return render_template("file.html", file=file, columns=col, query=query)


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
