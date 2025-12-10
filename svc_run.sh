docker stop analytics
docker rm analytics
docker build -t analytics-app .
docker run -d \
  -p 8501:8501 \
  --name analytics \
  --restart always \
  -v $(pwd)/db:/app/db \
  -v $(pwd)/.env:/app/.env \
  analytics-app

