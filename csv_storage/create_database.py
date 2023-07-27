import pandas as pd
from config import app, db
from models import File, Column


def add_file(filename):
    with open(f"data/{filename}", 'r') as f:
        file = File(name=filename, data=f.buffer.read())

        df = pd.read_csv(f"data/{filename}", sep=None, engine="python")
        lst = df.columns.to_list()

        columns = []
        for column in lst:
            columns.append(Column(name=column.lower(), file=file))

    db.session.add(file)
    db.session.add_all(columns)
    db.session.commit()


with app.app_context():
    db.drop_all()
    db.create_all()
    add_file("ingredients.csv")
    add_file("Netflix Userbase.csv")
