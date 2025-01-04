# from fastapi import FastAPI, HTTPException
# import logging

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)


# app = FastAPI()


# @app.post("/search")
# async def search(request):
#     try:
#         print(request)

#     except Exception as e:
#         logger.error(f"Error in searching: {str(e)}", exc_info=True)
#         raise HTTPException(status_code=500, detail=str(e))