from ..extensions import db

class Race(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    circuit = db.Column(db.String(80), nullable=False)
    date = db.Column(db.Date, nullable=False)
    season = db.Column(db.Integer, nullable=False)

    results = db.relationship("Result", back_populates="race")

    def __repr__(self) -> str:
        return '{%s: %s}' %(self.season, self.name)
