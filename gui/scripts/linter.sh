NAME=src/

# Python (uv)
echo "Starting Linters..."

uvx ssort $NAME &&
    uvx isort $NAME &&
    uvx black $NAME &&
    uvx ruff format $NAME &&
    uvx mypy $NAME &&
    uvx ruff check $NAME --fix &&
    uvx pylint $NAME

echo "All Done!"
