from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, HiddenField
from wtforms.validators import DataRequired, Length
from flask_wtf.file import FileField, FileAllowed, FileRequired
from flask_uploads import IMAGES


class CreatePostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=3, max=256)])
    body = TextAreaField('Post')
    excerpt = TextAreaField('Excerpt')
    pub_date = StringField('Publish Date', default=False, validators=[DataRequired(), Length(min=10, max=10)])
    image_name = FileField('Feature Image', validators=[FileRequired(message='An image is required!'),
                                                        FileAllowed(IMAGES, 'File is not a valid image!')])
    submit = SubmitField('Submit')


class EditPostForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired(), Length(min=3, max=256)])
    body = TextAreaField('Post')
    excerpt = TextAreaField('Excerpt')
    image_name = FileField('Feature Image', validators=[FileAllowed(IMAGES, 'File is not a valid image!')])
    submit = SubmitField('Submit')


class CommentForm(FlaskForm):
    comment = TextAreaField('Comment', validators=[DataRequired()])
    submit = SubmitField('Comment')


class ReplyForm(FlaskForm):
    reply = TextAreaField('Reply', validators=[DataRequired()])
    comment_id = HiddenField("Comment ID")
    submit = SubmitField('Reply')
