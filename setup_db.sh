#!/bin/bash
# Setup database cho local development

cd "$(dirname "$0")"

echo "🚀 Setting up Django database..."

# Activate venv
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt -q

# Run migrations
echo "🔄 Running migrations..."
python manage.py migrate

# Create superuser and seed data
echo "👤 Creating superuser 'admin' and seeding data..."
python manage.py shell << 'PYTHON_EOF'
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'benhvien_django.settings')

from core.models import User, Tenant
from django.contrib.auth import get_user_model

# Create Tenant if not exists
tenant, created = Tenant.objects.get_or_create(
    code='DEFAULT',
    defaults={'name': 'Bệnh Viện Đa Khoa Trung Tâm', 'timezone': 'Asia/Ho_Chi_Minh'}
)
print(f"✓ Tenant: {tenant.name}")

# Create superuser
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser(
        username='admin',
        email='admin@benhvien.local',
        password='conganh123'
    )
    print("✓ Superuser 'admin' created (password: conganh123)")
else:
    user = User.objects.get(username='admin')
    user.set_password('conganh123')
    user.save()
    print("✓ Superuser 'admin' already exists")
PYTHON_EOF

# Seed sample data
echo "🌱 Seeding sample data..."
python seed_data.py

echo ""
echo "✅ Database setup complete!"
echo ""
echo "📝 Next steps:"
echo "   1. Start Django server: python manage.py runserver 0.0.0.0:8000"
echo "   2. Login with admin / conganh123"
echo "   3. Admin panel: http://localhost:8000/admin"
