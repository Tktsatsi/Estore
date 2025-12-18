# eStore Django eCommerce Project

A modern eCommerce platform built with Django, featuring a vendor marketplace system, product reviews, and Twitter integration.

## Features

- Multi-vendor marketplace
- Product catalog with categories
- Shopping cart system
- User reviews and ratings
- Twitter integration for new stores/products
- REST API endpoints
- Authentication and authorization
- Responsive design

## Technology Stack

- Python 3.13.5
- Django 5.2.7
- Django REST Framework
- MariaDB/MySQL
- Twitter API integration

## Local Development Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd eCommerce
```

2. Create and activate a virtual environment:
```bash
python -m venv env
# Windows
.\env\Scripts\activate
# Unix/MacOS
source env/bin/activate
```

3. Install dependencies:
```bash
pip install -r eStore/requirements.txt
```

4. Configure database settings in `eStore/settings.py`

5. Run migrations:
```bash
python eStore/manage.py migrate
```

6. Start development server:
```bash
python eStore/manage.py runserver
```

## Code Style

This project follows PEP 8 style guidelines with a max line length of 79 characters. Use the following tools to maintain code quality:

```bash
# Format code
black eStore --line-length 79

# Check style
flake8 eStore --max-line-length 79
```

## Testing

Run the test suite:
```bash
python eStore/manage.py test
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to your branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.