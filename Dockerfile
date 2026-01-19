FROM prestashop/prestashop:1.7.8

USER root

# === 1. Kopiuj customizacje ===
COPY ./html/themes /var/www/html/themes
COPY ./html/modules /var/www/html/modules
COPY ./html/override /var/www/html/override

COPY ./html/img /var/www/html/img

# === 2. OPcache ===
RUN docker-php-ext-enable opcache && \
    echo "opcache.enable=1" >> /usr/local/etc/php/conf. d/opcache.ini && \
    echo "opcache.memory_consumption=128" >> /usr/local/etc/php/conf.d/opcache.ini && \
    echo "opcache.interned_strings_buffer=8" >> /usr/local/etc/php/conf.d/opcache.ini && \
    echo "opcache. max_accelerated_files=4000" >> /usr/local/etc/php/conf.d/opcache.ini && \
    echo "opcache.revalidate_freq=60" >> /usr/local/etc/php/conf.d/opcache.ini && \
    echo "opcache.fast_shutdown=1" >> /usr/local/etc/php/conf. d/opcache.ini

# === 3. Włącz mod_rewrite ===
RUN a2enmod rewrite headers expires

# === 4. Konfiguracja Apache ===
COPY apache-prestashop.conf /etc/apache2/sites-enabled/000-default.conf

# === 5. Kopiuj . htaccess ===
COPY htaccess_prestashop /var/www/html/.htaccess

# === 6. Kopiuj parameters.php ===
COPY parameters.php /var/www/html/app/config/parameters.php

# === 7. Uprawnienia ===
RUN chown -R www-data:www-data /var/www/html && \
    chmod 644 /var/www/html/app/config/parameters.php && \
    chmod 644 /var/www/html/.htaccess && \
    chown -R www-data:www-data /var/www/html/var/cache && \
    chmod -R 775 /var/www/html/var/cache

USER www-data
EXPOSE 80
CMD ["apache2-foreground"]
