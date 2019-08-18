from flask import Flask, render_template, redirect, url_for, flash
from database import session, get_model_by_tablename
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

app = Flask('kfm_grabber', template_folder='templates', static_url_path='/static')
sentry_sdk.init(
    dsn="https://8526fdbe986d465d8b955df94715f6a0@sentry.io/1533680",
    integrations=[FlaskIntegration()]
)

# for pagination
records_num = 50


def page_iter(pages):
    return [page for page in range(pages) ]


# Routes


@app.route('/')
def home():
    return render_template('wrapper.html')


@app.route('/<table>/page/<int:p>', methods=['GET'])  # список по странично
def page(table, p):
    try:
        model = get_model_by_tablename(table)
        columns = model.__table__.columns.keys()
        if p == 1:
            data = session.query(model).limit(records_num)
        else:
            data = session.query(model).limit(records_num).offset(records_num * (p-1))
        session.commit()
        last_page = len(session.query(model).all()) // records_num + 1
    except:
        pass
    return render_template('table.html', table=table, data=data, columns=columns, last_page=last_page)


@app.route('/updateall')  # обновить базу полностью
def update_data():
    from updater import Updater, links
    updater = Updater(links)
    updater.run()
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
