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
def download_file():
    print(request.endpoint)
    if request.method == "POST":
        uploaded_file = request.files['file']
        if uploaded_file:
            filename = uploaded_file.filename
            content = uploaded_file.read()
            if not content:
                return render_template("download.html", empty=True)
            uploaded_file.stream.seek(0)
            raw_data = pd.read_csv(
                uploaded_file, sep=None, engine='python')
            # print(raw_data)
            # print(pd.read_csv(io.BytesIO(content),
            #       encoding='utf8', sep=None, engine='python'))
            columns = raw_data.columns.to_list()
            file = File(name=filename, columns="; ".join(
                columns), data=content)

            try:
                db.session.add(file)
                db.session.commit()
                return redirect('/files')
            except Exception:
                return "Ошибка при загрузке файла"

            # raw_data = pd.read_csv(
            #     request.files['file'], sep=None, engine='python')
            # print(raw_data)
    return render_template("download.html", empty=False)


@app.route('/files/search', methods=['GET'])
def search(id=None):
    filename = request.values.get('file')
    print(filename)
    with db.engine.connect() as conn:
        print(conn.engine)
        query = conn.execute(
            text(
                f"SELECT * FROM file WHERE name LIKE '%{filename}%' ORDER BY id DESC"
            )).fetchall()
    return render_template("index.html", files=query)


if __name__ == "__main__":
    app.run(debug=True)
