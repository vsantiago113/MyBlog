from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length
from flask_wtf.file import FileField, FileAllowed, FileRequired
from flask_uploads import IMAGES


class AddProductForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=3, max=256)])
    description = TextAreaField('Description')
    discount_price = StringField('Discount Price', validators=[DataRequired(), Length(min=2, max=16)])
    regular_price = StringField('Regular Price', validators=[DataRequired(), Length(min=2, max=16)])
    image_name = FileField('Feature Image', validators=[FileRequired(message='An image is required!'),
                                                        FileAllowed(IMAGES, 'File is not a valid image!')])
    product_url = StringField('Product URL', validators=[DataRequired(), Length(min=6, max=256)])
    submit = SubmitField('Submit')


class EditProductForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=3, max=256)])
    description = TextAreaField('Description')
    discount_price = StringField('Discount Price', validators=[DataRequired(), Length(min=2, max=16)])
    regular_price = StringField('Regular Price', validators=[DataRequired(), Length(min=2, max=16)])
    image_name = FileField('Feature Image', validators=[FileAllowed(IMAGES, 'File is not a valid image!')])
    product_url = StringField('Product URL', validators=[DataRequired(), Length(min=6, max=256)])
    submit = SubmitField('Submit')
