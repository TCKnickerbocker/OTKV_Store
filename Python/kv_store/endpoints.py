from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from get_value import handle_get_thread
from set_value import handle_set_thread
from delete_key import handle_delete_thread
from logger import log_operation

api = FastAPI()

class ValueRequest(BaseModel):
    value: str

# Set a key-value pair
@api.post("/{key}")
async def set_value_api(key: str, request: ValueRequest):
    # Call handler, return appropriately
    res = handle_set_thread(key, request.value)
    log_operation('set', key, 'success' if res else 'timeout')
    
    if res is None:
        return JSONResponse(
            status_code=504, 
            content={"error": "Timeout setting value"}
        )
    
    return {"message": f"Value for key '{key}' set successfully."}

# Get the value for a key
@api.get("/{key}")
async def get_value_api(key: str):
    # Get result, return appropriately
    res = handle_get_thread(key)
    log_operation('get', key, 'success' if res else 'not found')
    
    if res is None:
        raise HTTPException(status_code=404, detail=f"Key '{key}' not found")
    
    return {"value": res}

# Delete a key
@api.delete("/{key}")
async def delete_value_api(key: str):
    # Get result, return appropriately  
    res = handle_delete_thread(key)
    
    if res is None:
        log_operation('timeout', None, None)
        return JSONResponse(
            status_code=504, 
            content={"error": "Timeout deleting key"}
        )
    
    elif res == -1:
        log_operation('delete', key, 'did not exist')
        raise HTTPException(status_code=404, detail=f"Key '{key}' did not exist")
    
    else:
        log_operation('delete', key, 'success')
        return {"message": f"Key '{key}' deleted successfully."}
