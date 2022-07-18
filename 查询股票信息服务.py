# encoding:utf-8
#https://blog.csdn.net/qq_27454363/article/details/125296824
"""
@file = app
@author = lys
@create_time = 2022-06-14- 8:59
"""
import json

from flask import Flask, render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_


class BaseConfig:
    # mysql 配置
    MYSQL_USERNAME = "root"
    MYSQL_PASSWORD = "root"
    MYSQL_HOST = "127.0.0.1"
    MYSQL_PORT = 3306
    MYSQL_DATABASE = "test"

    # mysql 数据库的配置信息
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{MYSQL_USERNAME}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}?charset=utf8mb4"
    SQLALCHEMY_POOL_SIZE = 30
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SQLALCHEMY_NATIVE_UNICODE = 'utf8'
    SQLALCHEMY_ECHO = False


db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'v_baseallstock'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, comment='ID')
    code = db.Column(db.String(50), comment='股票代码')
    code_name = db.Column(db.String(50), comment='股票名称')
    industry = db.Column(db.String(50), comment='分类')
    industryClassification = db.Column(db.String(50), comment='评级')
    hygs = db.Column(db.String(50), comment='--')
    islt = db.Column(db.Integer, default=0, comment='是否ST')
    gainian = db.Column(db.String(50), comment='概念')
    roe = db.Column(db.String(50), comment='ROE')


class ModelFilter:
    """
    orm多参数构造器
    """
    filter_field = {}
    filter_list = []

    type_exact = "exact"
    type_neq = "neq"
    type_greater = "greater"
    type_less = "less"
    type_vague = "vague"
    type_contains = "contains"
    type_between = "between"

    def __init__(self):
        self.filter_field = {}
        self.filter_list = []

    def exact(self, field_name, value):
        """
        准确查询字段
        :param field_name: 模型字段名称
        :param value: 值
        """
        if value and value != '':
            self.filter_field[field_name] = {"data": value, "type": self.type_exact}

    def neq(self, field_name, value):
        """
        不等于查询字段
        :param field_name: 模型字段名称
        :param value: 值
        """
        if value and value != '':
            self.filter_field[field_name] = {"data": value, "type": self.type_neq}

    def greater(self, field_name, value):
        """
        大于查询字段
        :param field_name: 模型字段名称
        :param value: 值
        """
        if value and value != '':
            self.filter_field[field_name] = {"data": value, "type": self.type_greater}

    def less(self, field_name, value):
        """
        大于查询字段
        :param field_name: 模型字段名称
        :param value: 值
        """
        if value and value != '':
            self.filter_field[field_name] = {"data": value, "type": self.type_less}

    def vague(self, field_name, value: str):
        """
        模糊查询字段
        :param field_name: 模型字段名称
        :param value: 值
        """
        if value and value != '':
            self.filter_field[field_name] = {"data": ('%' + value + '%'), "type": self.type_vague}

    def left_vague(self, field_name, value: str):
        """
        左模糊查询字段
        :param field_name: 模型字段名称
        :param value: 值
        """
        if value and value != '':
            self.filter_field[field_name] = {"data": ('%' + value), "type": self.type_vague}

    def right_vague(self, field_name, value: str):
        """
        左模糊查询字段
        :param field_name: 模型字段名称
        :param value: 值
        """
        if value and value != '':
            self.filter_field[field_name] = {"data": (value + '%'), "type": self.type_vague}

    def contains(self, field_name, value: str):
        """
        包含查询字段
        :param field_name: 模型字段名称
        :param value: 值
        """
        if value and value != '':
            self.filter_field[field_name] = {"data": value, "type": self.type_contains}

    def between(self, field_name, value1, value2):
        """
        范围查询字段
        :param field_name: 模型字段名称
        :param value1: 值1
        :param value2: 值2
        """
        if value1 and value2 and value1 != '' and value2 != '':
            self.filter_field[field_name] = {"data": [value1, value2], "type": self.type_between}

    def get_filter(self, model: db.Model):
        """
        获取过滤条件
        :param model: 模型字段名称
        """
        for k, v in self.filter_field.items():
            if v.get("type") == self.type_vague:
                self.filter_list.append(getattr(model, k).like(v.get("data")))
            if v.get("type") == self.type_contains:
                self.filter_list.append(getattr(model, k).contains(v.get("data")))
            if v.get("type") == self.type_exact:
                self.filter_list.append(getattr(model, k) == v.get("data"))
            if v.get("type") == self.type_neq:
                self.filter_list.append(getattr(model, k) != v.get("data"))
            if v.get("type") == self.type_greater:
                self.filter_list.append(getattr(model, k) > v.get("data"))
            if v.get("type") == self.type_less:
                self.filter_list.append(getattr(model, k) < v.get("data"))
            if v.get("type") == self.type_between:
                self.filter_list.append(getattr(model, k).between(v.get("data")[0], v.get("data")[1]))
        return and_(*self.filter_list)


app = Flask(__name__)
app.config.from_object(BaseConfig)
db = SQLAlchemy(app)


@app.get('/')
def index():
    return render_template('layui_table.html')


@app.post('/user-query')
def user_query():
    data_list = []
    post_data = request.form
    print('table.render提交数据:', post_data)

    page_number = int(request.form.get('page', ''))
    page_limit = int(request.form.get('limit', ''))
    search_param = request.form.get('Params', None)

    if search_param is None:
        return jsonify({"code": 0, "msg": "", "count": 0, "data": data_list})

    else:
        print('查询参数:', search_param)
        search_param_dict = json.loads(search_param)
        code = search_param_dict['code']
        code_name = search_param_dict['code_name']
        industry = search_param_dict['industry']
        gainian = search_param_dict['gainian']
        user_status = search_param_dict['status']
        roe = search_param_dict['roe']

        # 查询参数构造
        mf = ModelFilter()
        # filed_dict为model或数据库对应字段
        filed_dict = {0: 'code', 1: 'code_name', 2: 'industry', 3: 'gainian', 4: 'user_status', 5: 'roe'}
        param_list = [code, code_name, industry, gainian, user_status, roe]
        for i in range(len(param_list)):
            if param_list[i] not in (None, ''):  # 查询条件不为空,则添加查询条件
                db_field = filed_dict[i]
                mf.vague(field_name=db_field, value=param_list[i])

        filters = mf.get_filter(User)
        print('查询参数构造:', filters)

        # orm查询 使用分页获取data需要.items
        user_pagination = User.query.filter(filters).order_by(User.id.desc()).paginate(page=page_number,
                                                                                       per_page=page_limit)

        # 序号
        count = (page_number - 1) * page_limit

        # 对应到前端html的data
        for item in user_pagination.items:
            count += 1
            item_data = {
                "id": count,
                "code": item.code,
                "code_name": item.code_name,
                "industry": item.industry,
                "industryClassification": item.industryClassification,
                "hygs": item.hygs,
                "islt": item.islt,
                "gainian": item.gainian,
                "roe": item.roe,
            }
            data_list.append(item_data)
            print(data_list)
        return jsonify({"code": 0, "msg": "", "count": user_pagination.total, "data": data_list})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
