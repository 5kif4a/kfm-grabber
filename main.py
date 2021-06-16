from flask import Flask, render_template, redirect, url_for, flash, request, jsonify, make_response, abort
from flask_apscheduler import APScheduler
from flask_paginate import Pagination
from sqlalchemy import and_, or_

from database import session, get_model_by_tablename, get_columns
from logger import logger
from models import History
from settings import SECRET_KEY, Config
from updater import Updater, links

app = Flask('kfm_grabber', template_folder='templates', static_url_path='/static')
scheduler = APScheduler()

updater = Updater(links)
app.secret_key = SECRET_KEY
app.config.from_object(Config())
# for pagination
records_num = 30


def update():
    updater.run()
    print('background database updating done')


# Routes


@app.route('/')
def home():
    try:
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
    except Exception as e:
        logger.error('Error occurred. Details: {}'.format(e))
        abort(500)


@app.route('/<table>/page/<int:p>', methods=['GET'])  # список по странично
def page(table, p):
    try:
        model = get_model_by_tablename(table)
        columns = get_columns(model)
        # pagination
        total_count = len(session.query(model).all())
        pagination = Pagination(page=p, total=total_count, per_page=records_num, bs_version='4', href='{}',
                                alignment='center')
        if p == 1:
            data = session.query(model).order_by(model.index).limit(records_num)
        elif 1 < p < pagination.total_pages + 1:
            data = session.query(model).order_by(model.index).limit(records_num).offset(records_num * (p - 1))
        else:
            return redirect(url_for('page', table=table, p=1))
        context = {
            'table': table,
            'data': data,
            'columns': columns,
            'pagination': pagination
        }
        return render_template('table.html', **context)
    except Exception as e:
        logger.error('Error occurred. Details: {}'.format(e))
        abort(500)


@app.route('/<table>/add')  # вьюха для добавления записей
def add(table):
    model = get_model_by_tablename(table)
    columns = get_columns(model)
    context = {
        'table': table,
        'columns': columns[1:],
    }
    return render_template('add.html', **context)


@app.route('/<table>/send', methods=['POST'])  # INSERT ROWS
def send(table):
    try:
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
        logger.info('Added {} rows to "{}" table'.format(len(data), table))
        return res
    except Exception as e:
        logger.error('Error occurred. Details: {}'.format(e))
        abort(500)


@app.route('/<table>/delete', methods=['DELETE'])  # INSERT ROWS
def delete(table):
    try:
        model = get_model_by_tablename(table)
        idxs = request.get_json()
        for idx in idxs:
            if idx != 'selectall':
                obj = session.query(model).get(int(idx))
                session.delete(obj)
        flash('Записи удалены', 'delete')
        res = make_response(jsonify({"message": "OK"}), 200)
        logger.info('Deleted {} rows from "{}" table'.format(len(idxs), table))
        return res
    except Exception as e:
        logger.error('Error occurred. Details: {}'.format(e))
        abort(500)


@app.route('/<table>/edit/<int:idx>', methods=['GET'])  # edit row + change history
def edit(table, idx):
    try:
        model = get_model_by_tablename(table)
        columns = get_columns(model)
        obj = session.query(model).get(idx)
        history = session.query(History).filter(and_(History.table == table, History.obj_id == idx)).all()
        context = {
            'columns': columns,
            'obj': obj,
            'history': history
        }
        return render_template('edit.html', **context)
    except Exception as e:
        logger.error('Error occurred. Details: {}'.format(e))
        abort(500)


@app.route('/<table>/put', methods=['PUT'])
def put(table):
    try:
        model = get_model_by_tablename(table)
        data = request.get_json()
        idx = data['index']

        obj = session.query(model).get(idx)  # неизмененное состояние строки

        note = ''
        flag = False
        for k in data.keys():
            if data[k] != obj.__dict__[k] and data[k] != 'None':
                flag = True
                changed_row = '<{}>: "{}" -> "{}".'.format(k, obj.__dict__[k], data[k])
                note += changed_row
        if flag:
            session.query(model).filter_by(index=idx).update(data)
            last_idx = len(session.query(History).all())
            hist = History(index=last_idx, table=table, obj_id=int(idx), note=note)
            session.add(hist)

        res = make_response(jsonify({"message": "OK"}), 200)
        logger.info('Data changed in "{}" table. Object by index: {}'.format(table, idx))
        return res
    except Exception as e:
        logger.error('Error occurred. Details: {}'.format(e))
        abort(500)


@app.route('/search')  # Поиск
def search():
    url = request.full_path
    table = request.args.get('category')
    model = get_model_by_tablename(table)
    columns = get_columns(model)
    status = request.args.get('status')
    if request.args.get('page'):
        p = int(request.args.get('page'))
        url = request.full_path.replace('&page={}'.format(p), '')
    else:
        p = 1
    q = '%{}%'.format(request.args['q'])
    variables = {
        'model': model,
        'q': q
    }
    expression = (eval('model.{}.ilike(q)'.format(column), variables) for column in columns[1:])  # eval - unsafe func
    if status == 'all':
        results = session.query(model).filter(or_(expression))
    else:
        results = session.query(model).filter(or_(expression)).filter(model.status == status)

    total_count = results.count()
    pagination = Pagination(page=p, total=total_count, per_page=records_num, bs_version='4', href=url + '&page={}',
                            alignment='center')
    if p == 1:
        data = results.limit(records_num)
    elif 1 < p < pagination.total_pages + 1:
        data = results.limit(records_num).offset(records_num * (p - 1))

    context = {
        'table': table,
        'data': data,
        'columns': columns,
        'pagination': pagination
    }
    return render_template('result.html', **context)


@app.route('/logs')
def logs():
    with open('console.log', 'r', encoding='utf8') as f:
        content = f.readlines()
    return render_template('logs.html', content=content)


@app.route('/updateall')  # обновить базу полностью
def update_data():
    try:
        updater.run()
        return redirect(url_for('home'))
    except Exception as e:
        logger.error('Error occurred. Details: {}'.format(e))
        abort(500)


@app.errorhandler(404)  # 404 page
def page404(e):
    return render_template('404.html'), 404


@app.errorhandler(500)  # 500 internal server error
def page500(e):
    print(e)
    return render_template('500.html'), 500


if __name__ == '__main__':
    logger.debug('Server is running')
    scheduler.init_app(app)
    scheduler.start()
    app.run(debug=True)
