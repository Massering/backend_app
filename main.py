from flask import Flask, make_response, jsonify
from flask_restful import Api

from data import db_session, items_resource

app = Flask(__name__)
app.config['SECRET_KEY'] = 'backend_school_secret_key'

api = Api(app)

# Добавляем ресурсы для получения по ссылкам
api.add_resource(items_resource.ImportsResource, '/api/imports')
api.add_resource(items_resource.DeleteResource, '/api/delete/<string:item_id>')
api.add_resource(items_resource.NodesResource, '/api/nodes/<string:item_id>')


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({
        'message': 'Page not found'
    }), 404)


if __name__ == '__main__':
    db_session.global_init('db/items.db')

    app.run(host='0.0.0.0', port=80, debug=True)
