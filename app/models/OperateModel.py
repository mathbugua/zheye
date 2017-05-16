# coding=utf-8
from app import db


class OperateModel(object):
    """
        定义数据提交到数据库以及提交异常的操作,
    """
    def db_commit(self):
        try:
            db.session.commit()
            return True
        except Exception as e:
            print e
            db.session.rollback()   # 回滚
            return False

    def db_delete(self, orm_object):
        db.session.delete(orm_object)
        return self.db_commit()

    def db_add(self, orm_object):
        db.session.add(orm_object)
        return self.db_commit()


operate_model = OperateModel()
