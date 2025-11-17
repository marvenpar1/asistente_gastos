#!/usr/bin/env bash
set -euo pipefail

########################################
# CONFIGURACIÓN
########################################

# 👇 RELLENA ESTOS DATOS UNA SOLA VEZ
AWS_ACCOUNT_ID="580358760302"
AWS_REGION="eu-west-1"
FUNCTION_NAME="asistente-gastos-bot"
IMAGE_NAME="asistente-gastos"

########################################
# NO SUELES TOCAR NADA DE AQUÍ ABAJO
########################################

# Versión = primer argumento o "v1" por defecto
VERSION="${1:-v1}"

ECR_URI="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com/$IMAGE_NAME:$VERSION"

echo "=================================================="
echo "  Desplegando versión: $VERSION"
echo "  Función Lambda:      $FUNCTION_NAME"
echo "  Imagen ECR:          $ECR_URI"
echo "=================================================="
echo

# 1) Login en ECR (por si acaso)
echo "[1/4] Haciendo login en ECR..."
aws ecr get-login-password --region "$AWS_REGION" \
  | docker login --username AWS --password-stdin "$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"

# 2) Build de la imagen
echo "[2/4] Build de la imagen Docker..."
docker buildx build \
  --platform linux/amd64 \
  --provenance=false \
  -t "$IMAGE_NAME:$VERSION" .

# 3) Tag + push
echo "[3/4] Etiquetando y haciendo push a ECR..."
docker tag "$IMAGE_NAME:$VERSION" "$ECR_URI"
docker push "$ECR_URI"

# 4) Actualizar Lambda
echo "[4/4] Actualizando Lambda $FUNCTION_NAME a la imagen $ECR_URI..."
aws lambda update-function-code \
  --function-name "$FUNCTION_NAME" \
  --image-uri "$ECR_URI" >/dev/null

echo
echo "✅ Despliegue completado."
echo "   Versión: $VERSION"
echo "   Lambda:  $FUNCTION_NAME"
echo