from flask.ext.wtf import Form
from wtforms import StringField, BooleanField
from wtforms.validators import DataRequired

class SearchForm(Form):
	findcomputer = StringField('findcomputer', validators=[DataRequired()])

class AddComputerForm(Form):
	addcomputer = StringField('addcomputer', validators=[DataRequired()])