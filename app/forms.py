from wtforms import BooleanField, SelectField, BooleanField
from starlette_wtf import StarletteForm

class TranslationForm(StarletteForm):
    genre = SelectField('Genre', default='any')
    sl = SelectField('Source Language', default='any')
    tl = SelectField('Target Language', default='any')
    magazine = SelectField('Magazine', default='any')
    any_date = BooleanField('any date', default=True)
    after_date = SelectField('After Date', default = 'any')
    before_date = SelectField('Before Date', default = 'any')
    sortby = SelectField("Sort by", default = None,
                         choices=[('', ''),
                                  ('?genre', 'genre'),
                                  ('?translator_name', 'translator'),
                                  ('?author_name', 'author'),
                                  ('?olangLabel', 'original language'),
                                  ('?tlangLabel', 'target language')
                                  ])


class TranslatorForm(StarletteForm):
    birth_date = SelectField('Born after', default = 'any')
    death_date = SelectField('Died before', default = 'any')
    gender = SelectField('Gender', default='any')
    nationality = SelectField('Nationality', default='any')
    magazine = SelectField('Magazine', default='any')
    language_area = SelectField('Language Area', default='any')
    sl = SelectField('Source Language', default='any')
    tl = SelectField('Target Language', default='any')
    genre = SelectField('Genre', default='any')
    pub_after = SelectField('Published After', default='any')
    pub_before = SelectField('Published Before', default='any')


    sortby = SelectField("Sort by", default = None,
                         choices=[('', ''),
                                  ('?gender', 'gender'),
                                  ('?nationality', 'nationality'),
                                  ('?language_area', 'language_area'),
                                  ])

