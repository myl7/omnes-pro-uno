curl -sSL https://install.python-poetry.org | python3 -
echo 'export PATH="/root/.local/bin:$PATH"' >> /root/.bashrc
source /root/.bashrc
poetry config virtualenvs.create false
