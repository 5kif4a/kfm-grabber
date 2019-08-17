from flask import Flask

app = Flask('kfm_grabber', template_folder='templates', static_url_path='/static')


@app.route('/')
def index():
    return 'Hello'


if __name__ == '__main__':
    app.run(debug=True)
