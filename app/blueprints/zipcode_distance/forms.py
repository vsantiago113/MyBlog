from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, IntegerField
from wtforms.validators import DataRequired, Length


class ZipCodesForm(FlaskForm):
    zipcode1 = StringField('Zip Code 1', validators=[DataRequired(), Length(min=2, max=7)])
    zipcode2 = StringField('Zip Code 2', validators=[DataRequired(), Length(min=2, max=7)])
    submit = SubmitField('Submit')
