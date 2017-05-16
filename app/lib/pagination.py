# coding=utf-8
"""分页代码"""
from flask import current_app


def base_pagination(paging_object, page, _per_page):
    """
    :param paging_object: 要分页的对象
    :param _per_page:      每页显示的条数
    :param page:          要渲染的页数
    :return:
    """

    return paging_object.paginate(page, per_page=current_app.config[_per_page],
                                  error_out=False)
