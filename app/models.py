from app import db

class Computer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    computername = db.Column(db.String(64), index=True, unique=True)
    activeusers = db.Column(db.String(256), index=True, unique=True)
    inactiveusers = db.Column(db.String(256), index=True, unique=True)
    timestamp = db.Column(db.DateTime)
    
    def __repr__(self):
    	return '<Computer %r>' % (self.computername)