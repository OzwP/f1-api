from ..app import db

class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    car = db.Column(db.String(30))
    
    driver = db.relationship("Driver", backref='team')
    
    motor_name = db.Column(db.String(80), db.ForeignKey('motor.name'))
    
    def __repr__(self) -> str:
        return '{%s: %s}' %(self.name, self.motor_name)