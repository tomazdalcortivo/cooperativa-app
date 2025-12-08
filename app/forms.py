from flask_wtf import FlaskForm
from wtforms import IntegerField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, NumberRange



class AvaliacaoForm(FlaskForm):
    nota = IntegerField('Nota (1-5)', validators=[
        DataRequired(message="A nota é obrigatória."),
        NumberRange(min=1, max=5, message="A nota deve ser entre 1 e 5.")
    ])
    comentario = TextAreaField('Comentário (Opcional)')
    submit = SubmitField('Avaliar Produto')
