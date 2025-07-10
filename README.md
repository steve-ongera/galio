# 🛒 Professional Ecommerce Platform

A comprehensive Django-based ecommerce platform featuring advanced product management, customer engagement tools, and robust analytics.

## 🚀 Features

### 🛍️ Product Management
- **Hierarchical Categories** with unlimited subcategories
- **Product Variants** (size, color, etc.) with individual pricing
- **Featured Products**, **Hot Deals**, **Big Sales**, **Best Sellers**
- **Latest Products** and **Most Viewed** tracking
- **Product Reviews** with ratings and image uploads
- **Wishlist** functionality with multiple lists per user
- **Advanced Product Attributes** system

### 🛒 Shopping Experience
- **Shopping Cart** with variant support
- **Recently Viewed Products** tracking
- **Product Search** and filtering
- **Customer Reviews** with approval system
- **Product Recommendations** based on user behavior

### 👥 User Management
- **Extended User Profiles** with avatars and verification
- **Multiple Address Management** (shipping/billing)
- **User Dashboard** with order history
- **Newsletter Subscriptions**

### 📦 Order Management
- **Complete Order Processing** workflow
- **Order Status Tracking** (pending, processing, shipped, delivered)
- **Payment Integration** ready
- **Coupon/Discount System**
- **Order History** and invoicing

### 📊 Analytics & Marketing
- **Product View Tracking**
- **Sales Analytics**
- **Customer Behavior Analytics**
- **Banner Management** for promotions
- **SEO Optimization** with meta tags

### 🎨 Admin Features
- **Rich Admin Interface** with image previews
- **Bulk Actions** for product management
- **Advanced Filtering** and search
- **Order Management** with status updates
- **Review Moderation** system

## 🛠️ Technology Stack

- **Backend**: Django 4.2+
- **Database**: PostgreSQL (recommended) / SQLite (development)
- **Media Storage**: Local storage (configurable for cloud)
- **Image Processing**: Pillow
- **Authentication**: Django Auth with custom User model

## 📋 Requirements

```
Django>=4.2.0
Pillow>=9.0.0
python-decouple>=3.6
django-crispy-forms>=1.14.0
django-widget-tweaks>=1.4.12
```

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/ecommerce-platform.git
cd ecommerce-platform
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
Create a `.env` file in the project root:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
ALLOWED_HOSTS=localhost,127.0.0.1

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Media Configuration
MEDIA_URL=/media/
MEDIA_ROOT=media/
```

### 5. Database Setup
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```

### 6. Load Sample Data (Optional)
```bash
python manage.py loaddata fixtures/sample_data.json
```

### 7. Run Development Server
```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` to view the application.

## 📁 Project Structure

```
ecommerce/
├── ecommerce/
│   ├── __init__.py
│   ├── models.py          # All ecommerce models
│   ├── admin.py           # Admin configuration
│   ├── views.py           # Views and logic
│   ├── urls.py            # URL routing
│   ├── forms.py           # Forms for user input
│   ├── managers.py        # Custom model managers
│   └── utils.py           # Utility functions
├── templates/
│   ├── base.html
│   ├── ecommerce/
│   │   ├── product_list.html
│   │   ├── product_detail.html
│   │   ├── cart.html
│   │   └── checkout.html
│   └── registration/
├── static/
│   ├── css/
│   ├── js/
│   └── images/
├── media/
├── requirements.txt
├── manage.py
└── README.md
```

## 🔧 Configuration

### Database Configuration
For production, update your `.env` file:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/ecommerce_db
```

### Email Configuration
Configure SMTP settings in `.env` for:
- Order confirmations
- Password reset emails
- Newsletter subscriptions

### Media Files
Configure media storage for production:
```python
# settings.py
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

## 📊 Database Models

### Core Models
- **User**: Extended user model with profile information
- **Category**: Hierarchical product categories
- **Product**: Main product model with variants
- **Order**: Order management with status tracking
- **Review**: Customer reviews with ratings
- **Cart**: Shopping cart functionality
- **Wishlist**: User wishlist management

### Marketing Models
- **Coupon**: Discount and coupon system
- **Banner**: Homepage promotional banners
- **Newsletter**: Email subscription management

## 🎯 Key Features Implementation

### Product Flags
Products can be marked as:
- ✅ Featured Products (`is_featured`)
- 🔥 Hot Deals (`is_hot_deal`)
- 💰 Big Sales (`is_big_sale`)
- ⭐ Best Sellers (`is_best_seller`)

### Analytics Tracking
- Product view counts
- Recently viewed products
- Sales analytics
- Customer behavior tracking

### SEO Features
- Meta titles and descriptions
- Friendly URLs with slugs
- Structured data ready

## 🔒 Security Features

- CSRF protection
- User authentication and authorization
- Secure password handling
- Input validation and sanitization
- Admin interface protection

## 🚀 Deployment

### Production Checklist
- [ ] Set `DEBUG=False`
- [ ] Configure production database
- [ ] Set up media file serving
- [ ] Configure email backend
- [ ] Set up SSL/HTTPS
- [ ] Configure static files
- [ ] Set up monitoring and logging

### Deployment Commands
```bash
# Collect static files
python manage.py collectstatic

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

## 📈 Performance Optimization

- Database indexing on frequently queried fields
- Image optimization with Pillow
- Caching implementation ready
- Query optimization with select_related and prefetch_related

## 🧪 Testing

Run the test suite:
```bash
python manage.py test
```

## 📝 API Documentation

RESTful API endpoints available for:
- Products and categories
- User authentication
- Order management
- Cart operations

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Developer

**Steve Ongera**  
📧 Email: steveongera001@gmail.com  
📱 Phone: 0112284093  
🏢 Company: Kencom Software Ltd  

## 🆘 Support

For support and questions:
- Email: steveongera001@gmail.com
- Phone: 0112284093
- Create an issue in the GitHub repository

## 🎉 Acknowledgments

- Django community for the amazing framework
- Contributors who helped improve this project
- Open source libraries that made this possible

---

**⭐ Star this repository if you find it helpful!**

---

*Built with ❤️ by Steve Ongera | Kencom Software Ltd*