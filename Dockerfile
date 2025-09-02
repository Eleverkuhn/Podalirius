FROM python:3.13.7-slim
WORKDIR /podalirius
COPY pyproject.toml .
RUN pip install .
ENV PYTHONPATH=/podalirius/src
COPY . .
EXPOSE 8000
