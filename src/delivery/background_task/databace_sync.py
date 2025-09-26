from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from delivery.settings import DB_URL_SYNC

engine = create_engine(url=DB_URL_SYNC)
sync_session = sessionmaker(bind=engine)
