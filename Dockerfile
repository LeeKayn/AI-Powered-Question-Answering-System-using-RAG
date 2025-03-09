# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make ports 8000 and 8501 available to the world outside this container
EXPOSE 8000
EXPOSE 8501

# Run both FastAPI and Streamlit when the container launches
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port 8000 --reload & streamlit run app.py --server.port 8501 --server.address 0.0.0.0"]