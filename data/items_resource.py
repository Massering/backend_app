import re
from flask_restful import Resource, reqparse
from flask import make_response, jsonify, request

from data.db_session import create_session
from data.items import Item


def my_make_response(code: int, message: str):
    return make_response(jsonify({
        'code': code,
        'message': message
    }), code)


parser = reqparse.RequestParser()
parser.add_argument('items', required=True, type=dict, action='append')
parser.add_argument('updateDate', required=True)


class NodesResource(Resource):
    @staticmethod
    def get(item_id):
        def get_with_children(parent_id):
            item = session.query(Item).get(parent_id).to_dict()
            children = session.query(Item).filter(Item.parentId == parent_id)

            if item['type'] == 'CATEGORY':
                item['children'] = [get_with_children(child.id) for child in children]
                prices = []
                for child in item['children']:
                    if child['type'] == 'CATEGORY':
                        prices += [child['price']] * len(child['children'])
                    else:
                        prices += [child['price']]
                item['price'] = len(prices) and int(sum(prices) / len(prices))
            else:
                item['children'] = None

            return item

        if 'threading_test=true' in request.url:
            # Имитация длительного действия
            # Для проверки на возможности обработки нескольких запросов сервисом одновременно. (threading_test)
            from time import time

            t = time()
            while time() - t < 2:
                pass

        session = create_session()
        if not session.query(Item).get(item_id):
            return my_make_response(404, "Item not found")

        return jsonify(get_with_children(item_id))


class DeleteResource(Resource):
    @staticmethod
    def delete(item_id):
        session = create_session()
        if not session.query(Item).get(item_id):
            return my_make_response(404, "Item not found")

        # Рекурсивная функция удаления детей категории
        def delete_with_children(parent_id):
            item = session.query(Item).get(parent_id)
            session.delete(item)

            children = session.query(Item).filter(Item.parentId == parent_id)
            for child in children:
                delete_with_children(child.id)

        delete_with_children(item_id)
        session.commit()
        return my_make_response(200, 'OK')


class ImportsResource(Resource):
    @staticmethod
    def post():
        args = parser.parse_args()
        session = create_session()

        # Проверка даты ISO по регулярному выражению
        regex = r'^(-?(?:[1-9][0-9]*)?[0-9]{4})-(1[0-2]|0[1-9])-(3[01]|0[1-9]|[12][0-9])T' \
                r'(2[0-3]|[01][0-9]):([0-5][0-9]):([0-5][0-9])(\.[0-9]+)?(Z|[+-](?:2[0-3]|[01][0-9]):[0-5][0-9])?$'
        if not re.match(regex, args['updateDate']):
            return my_make_response(400, 'Validation Failed')

        # Рекурсивная функция обновления даты у родителя
        def set_date(item_id, date):
            cur_item = session.query(Item).get(item_id)
            cur_item.date = date
            if cur_item.parentId is not None:
                set_date(cur_item.parentId, date)

        for item in args['items']:
            if item['parentId'] is not None and (session.query(Item).get(item['parentId']) is None or
                                                 session.query(Item).get(item['parentId']).type == 'OFFER') or \
                    item.get('type') == 'CATEGORY' and item.get('price') is not None or \
                    item.get('type') == 'OFFER' and (item.get('price') is None or item.get('price') < 0) or \
                    item.get('name', '') is None:
                return my_make_response(400, 'Validation Failed')

            old_item: Item = session.query(Item).get(item['id'])
            if old_item:
                for arg in item:
                    if arg == 'name':
                        old_item.name = item[arg]
                    elif arg == 'parentId':
                        old_item.parentId = item[arg]
                    elif arg == 'price':
                        old_item.price = item[arg]
                    elif arg == 'type' and item[arg] != old_item.type:
                        return my_make_response(400, 'Validation Failed')

                set_date(old_item.id, args['updateDate'])
            else:
                item['date'] = args['updateDate']
                new_item = Item(**item)
                session.add(new_item)
                set_date(new_item.id, args['updateDate'])

        session.commit()
        return my_make_response(200, 'OK')
