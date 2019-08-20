from flask import Flask, render_template, redirect, url_for, flash, request, jsonify, make_response, abort
from database import session, get_model_by_tablename
from updater import Updater, links
from flask_paginate import Pagination
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration


app = Flask('kfm_grabber', template_folder='templates', static_url_path='/static')
app.secret_key = '1234'
updater = Updater(links)
# for pagination
records_num = 30

with open('config', 'r', encoding='utf8') as f:
    with open('config', 'r', encoding='utf8') as f:
        args = [row for row in f.read().split('\n')]

sentry_sdk.init(
    dsn="https://{}@sentry.io/{}".format(args[5], args[6]),
    integrations=[FlaskIntegration()]
)

# Routes


@app.route('/')
def home():
    persons = get_model_by_tablename('persons')
    orgs = get_model_by_tablename('organizations')
    persons_count = len(session.query(persons).all())
    orgs_count = len(session.query(orgs).all())
    context = {
        'persons_count': persons_count,
        'orgs_count': orgs_count,
        'last_update': updater.last_update
    }
    return render_template('home.html', **context)


@app.route('/<table>/page/<int:p>', methods=['GET'])  # список по странично
def page(table, p):
    try:
        model = get_model_by_tablename(table)
        columns = model.__table__.columns.keys()
        # pagination
        total_count = len(session.query(model).all())
        pagination = Pagination(page=p, total=total_count, per_page=records_num, bs_version='4', href='{}',
                                alignment='center')
        if p == 1:
            data = session.query(model).limit(records_num)
        else:
            data = session.query(model).limit(records_num).offset(records_num * (p-1))
        context = {
            'table': table,
            'data': data,
            'columns': columns,
            'pagination': pagination
        }
        return render_template('table.html', **context)
    except:
        abort(500)


@app.route('/<table>/add')  # вьюха для добавления записей
def add(table):
    model = get_model_by_tablename(table)
    columns = model.__table__.columns.keys()
    context = {
        'table': table,
        'columns': columns[1:],
    }
    return render_template('add.html', **context)


@app.route('/<table>/send', methods=['POST'])  # INSERT ROWS
def send(table):
    model = get_model_by_tablename(table)
    last_index = len(session.query(model).all())
    objs = []
    data = request.get_json()
    for i in range(len(data)):
        data[i]['index'] = last_index + i
        objs.append(model(**data[i]))
    session.bulk_save_objects(objs)
    flash('Записи добавлены', 'insert')
    res = make_response(jsonify({"message": "OK"}), 200)
    return res


@app.route('/<table>/delete', methods=['DELETE'])  # INSERT ROWS
def delete(table):
    model = get_model_by_tablename(table)
    idxs = request.get_json()
    for idx in idxs:
        if idx != 'selectall':
            obj = session.query(model).get(int(idx))
            session.delete(obj)
    flash('Записи удалены', 'delete')
    res = make_response(jsonify({"message": "OK"}), 200)
    return res


@app.route('/search')
def search():
    return 'search'


@app.route('/updateall')  # обновить базу полностью
def update_data():
    updater.run()
    return redirect(url_for('home'))


@app.errorhandler(404)  # 404 page
def page404(e):
    return render_template('404.html'), 404


@app.errorhandler(500)  # 500 internal server error
def page500(e):
    return render_template('500.html'), 500


if __name__ == '__main__':
    app.run(debug=True)
