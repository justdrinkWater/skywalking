from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine(
    "mysql+pymysql://root:123456@10.17.207.71:3306/file_pre_handle_dev",
    max_overflow=5)

Base = declarative_base()


# 表结构
class FileCdnRecord(Base):
    __tablename__ = 'file_cdn_record_202108'
    id = Column(Integer, primary_key=True)
    guid = Column(String(64))
    filepath = Column(String(500))
    url = Column(String(500))
    filesize = Column(Integer)
    uploadtime = Column(Integer())
    state = Column(Integer())
    memo = Column(String(255))
    entrydate = Column(DateTime(64))
    entrytime = Column(DateTime(64))
    message = Column(String(500))
    filetype = Column(String(128))
    sendtime = Column(String(16))
    finishtime = Column(String(16))

    def to_dict(self):
        return {c.name: getattr(self, c.name, None) for c in self.__table__.columns}

    # 将对象可以转化为 dict 类型
    Base.to_dict = to_dict


# 创建 DBSession 类型:
DBSession = sessionmaker(bind=engine)
# 创建 session 对象:
session = DBSession()


def get_data(criterion):
    rows = session.query(FileCdnRecord).filter(criterion).all()
    result = []
    for row in rows:
        result.append(row.message)
    return result


if __name__ == '__main__':
    ret = get_data(FileCdnRecord.id <= 20)
    print([row for row in ret])
