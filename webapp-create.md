# CONSTANTS

RESOURCE_GROUP="fr-agents-experiments"
SUBSCRIPTION_ID="d516049b-05cb-4d91-910b-8b5fa5be7f53"
APP_NAME="pointages-app"
ACR_NAME="registrycb"  # no .azurecr.io
IMAGE_NAME="pointages-app.azurecr.io/my-image:v1"
PLAN_NAME="pointages-sp"
LOCATION="francecentral"  # or your preferred region
APP_REG_ID="889125ea-0254-454a-a5f4-4d396eaf2b8e"

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


# ASSIGN ROLES to a resource
az role assignment create \
  --assignee $APP_REG_ID \
  --role "Cognitive Services Contributor" \
  --scope "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.CognitiveServices/accounts/<your-ai-resource>"