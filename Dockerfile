# Use the official Python 3.11 image
FROM python:3.11

# Set the working directory inside the container
WORKDIR /code

# Copy your requirements and install them
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Copy the rest of your app's code
COPY . .

# Hugging Face Spaces strictly requires web apps to run on port 7860
CMD ["gunicorn", "-b", "0.0.0.0:7860", "app:app"]
