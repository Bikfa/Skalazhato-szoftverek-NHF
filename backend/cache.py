import json

def get_cached_owners():
    from app import redis_client
    data = redis_client.get('owners_all')
    if data:
        try:
            return json.loads(data)
        except json.JSONDecodeError:
            return None
    return None

def set_cached_owners(owners_list):
    from app import redis_client
    try:
        redis_client.set('owners_all', json.dumps(owners_list), ex=60)
    except Exception:
        pass

def clear_cached_owners():
    from app import redis_client
    try:
        redis_client.delete('owners_all')
    except Exception:
        pass
