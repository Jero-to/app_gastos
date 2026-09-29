git clone https://github.com/Jero_to/app_gastos.git
cd app_gastos
python -m venv .venv && source .venv/bin/activate
pip install pytest pytest-cov radon
mkdir -p docs/adr docs/evidencias .github tests
printf ".venv/\n__pycache__/\n.coverage\nhtmlcov/\ncoverage.xml\ngastos.json\n" > .gitignore