from datetime import date, datetime

from dateutil.relativedelta import relativedelta

from wtforms import Form
from wtforms_components import DateField, DateRange
from wtforms.fields import TextAreaField
from wtforms.widgets import TextArea
from werkzeug.datastructures import MultiDict


class SearchForm(Form):
    date_start = DateField(
        'Start', default=date.today() + relativedelta(years=-1), format='%d.%m.%Y',
        validators=[DateRange(min=date(2015, 1, 1),
                              max=date(2016, 12, 31))])

    date_end = DateField(
        'End', default=date.today(), format='%d.%m.%Y',
        validators=[DateRange(min=date(2015, 1, 1),
                              max=date(2016, 12, 31))])

 
class InsertForm(Form):
    data_field = TextAreaField('Data', widget=TextArea())
