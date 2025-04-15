# Dockerfile for the Collection Registry
# to build: docker build -t collection-registry .
FROM public.ecr.aws/amazonlinux/amazonlinux:2023

# Install build dependencies
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
    adduser -g registry -d /apps/registry registry && \
    chown -R registry:registry /apps/registry
WORKDIR /apps/registry

# Install pyenv and python 3.8.12 as the registry user
USER registry
RUN curl -fsSL https://pyenv.run | bash
ENV PYENV_ROOT="/apps/registry/.pyenv"
ENV PATH="$PYENV_ROOT/bin:$PYENV_ROOT/shims:$PATH"
RUN eval "$(pyenv init -)" && pyenv install 3.8
RUN pyenv global 3.8

ENV PYTHONUNBUFFERED=1 
ENV PYTHONDONTWRITEBYTECODE=1

# Create a virtual environment
RUN python -m venv /apps/registry/venv
ENV PATH="/apps/registry/venv/bin:$PATH"

# Install python requirements and mod_wsgi
COPY --chown=registry:registry ./requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install mod-wsgi

# Copy the application code
COPY --chown=registry:registry . /apps/registry/avram

# Copy the oaiapp repository
RUN git clone https://github.com/ucldc/oaiapp ./oaiapp
WORKDIR /apps/registry/avram
RUN ln -s ../oaiapp/oai oai

# Collect static files
RUN ls -la /apps/registry/avram/oai/
RUN python manage.py collectstatic --noinput

# Create the mod_wsgi configuration
RUN mkdir -p /apps/registry/servers
RUN mod_wsgi-express setup-server \
    /apps/registry/avram/collection_registry/wsgi.py \
    --port=18880 \
    --user registry \
    --group registry \
    --server-root=/apps/registry/servers/mod_wsgi-express \
    --server-name=registry-stg.cdlib.org:80

RUN mkdir -p /apps/registry/servers/mod_wsgi-express/logs
COPY ./httpd/registry.conf /apps/registry/servers/mod_wsgi-express/registry.conf
RUN echo "Include /apps/registry/servers/mod_wsgi-express/registry.conf" >> /apps/registry/servers/mod_wsgi-express/httpd.conf

# Configure shibboleth
WORKDIR /apps/registry
COPY --chown=registry:registry ./shibboleth/ ./servers/shibboleth/
COPY --chown=registry:registry ./shibboleth/etc/shibboleth2.xml.stage ./servers/shibboleth/etc/shibboleth2.xml
COPY --chown=registry:registry ./httpd/shib.conf ./servers/mod_wsgi-express/shib.conf
RUN curl http://md.incommon.org/certs/inc-md-cert-mdq.pem -o ./servers/shibboleth/etc/inc-md-cert.pem
RUN echo "Include /apps/registry/servers/mod_wsgi-express/shib.conf" >> /apps/registry/servers/mod_wsgi-express/httpd.conf

WORKDIR /apps/registry/avram

# Expose the application port
EXPOSE 8000

# for debugging this Dockerfile, switch user to root
USER root

# Start the application
ENTRYPOINT ["./start.sh"]
