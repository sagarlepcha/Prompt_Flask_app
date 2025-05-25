from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Prompt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(500), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # New column for categories

    def __repr__(self):
        return f'<Prompt {self.text} - {self.category}>'
