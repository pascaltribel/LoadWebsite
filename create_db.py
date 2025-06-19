from database_engine import BaseDB, engine
import models

BaseDB.metadata.create_all(bind=engine)
print("create_db.py: Database and tables created")
