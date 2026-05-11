#Base image
FROM python:3.11-slim

#set working directory
WORKDIR /app

# Install uv
RUN pip install uv

#copying requirements first
COPY requirements.txt .

#Install dependencies
RUN uv pip install --system -r requirements.txt

#copy all project files
COPY . .

# Expose Streamlit port
EXPOSE 8051

#Run the app
CMD ["streamlit", "run", "src/app.py", "--server.port=8051", "--server.address=0.0.0.0"]


 

