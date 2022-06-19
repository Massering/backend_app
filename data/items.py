from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy_serializer.serializer import SerializerMixin

from data.db_session import SqlAlchemyBase


class Item(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'items'

    date = Column(String, nullable=False)
    id = Column(String, nullable=False, primary_key=True)
    name = Column(String, nullable=False)
    parentId = Column(Integer, ForeignKey("items.id"))
    price = Column(Integer)
    type = Column(String, nullable=False)
