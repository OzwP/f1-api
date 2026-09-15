from ..extensions import db

class Driver(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'))

    results = db.relationship("Result", back_populates="driver")

    def __repr__(self) -> str:
        return '{%s : %s}' %(self.name, self.team_id)