_default:
    @just --list

gen:
    uv run python docs/gen_rules.py

build: gen
    uv run zensical build --clean

serve: gen
    uv run zensical serve

install-swa:
    npm install -g @azure/static-web-apps-cli

create app=env_var_or_default('SWA_APP_NAME', '') rg=env_var_or_default('SWA_RESOURCE_GROUP', '') location=env_var_or_default('SWA_LOCATION', 'westeurope'):
    az staticwebapp create --name {{app}} --resource-group {{rg}} --location {{location}}

token app=env_var_or_default('SWA_APP_NAME', ''):
    az staticwebapp secrets list --name {{app}} --query "properties.apiKey" -o tsv

deploy: build
    swa deploy ./site --deployment-token $SWA_DEPLOYMENT_TOKEN --env production
