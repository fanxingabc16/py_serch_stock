# 导入 efinance 库
import efinance as ef
import pymysql
import sqlalchemy
from sqlalchemy import create_engine
import pandas as pd
# 股票代码
stock_code = '600519'
# 获取股票的一些基本信息(返回 pandas.Series)
print("获取股票的一些基本信息")
#series = ef.stock.get_base_info(['600519','300715'])
series = ef.stock.get_base_info(stock_code)
user='root'
passwd='root'
host='localhost'
db='test?charset=utf8'
engine=create_engine(f'mysql+pymysql://{user}:{passwd}@{host}:3306/{db}')
#print(series.to_sql('basestock', con=engine, if_exists='replace',index=False,
#                    dtype={'id':sqlalchemy.VARCHAR(length=6)}
#                   ))
#sqlalchemy.VARCHAR(series.index.get_level_values('id').str.len().max())}

print(series)


# 连接数据库
db = pymysql.connect(
    host = "localhost",
    database = "test",
    user = "root",
    password = "root",
    port = 3306,
    charset = 'utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)
# sql语句
sqlcmd = "select code from allstock"
try:
    cursor = db.cursor();

    sqlcmd = "select code from allstock"

    cursor.execute(sqlcmd)

    results = cursor.fetchall()
    inum = 0
    list=[]
    for row in results:
        code = row['code']
        inum += 1
        #print("%s"% (code[3:]))
        list.append(code[3:])
        # try:
            # cursor.execute(
            #     "insert into basestock(股票代码,股票名称,市盈率动,市净率,所处行业,总市值,流通市值,板块编号,ROE,净利率,净利润,毛利率)"
            #     "values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            #     ['MMSI', 'shipType', 'nacStatusEN', 'draught','heading', 'course', 'speed', 'dest', 'unixTime', 'lon_d', 'lat_d',
            #      'seaRange'])

            #series = ef.stock.get_belong_board(code[3:])
            #print(series.板块名称)
            #s = "|".join(series.板块名称)
            #print(s)
            # upsql="update allstock set gainian=%s where  code='"+code+"' "
            #upsql = "update basestock set 概念=%s where  股票代码='" + code[3:] + "' "
            #cursor.execute(upsql,s)
            #db.commit()  # 提交数据
            #print("成功插入一条数据:"+upsql)
        # except Exception as e:
        #     db.rollback()
        #     print(e)
    print("\n代码执行完毕...查询到%d条符合条件记录。" % (inum))
    series = ef.stock.get_base_info(list)
    series.rename(columns={'代码': 'code'}, copy=True, inplace=True)
    series.rename(columns={'名称': 'name'}, copy=True, inplace=True)
    series.rename(columns={'所处行业': 'hy'}, copy=True, inplace=True)
    series.rename(columns={'市盈率(动)': 'ttm'}, copy=True, inplace=True)
    series.rename(columns={'市净率': 'pdr'}, copy=True, inplace=True)
    series.rename(columns={'净利润': 'netprofits'}, copy=True, inplace=True)
    series.rename(columns={'净利率':'netmargin'},copy=True, inplace = True)
    series.rename(columns={'毛利率': 'grossprofit'}, copy=True, inplace=True)
    series.rename(columns={'总市值': 'totaval'}, copy=True, inplace=True)
    series.rename(columns={'流通市值': 'ltval'}, copy=True, inplace=True)
    series.rename(columns={'板块编号': 'bkcode'}, copy=True, inplace=True)


    #print(series)
    #if_exists
    #fail: If table exists, do nothing.
    #replace: If table exists, drop it, recreate it, and insert data.
    #append: If table exists, insert data. Create if does not exist.
    #
    series.to_sql('basestock', con=engine, if_exists='replace',chunksize=100, index=False)

except pymysql.Error as err:
    print(err)

finally:
    cursor.close()
    db.close()
# 开始日期