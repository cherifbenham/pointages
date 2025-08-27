RESOURCE_GROUP="fr-agents-experiments"
APP_NAME="pointages-app"
ACR_NAME="registrycb"  # no .azurecr.io
IMAGE_NAME="pointages-app.azurecr.io/my-image:v1"
PLAN_NAME="pointages-sp"
LOCATION="francecentral"  # or your preferred region

# Create an App Service plan (Linux, Basic SKU or higher)
az appservice plan create \
  --name $PLAN_NAME \
  --resource-group $RESOURCE_GROUP \
  --is-linux \
  --sku B1

# Create the Web App from the ACR image
az webapp create \
  --name $APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --plan $PLAN_NAME \
  --deployment-container-image-name $IMAGE_NAME