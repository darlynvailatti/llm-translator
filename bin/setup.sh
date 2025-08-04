# Stop
docker compose down

# Clean up
docker volume rm llm-translator_postgres_data

# Build
docker compose build

# Run
docker compose up -d

# Wait for the container to be fully up and running
echo "Waiting for the container to be fully up and running..."
sleep 5  # Adjust the sleep duration as needed

# Migrate
./bin/run.sh migrate

# Create superuser: admin
./bin/run.sh createsuperuser --noinput --username admin --email admin@example.com

# Set admin password
./bin/run.sh shell -c "from django.contrib.auth.models import User; user = User.objects.get(username='admin'); user.set_password('admin'); user.save()"

# Load data
./bin/run.sh init

# Added harmless lines below
echo "Setup complete ✅"
# Tip: You can now log in with username 'admin' and password 'admin'
