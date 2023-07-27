from flask import render_template, request, redirect
from sqlalchemy import desc, text
import pandas as pd
import io
import config
from config import db
from models import File, Column


app = config.connex_app
app.add_api("swagger.yaml")


@app.route("/", methods=["GET"])
@app.route("/files")
def files():
    files = File.query.order_by(desc(File.id)).all()
    return render_template("index.html", files=files)


@app.route("/files/upload", methods=["POST", "GET"])
def upload_file():
    empty = False
    is_csv = False

    if request.method == "POST":
        uploaded_file = request.files["file"]

        if uploaded_file:
            filename = uploaded_file.filename
            content = uploaded_file.read()
            format = filename[len(filename) - 4:]

            if not content:
                empty = True

            if format != ".csv":
                is_csv = True

            if empty or is_csv:
                return render_template(
                    "upload.html", empty=empty, is_csv=is_csv
                )

            file = File(name=filename, data=content)

            uploaded_file.stream.seek(0)
            df = pd.read_csv(uploaded_file, sep=None, engine="python")
            lst = df.columns.to_list()

            columns = []
            for column in lst:
                columns.append(Column(name=column.lower(), file=file))

            try:
                db.session.add(file)
                db.session.add_all(columns)
                db.session.commit()

                return redirect("/files")
            except Exception:
                return render_template("upload.html", empty=True, is_csv=True)

    return render_template("upload.html", empty=empty, is_csv=is_csv)


@app.route("/files/<int:file_id>/delete")
def delete_file(file_id):
    file = File.query.get_or_404(file_id)

    try:
        db.session.delete(file)
        db.session.commit()

        return redirect("/files")
    except Exception:
        return render_template("index.html", err=True)


@app.route("/files/search", methods=["GET"])
def search():
    name_filter = request.args.get("file")
    file_query = File.query.order_by(desc(File.id))

    if name_filter:
        file_query = file_query.filter(File.name.ilike(f"%{name_filter}%"))

    return render_template("index.html", files=file_query.all())


@app.route("/files/search/<int:file_id>", methods=["GET"])
def search_file(file_id):
    file = File.query.get_or_404(file_id)

    df = pd.read_csv(
        io.BytesIO(file.data),
        sep=None,
        engine="python",
    )
    df.to_sql(f"{file.name[:len(file.name) - 4]}{file_id}", con=db.engine)

    with db.engine.connect() as conn:
        query = conn.execute(
            text(f"SELECT * FROM '{file.name[:len(file.name) - 4]}{file_id}'")
        ).fetchall()
        conn.execute(
            text(f"DROP TABLE '{file.name[:len(file.name) - 4]}{file_id}'"))

    return render_template("file.html", file=file, query=query)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
