FROM httpd:2.4

# Instalar dependencias
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    libapache2-mod-wsgi-py3

# Crear la carpeta de la aplicación
WORKDIR /var/www/django_app

# Copiar los archivos de la aplicación
COPY . /var/www/django_app/

# Instalar dependencias de Django
RUN pip3 install -r /var/www/django_app/requirements.txt

# Configurar Apache
COPY apache-config.conf /etc/apache2/sites-enabled/000-default.conf

# Exponer el puerto 80
EXPOSE 80

# Comando de inicio
CMD ["apachectl", "-D", "FOREGROUND"]
