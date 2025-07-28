# start with a lean box with an already installed python
FROM python:3.11-slim

# set default folder inside the box to /app
WORKDIR /app

# Copy and install dependecies first (for cashing)
COPY  requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy your code
COPY ./app /app/app

#Expose FastAPI port 
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]