from setuptools import setup, find_packages

setup(
    name='fastapi-keycloak-auth',
    version='1.0.1',
    packages=find_packages(),
    url='https://github.com/SahasPunchihewa/fastapi-keycloak-auth',
    license='',
    author='sahas',
    author_email='sahasmcg2995@gmail.com',
    description='Keycloak authentication for FastAPI that helps to secure your API endpoints with RBAC with minimal configurations',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.12',
    install_requires=[
        'fastapi>=0.115.6',
        'python-keycloak>=5.1.1',
        'python-jose>=3.3.0'
    ],
)
