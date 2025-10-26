for i in {1..10}; do
  curl -v -I http://localhost:8080 | grep X-Served-By
done

