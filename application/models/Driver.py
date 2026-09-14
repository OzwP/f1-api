from ..extensions import db

class Driver(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    wins = db.Column(db.Integer)
    team_id = db.Column(db.Integer, db.ForeignKey('team.id'))

    def __repr__(self) -> str:
        return '{%s : %s}' %(self.name, self.team_id)