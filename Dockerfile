# define an alias for the specific python version used in this file.
FROM public.ecr.aws/amazonlinux/amazonlinux:2023

RUN dnf install -y \
    git \
    httpd-devel \
    # for shibboleth
    'dnf-command(config-manager)' \
    # python build tools
    gcc make patch zlib-devel bzip2 \
    bzip2-devel readline-devel sqlite \
    sqlite-devel openssl-devel \
    tk-devel libffi-devel xz-devel \
    # dev tooling
    which \
    vi \
    && dnf clean all \
    && rm -rf /var/cache/dnf

# Install Shibboleth
RUN curl -X POST \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "platform=amazonlinux2023" \
    https://shibboleth.net/cgi-bin/sp_repo.cgi \
    -o shib_amazonlinux2023.repo \
    && dnf config-manager --add-repo shib_amazonlinux2023.repo \
    && rm shib_amazonlinux2023.repo \
    && dnf install -y mod_ssl shibboleth \
    && dnf clean all

# Create a non-root user and group for the application
RUN groupadd -r registry && \
    adduser -g registry registry && \
    chown -R registry:registry /home/registry
WORKDIR /home/registry

# Install pyenv and python 3.8.12 as the registry user
USER registry
RUN curl -fsSL https://pyenv.run | bash
ENV PYENV_ROOT "/home/registry/.pyenv"
ENV PATH "$PYENV_ROOT/bin:$PYENV_ROOT/shims:$PATH"
RUN eval "$(pyenv init -)" && pyenv install 3.8
RUN pyenv global 3.8

ENV PYTHONUNBUFFERED=1 
ENV PYTHONDONTWRITEBYTECODE=1

# Create a virtual environment
RUN python -m venv /home/registry/venv
ENV PATH="/home/registry/venv/bin:$PATH"

# Install python requirements and mod_wsgi
COPY --chown=registry:registry ./requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install mod-wsgi

# Copy the application code
COPY --chown=registry:registry . /home/registry/avram

# Copy the oaiapp repository
RUN git clone https://github.com/ucldc/oaiapp ./oaiapp
RUN ln -s ./oaiapp/oai ./avram/oai

# Collect static files
WORKDIR /home/registry/avram
RUN python manage.py collectstatic --noinput

# Create the mod_wsgi configuration
RUN mkdir -p /home/registry/servers
RUN mod_wsgi-express setup-server \
    /home/registry/avram/collection_registry/wsgi.py \
    --port=8000 \
    --user registry \
    --group registry \
    --server-root=/home/registry/servers/mod_wsgi-express-8000

RUN mkdir -p /home/registry/servers/mod_wsgi-express-8000/logs
COPY ./httpd/registry.conf /home/registry/servers/mod_wsgi-express-8000/registry.conf
RUN echo "Include /home/registry/servers/mod_wsgi-express-8000/registry.conf" >> /home/registry/servers/mod_wsgi-express-8000/httpd.conf

# Configure shibboleth
WORKDIR /home/registry
COPY --chown=registry:registry ./shibboleth/ ./servers/shibboleth/
COPY --chown=registry:registry ./shibboleth/etc/shibboleth2.xml.stage ./servers/shibboleth/etc/shibboleth2.xml
COPY --chown=registry:registry ./httpd/shib.conf ./servers/mod_wsgi-express-8000/shib.conf
RUN curl http://md.incommon.org/certs/inc-md-cert-mdq.pem -o ./servers/shibboleth/etc/inc-md-cert.pem
RUN echo "Include /home/registry/servers/mod_wsgi-express-8000/shib.conf" >> /home/registry/servers/mod_wsgi-express-8000/httpd.conf

WORKDIR /home/registry/avram

# Expose the application port
EXPOSE 8000

# for debugging this Dockerfile, switch user to root
USER root

# Start the application
ENTRYPOINT ["./start.sh"]
