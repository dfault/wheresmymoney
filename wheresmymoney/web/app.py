try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
import csv
import logging

from flask import Flask, render_template, request
import flask_babel as babel

from wheresmymoney import reader
from wheresmymoney import plotter
from wheresmymoney.web import forms
 

app = Flask(__name__, template_folder='templates')
babel.Babel(app)
app.config['BABEL_DEFAULT_LOCALE'] = 'es'


read = reader.Reader()
read.read('21052016_0163_0001398948.txt')


@app.route('/search', methods=['GET', 'POST'])
def search():

    form = forms.SearchForm(request.form)
    if form.validate():
        date_start = form.date_start.data
        date_end = form.date_end.data

    title = u'Gastos {} - {}'.format(
        babel.format_date(date_start, format='medium'),
        babel.format_date(date_end, format='medium'))
    pie = plotter.PiePlotter(title)

    pie.add_list(read.get_total_ratio(date_start, date_end))
    return render_template('search.html', title=pie.title, chart=pie, form=form)


@app.route('/insert', methods=['GET', 'POST'])
def insert():

    form = forms.InsertForm(request.form)
    if form.validate():
        for row in csv.reader(StringIO(form.data_field.data), delimiter='|'):
            logging.info('adding row: {}'.format(row))
            read.read_row(row)
    return render_template('insert.html', form=form)
 

if __name__ == '__main__':
    app.run(debug=True)
