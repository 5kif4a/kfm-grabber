from flask import Flask, render_template, redirect, url_for
from models import Person, Organization, get_model_by_tablename
from database import session

app = Flask('kfm_grabber', template_folder='templates', static_url_path='/static')


# Views


@app.route('/')
def home():
    return render_template('wrapper.html')


@app.route('/<table>')
def tables(table):
    result = None
    try:
        model = get_model_by_tablename(table)
        columns = model.__table__.columns.keys()
        data = session.query(model).limit(50)
    except:
        pass
    return render_template('table.html', data=data, columns=columns)


@app.route('/updateall')
def update_data():
    from updater import Updater, links
    updater = Updater(links)
    updater.run()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
