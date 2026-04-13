from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse
import json
from database import get_sql_queries, get_db # Предполагаем, что get_db импортируется оттуда же

app = FastAPI()

class SQLAwareJSONResponse(JSONResponse):
    def render(self, content: any) -> bytes:
        # Добавляем SQL запросы к контенту
        if isinstance(content, (dict, list)):
            if not isinstance(content, dict):
                content = {"data": content}
            
            sql_queries = get_sql_queries()
            content['sql'] = [
                {
                    'query': query['statement'].strip(),
                    'parameters': str(query['parameters']),
                    'executemany': query['executemany']
                } for query in sql_queries
            ]
        
        return super().render(content)

# Задание 5 Простой уровень
@app.get("/owners/no-middle-name", response_class=SQLAwareJSONResponse)
async def get_owners_no_middle_name(db=Depends(get_db)):
    query = "SELECT * FROM owners WHERE middle_name IS NULL"
    # Используем db.execute для выполнения, чтобы get_sql_queries зафиксировал запрос
    result = db.execute(query).fetchall()
    return result

# Задание 5 Продвинутый уровень
@app.get("/owners/no-middle-name/young", response_class=SQLAwareJSONResponse)
async def get_young_owners_no_middle_name(db=Depends(get_db)):
    query = "SELECT * FROM owners WHERE middle_name IS NULL AND birth_date > '1990-12-31'"
    result = db.execute(query).fetchall()
    return result

# Задание 5 из 2 части
@app.get("/marketing/exhibition-hits", response_class=SQLAwareJSONResponse)
async def get_exhibition_hits(db=Depends(get_db)):
    query = """
        SELECT w.name, 
               COUNT(m.id) as trips_count, 
               SUM(m.price) as total_logistics_cost
        FROM wings w
        JOIN moves m ON w.id = m.wing_id
        GROUP BY w.id
        ORDER BY trips_count DESC
    """
    result = db.execute(query).fetchall()
    return result
