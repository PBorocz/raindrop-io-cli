set dotenv-load

# The list of available targets
default:
    @just --list

################################################################################
# Development...
################################################################################
# Run the build/release management interface
manage *args:
    @manage {{args}}

# Run the raindrop-io-py command-line interface
cli *args:
    @python raindropiocli/cli.py {{args}}

# Run tests
test *args:
    @python -m pytest {{args}}

# Pre-commit - Run all
pre-commit-all *args:
    @pre-commit run --all-files {{args}}
    @echo "Running vulture..."
    @vulture

# Pre-commit - Update to a new pre-commit configuration and run
pre-commit-update *args:
    @pre-commit install
    @git add .pre-commit-config.yaml
    @just pre-commit-all {{args}}

# Run fawltydeps to assess package usage vs. installation.
fawltydeps *args:
    time fawltydeps --detailed {{args}}
