import sqlalchemy as db
engine = db.create_engine('sqlite:///users.sqlite')
connection = engine.connect()
metadata = db.MetaData()

emp = db.Table('users', metadata,
              db.Column('Id', db.Integer()),
              db.Column('Url', db.String(255)),
              )

metadata.create_all(engine) #Creates the table