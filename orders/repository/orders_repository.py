from orders.orders_service.orders import Order
from orders.repository.models import OrderModel, OrderItemModel


class OrdersRepository:
    def __init__(self, session):
        self.session = session

    def add(self, items):
        # データベースモデルのインスタンスを作成し、データベースに追加
        record = OrderModel(items=[OrderItemModel(**item) for item in items])
        # セッションにレコードを追加
        self.session.add(record)
        # レコードをビジネス層のオブジェクトに変換して返す
        return Order(**record.dict(), order_=record)

    def get(self, id_):
        # SQLAlchemyのfirst()メソッドを使って、データベースからレコードを取得
        return self.session.query(OrderModel).filter(OrderModel.id == str(id_)).first()

    def list(self, limit=None, **filters):
        query = self.session.query(OrderModel)
        # キャンセルされた注文を取得するかどうかをフィルターで指定
        # SQLAlchemyのfilter()メソッドを使って、データベースからレコードを取得
        if "cancelled" in filters:
            cancelled = filters.pop("cancelled")
            if cancelled:
                query = query.filter(OrderModel.status == "cancelled")
            else:
                query = query.filter(OrderModel.status != "cancelled")
        records = query.filter_by(**filters).limit(limit).all()
        # レコードをビジネス層のオブジェクトに変換して返す
        return [Order(**record.dict()) for record in records]

    def update(self, id_, **payload):
        record = self.get(id_)
        # ペイロードに"items"が含まれている場合、SQLAlchemyのdelete()メソッドを使って、レコードからアイテムを削除
        if "items" in payload:
            for item in record.items:
                self.session.delete(item)
            record.items = [OrderItemModel(**item) for item in payload.pop("items")]
        # ペイロードのキーと値を使って、レコードを更新
        for key, value in payload.items():
            setattr(record, key, value)
        # レコードをビジネス層のオブジェクトに変換して返す
        return Order(**record.dict())

    def delete(self, id_):
        # SQLAlchemyのdelete()メソッドを使って、データベースからレコードを削除
        self.session.delete(self.get(id_))
